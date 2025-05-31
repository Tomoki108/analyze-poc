package main

import (
	"net/http"
	"time"

	"github.com/gocql/gocql"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

type UserSegment struct {
	MenuType string   `json:"menu_type"`
	Count    int64    `json:"count"`
	UserIDs  []string `json:"user_ids"`
}

type DailyOrderSummary struct {
	Date   string `json:"date"`
	Counts []struct {
		MenuType string `json:"menu_type"`
		Count    int    `json:"count"`
	} `json:"counts"`
}

var session *gocql.Session

func main() {
	// Initialize Echo
	e := echo.New()
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	// Cassandra cluster configuration
	cluster := gocql.NewCluster("cassandra")
	cluster.Keyspace = "analyze_poc"
	cluster.Consistency = gocql.Quorum
	cluster.Timeout = 10 * time.Second

	// Create Cassandra session
	session, err := cluster.CreateSession()
	if err != nil {
		e.Logger.Fatal("Failed to connect to Cassandra:", err)
	}
	defer session.Close()

	// API routes
	e.GET("/api/user_segments", getUserSegments)
	e.GET("/api/daily_order_summaries", getDailyOrderSummaries)

	// Start server
	e.Logger.Fatal(e.Start(":8081"))
}

func getUserSegments(c echo.Context) error {
	var segments []UserSegment

	// Get washoku segment
	washokuIter := session.Query(`SELECT user_id FROM user_preferences WHERE preference = 'washoku'`).Iter()
	var washokuUsers []string
	var userID string
	for washokuIter.Scan(&userID) {
		washokuUsers = append(washokuUsers, userID)
	}
	if err := washokuIter.Close(); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	// Get yoshoku segment
	yoshokuIter := session.Query(`SELECT user_id FROM user_preferences WHERE preference = 'yoshoku'`).Iter()
	var yoshokuUsers []string
	for yoshokuIter.Scan(&userID) {
		yoshokuUsers = append(yoshokuUsers, userID)
	}
	if err := yoshokuIter.Close(); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	segments = append(segments,
		UserSegment{
			MenuType: "washoku",
			Count:    int64(len(washokuUsers)),
			UserIDs:  washokuUsers,
		},
		UserSegment{
			MenuType: "yoshoku",
			Count:    int64(len(yoshokuUsers)),
			UserIDs:  yoshokuUsers,
		},
	)

	return c.JSON(http.StatusOK, map[string]interface{}{"segments": segments})
}

func getDailyOrderSummaries(c echo.Context) error {
	yearMonth := c.QueryParam("year_month")
	var summaries []DailyOrderSummary

	// Get daily summaries filtered by year_month if provided
	query := `SELECT order_date, menu_type, count FROM daily_order_summaries`
	if yearMonth != "" {
		query += ` WHERE order_date >= ? AND order_date < ?`
	}
	iter := session.Query(query).Iter()
	var date time.Time
	var menuType string
	var count int
	for iter.Scan(&date, &menuType, &count) {
		// Find or create summary for this date
		var summary *DailyOrderSummary
		for i := range summaries {
			if summaries[i].Date == date.Format("2006-01-02") {
				summary = &summaries[i]
				break
			}
		}
		if summary == nil {
			summaries = append(summaries, DailyOrderSummary{
				Date: date.Format("2006-01-02"),
			})
			summary = &summaries[len(summaries)-1]
		}
		summary.Counts = append(summary.Counts, struct {
			MenuType string `json:"menu_type"`
			Count    int    `json:"count"`
		}{
			MenuType: menuType,
			Count:    count,
		})
	}
	if err := iter.Close(); err != nil {
		return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
	}

	return c.JSON(http.StatusOK, map[string]interface{}{"summaries": summaries})
}
