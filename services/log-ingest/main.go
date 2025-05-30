package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/segmentio/kafka-go"
)

type VisitLog struct {
	UserID    string    `json:"user_id"`
	Timestamp time.Time `json:"timestamp"`
	MenuType  string    `json:"menu_type"`
}

func main() {
	// ブローカーは環境変数 KAFKA_BROKERS（例: "localhost:9092"）で指定、未指定時はローカルを使う
	brokers := os.Getenv("KAFKA_BROKERS")
	if brokers == "" {
		brokers = "localhost:9092"
	}
	// 注文ログ用ライターを作成
	writer := kafka.NewWriter(kafka.WriterConfig{
		Brokers: []string{brokers},
		Topic:   "order-logs",
	})
	defer writer.Close()

	e := echo.New()
	// 注文ログ用エンドポイント
	e.POST("/api/log", func(c echo.Context) error {
		var v VisitLog
		if err := c.Bind(&v); err != nil {
			return c.JSON(http.StatusBadRequest, map[string]string{"error": err.Error()})
		}
		msg := kafka.Message{
			Key:   []byte(v.UserID),
			Value: []byte(fmt.Sprintf("%s,%s,%s", v.UserID, v.Timestamp.Format(time.RFC3339), v.MenuType)),
		}
		if err := writer.WriteMessages(context.Background(), msg); err != nil {
			log.Printf("kafka write error: %v", err)
			return c.JSON(http.StatusInternalServerError, map[string]string{"error": "failed to write to kafka"})
		}
		return c.JSON(http.StatusOK, map[string]string{"status": "ok"})
	})

	e.Logger.Fatal(e.Start(":8080"))
}
