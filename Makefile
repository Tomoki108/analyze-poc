.PHONY: create-topics describe-topics

#########
# Kafka #
#########
create-topics:
	@docker-compose exec kafka \
		kafka-topics --create --bootstrap-server kafka:9092 \
		--replication-factor 1 --partitions 1 --topic order-logs || echo "order-logs already exists"

describe-topics:
	@docker-compose exec kafka \
		kafka-topics --describe --bootstrap-server kafka:9092 --topic order-logs

list-topics:
	@docker-compose exec kafka \
		kafka-topics --list --bootstrap-server kafka:9092

#############
# Cassandra #
#############
rebuild-cassandra:
	@docker-compose up -d --build cassandra

log-cassandra:
	@docker-compose logs -f cassandra

##############
# log-ingest #
##############
rebuild-log-ingest:
	@docker-compose up -d --build log-ingest

log-log-ingest:
	@docker-compose logs -f log-ingest

################
# log-consumer #
################
rebuild-log-consumer:
	@docker-compose up -d --build log-consumer

log-log-consumer:
	@docker-compose logs -f log-consumer

###############
# aggregator #
###############
rebuild-aggregator:
	@docker-compose up -d --build aggregator

# 指定した日付でaggregatorを実行する (例: make run-aggregator date=2025-05-30)
run-aggregator:
	@docker-compose exec aggregator python main.py $(date)
