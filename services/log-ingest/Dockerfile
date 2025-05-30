# Dockerfile for Log-Ingest Service
FROM golang:1.23-alpine
WORKDIR /app

# 依存関係のキャッシュ
COPY go.mod go.sum ./
RUN go mod download

# ソースをコピーしてビルド
COPY . ./
RUN go build -o log-ingest .

# ポートと実行コマンド
EXPOSE 8080
CMD ["/app/log-ingest"]
