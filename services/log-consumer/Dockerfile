# Dockerfile for Log-Consumer Service
FROM golang:1.23-alpine
WORKDIR /app

# 依存関係のキャッシュ
COPY go.mod go.sum ./
RUN go mod download

# ソースをコピーしてビルド
COPY . ./
RUN go build -o log-consumer .

# 実行コマンド
CMD ["/app/log-consumer"]
