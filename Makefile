.PHONY: create-topics describe-topics

# Kafka トピックを作成する
create-topics:
	@echo "Creating Kafka topics..."
	@docker-compose exec kafka \
		kafka-topics --create --bootstrap-server kafka:9092 \
		--replication-factor 1 --partitions 1 --topic visit-logs || echo "visit-logs already exists"
	@docker-compose exec kafka \
		kafka-topics --create --bootstrap-server kafka:9092 \
		--replication-factor 1 --partitions 1 --topic order-logs || echo "order-logs already exists"

# Kafka トピックの情報を表示する
describe-topics:
	@echo "Describing Kafka topics..."
	@docker-compose exec kafka \
		kafka-topics --describe --bootstrap-server kafka:9092 --topic visit-logs,order-logs

rebuild-log-ingest:
	@echo "Rebuilding log-ingest service..."
	@docker-compose up -d --build log-ingest

log-ingest:
	@echo "Starting log-ingest service..."
	@docker-compose up -d log-ingest