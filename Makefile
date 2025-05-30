.PHONY: create-topics describe-topics

# Kafka トピックを作成する
create-topics:
	@docker-compose exec kafka \
		kafka-topics --create --bootstrap-server kafka:9092 \
		--replication-factor 1 --partitions 1 --topic order-logs || echo "order-logs already exists"

# Kafka トピックの情報を表示する
describe-topics:
	@docker-compose exec kafka \
		kafka-topics --describe --bootstrap-server kafka:9092 --topic order-logs

rebuild-log-ingest:
	@docker-compose up -d --build log-ingest

restart-log-ingest:
	@docker-compose restart log-ingest

rebuild-cassandra:
	@docker-compose up -d --build cassandra

log-ingest:
	@docker-compose up -d log-ingest

log-log-ingest:
	@docker-compose logs -f log-ingest