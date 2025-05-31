import os
from datetime import datetime, timedelta
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Cassandra接続設定
CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'cassandra')
CASSANDRA_PORT = os.getenv('CASSANDRA_PORT', '9042')
CASSANDRA_USER = os.getenv('CASSANDRA_USER', 'cassandra')
CASSANDRA_PASS = os.getenv('CASSANDRA_PASS', 'cassandra')
KEYSPACE = 'analyze_poc'

def get_cassandra_session():
    auth_provider = PlainTextAuthProvider(
        username=CASSANDRA_USER,
        password=CASSANDRA_PASS
    )
    cluster = Cluster(
        [CASSANDRA_HOST],
        port=int(CASSANDRA_PORT),
        auth_provider=auth_provider
    )
    return cluster.connect(KEYSPACE)

def aggregate_orders(date_str=None):
    session = get_cassandra_session()
    
    # 日付が指定されていない場合は前日の日付を使う
    if date_str is None:
        yesterday = datetime.utcnow() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
    else:
        # 日付フォーマットを検証
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD")
            return
    
    # 前日の注文データを取得
    query = """
        SELECT menu_type, COUNT(*) as count
        FROM raw_orders
        WHERE ts >= %s AND ts < %s
        GROUP BY menu_type
    """
    start_date = f"{date_str} 00:00:00"
    end_date = f"{date_str} 23:59:59"
    
    rows = session.execute(query, [start_date, end_date])
    
    # 集計結果をdaily_cuisine_summaryに保存 (Cassandraでは同じPK（日付・セグメント）のレコードがある場合は上書き)
    insert_query = """
        INSERT INTO daily_cuisine_summary (order_date, segment, cnt)
        VALUES (%s, %s, %s)
    """
    
    washoku_count = 0
    yoshoku_count = 0
    
    for row in rows:
        if row.menu_type == 'washoku':
            washoku_count = row.count
        elif row.menu_type == 'yoshoku':
            yoshoku_count = row.count
    
    session.execute(insert_query, [date_str, 'washoku', washoku_count])
    session.execute(insert_query, [date_str, 'yoshoku', yoshoku_count])
    
    print(f"Aggregated data for {date_str}: washoku={washoku_count}, yoshoku={yoshoku_count}")

if __name__ == '__main__':
    import sys
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    aggregate_orders(date_arg)
