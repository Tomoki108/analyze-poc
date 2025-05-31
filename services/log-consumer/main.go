package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/gocql/gocql"
	"github.com/segmentio/kafka-go"
)

type OrderLog struct {
	UserID    string    `json:"user_id"`
	Timestamp time.Time `json:"timestamp"`
	MenuType  string    `json:"menu_type"` // "washoku" or "yoshoku"
}

func main() {
	// Kafka設定
	brokers := os.Getenv("KAFKA_BROKERS")
	if brokers == "" {
		brokers = "localhost:9092"
	}

	// Cassandra設定
	cassandraHosts := os.Getenv("CASSANDRA_HOSTS")
	if cassandraHosts == "" {
		cassandraHosts = "localhost"
	}

	// Kafka Reader作成
	reader := kafka.NewReader(kafka.ReaderConfig{
		Brokers:  strings.Split(brokers, ","),
		Topic:    "order-logs",
		GroupID:  "log-consumer-group",
		MinBytes: 10e3, // 10KB
		MaxBytes: 10e6, // 10MB
	})
	defer reader.Close()

	// Cassandraセッション作成
	cluster := gocql.NewCluster(strings.Split(cassandraHosts, ",")...)
	cluster.Keyspace = "analyze_poc"
	cluster.Consistency = gocql.Quorum
	session, err := cluster.CreateSession()
	if err != nil {
		log.Fatalf("Failed to create Cassandra session: %v", err)
	}
	defer session.Close()

	// メッセージ処理ループ
	for {
		msg, err := reader.ReadMessage(context.Background())
		if err != nil {
			log.Printf("Failed to read message: %v", err)
			continue
		}

		// メッセージパース
		parts := strings.Split(string(msg.Value), ",")
		if len(parts) != 3 {
			log.Printf("Invalid message format: %s", string(msg.Value))
			continue
		}

		timestamp, err := time.Parse(time.RFC3339, parts[1])
		if err != nil {
			log.Printf("Invalid timestamp format: %v", err)
			continue
		}

		order := OrderLog{
			UserID:    parts[0],
			Timestamp: timestamp,
			MenuType:  parts[2],
		}

		// Cassandraに書き込み
		if err := processOrder(session, order); err != nil {
			log.Printf("Failed to process order: %v", err)
		}
	}
}

func processOrder(session *gocql.Session, order OrderLog) error {
	// raw_ordersへの挿入 (order_dateを追加)
	if err := session.Query(
		`INSERT INTO raw_orders (user_id, ts, order_date, menu_type) VALUES (?, ?, ?, ?)`,
		order.UserID, order.Timestamp, order.Timestamp.UTC().Truncate(24*time.Hour), order.MenuType,
	).Exec(); err != nil {
		return fmt.Errorf("failed to insert raw order: %w", err)
	}

	// user_order_counts更新
	var counterColumn string
	switch order.MenuType {
	case "washoku":
		counterColumn = "washoku_cnt"
	case "yoshoku":
		counterColumn = "yoshoku_cnt"
	default:
		return fmt.Errorf("invalid menu_type: %s", order.MenuType)
	}

	if err := session.Query(
		fmt.Sprintf(`UPDATE user_order_counts SET %s = %s + 1 WHERE user_id = ?`, counterColumn, counterColumn),
		order.UserID,
	).Exec(); err != nil {
		return fmt.Errorf("failed to update user order counts: %w", err)
	}
	return nil
}
