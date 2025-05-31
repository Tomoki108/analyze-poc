.PHONY: create-topics describe-topics

# 全コンテナを削除、再作成して起動
du-containers:
	@docker compose down --remove-orphans && docker compose up -d

# 全コンテナを削除、イメージを再ビルド、コンテナを再作成して起動
dbu-containers:
	@docker compose down --remove-orphans && docker compose up -d --build

#########
# Kafka #
#########
create-topics:
	@docker compose exec kafka \
		kafka-topics --create --bootstrap-server kafka:9092 \
		--replication-factor 1 --partitions 1 --topic order-logs || echo "order-logs already exists"

describe-topics:
	@docker compose exec kafka \
		kafka-topics --describe --bootstrap-server kafka:9092 --topic order-logs

list-topics:
	@docker compose exec kafka \
		kafka-topics --list --bootstrap-server kafka:9092

#############
# Cassandra #
#############
rebuild-cassandra:
	@docker compose up -d --build cassandra

log-cassandra:
	@docker compose logs -f cassandra

# 初期化スクリプトの実行制御が難しかったので、手動コマンドを用意
# https://medium.com/@driptaroop.das/execute-startup-scripts-in-cassandra-docker-13b6563d4f2f
init-cassandra:
	@docker compose exec cassandra cqlsh -f /docker-entrypoint-initdb.d/01_create_keyspace_and_tables.cql

clean-cassandra:
	@echo "Cleaning Cassandra database..."
	@docker compose exec cassandra cqlsh -e "TRUNCATE analyze_poc.raw_orders;"
	@docker compose exec cassandra cqlsh -e "TRUNCATE analyze_poc.user_cuisine_counts;"
	@docker compose exec cassandra cqlsh -e "TRUNCATE analyze_poc.cuisine_segment_counts;"
	@docker compose exec cassandra cqlsh -e "TRUNCATE analyze_poc.daily_cuisine_summary;"
	@echo "Database cleaned successfully"

drop-cassandra:
	@echo "Dropping Cassandra keyspace..."
	@docker compose exec cassandra cqlsh -e "DROP KEYSPACE IF EXISTS analyze_poc;"
	@echo "Keyspace dropped successfully"

describe-keyspaces:
	@docker compose exec cassandra cqlsh -e "DESCRIBE KEYSPACES;"

##############
# log-ingest #
##############
rebuild-log-ingest:
	@docker compose up -d --build log-ingest

log-log-ingest:
	@docker compose logs -f log-ingest

################
# log-consumer #
################
rebuild-log-consumer:
	@docker compose up -d --build log-consumer

log-log-consumer:
	@docker compose logs -f log-consumer

###############
# aggregator #
###############
rebuild-aggregator:
	@docker compose up -d --build aggregator

# 指定した日付でaggregatorを実行する (例: make run-aggregator date=2025-05-31)
run-aggregator:
	@docker compose exec aggregator python main.py $(date)

###########
# web-summary #
###########
rebuild-summary-api:
	@docker compose up -d --build summary-api

log-summary-api:
	@docker compose logs -f summary-api


########
# test #
########

# date=2025-05-31のログが大量に出力される
test:
	@./log-stream-test.sh

