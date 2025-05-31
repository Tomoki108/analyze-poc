package main

import (
	"net/http"
	"time"

	"github.com/gocql/gocql"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

type CuisineSegment struct {
	Segment string   `json:"segment"`
	Count   int64    `json:"count"`
	Users   []string `json:"users"`
}

type DailySummary struct {
	Date       string `json:"date"`
	Segment    string `json:"segment"`
	TotalCount int    `json:"total_count"`
}

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
	e.GET("/api/segments", func(c echo.Context) error {
		var segments []CuisineSegment

		// Get segment counts
		iter := session.Query(`SELECT segment, cnt FROM cuisine_segment_counts`).Iter()
		var segment string
		var count int64
		for iter.Scan(&segment, &count) {
			// Get users for each segment from user_cuisine_counts
			var users []string
			userIter := session.Query(`SELECT user_id FROM user_cuisine_counts WHERE ` + segment + `_cnt > 0`).Iter()
			var userID string
			for userIter.Scan(&userID) {
				users = append(users, userID)
			}
			if err := userIter.Close(); err != nil {
				return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
			}

			segments = append(segments, CuisineSegment{
				Segment: segment,
				Count:   count,
				Users:   users,
			})
		}
		if err := iter.Close(); err != nil {
			return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
		}

		return c.JSON(http.StatusOK, map[string]interface{}{"cuisines": segments})
	})

	e.GET("/api/summaries", func(c echo.Context) error {
		var summaries []DailySummary

		// Get daily summaries
		iter := session.Query(`SELECT order_date, segment, cnt FROM daily_cuisine_summary`).Iter()
		var date time.Time
		var segment string
		var count int
		for iter.Scan(&date, &segment, &count) {
			summaries = append(summaries, DailySummary{
				Date:       date.Format("2006-01-02"),
				Segment:    segment,
				TotalCount: count,
			})
		}
		if err := iter.Close(); err != nil {
			return c.JSON(http.StatusInternalServerError, map[string]string{"error": err.Error()})
		}

		return c.JSON(http.StatusOK, map[string]interface{}{"summaries": summaries})
	})

	// Start server
	e.Logger.Fatal(e.Start(":8081"))
}
