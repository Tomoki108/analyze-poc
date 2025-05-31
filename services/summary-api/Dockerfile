FROM golang:1.23-alpine as builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o summary-api

FROM alpine:3.18
WORKDIR /app
COPY --from=builder /app/summary-api .

EXPOSE 8081
CMD ["./summary-api"]
