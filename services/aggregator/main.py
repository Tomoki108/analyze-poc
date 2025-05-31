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
    
    # 指定日付の注文データを取得（ページネーションでメモリ効率化）
    query = """
        SELECT menu_type
        FROM raw_orders
        WHERE order_date = ?
    """
    # datetimeオブジェクトに変換
    start_date = datetime.strptime(date_str, '%Y-%m-%d')
    end_date = datetime.strptime(date_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    
    # アプリケーション側で集計
    washoku_count = 0
    yoshoku_count = 0
    
    # ページネーションでデータ取得
    page_size = 1000
    stmt = session.prepare(query)
    stmt.fetch_size = page_size
    
    rows = session.execute(stmt, [start_date.date()])
    for row in rows:
        if row.menu_type == 'washoku':
            washoku_count += 1
        elif row.menu_type == 'yoshoku':
            yoshoku_count += 1
    
    # 集計結果をdaily_cuisine_summaryに保存
    insert_query = """
        INSERT INTO daily_cuisine_summary (order_date, segment, cnt)
        VALUES (%s, %s, %s)
    """
    
    session.execute(insert_query, [date_str, 'washoku', washoku_count])
    session.execute(insert_query, [date_str, 'yoshoku', yoshoku_count])
    
    print(f"Aggregated data for {date_str}: washoku={washoku_count}, yoshoku={yoshoku_count}")

if __name__ == '__main__':
    import sys
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    aggregate_orders(date_arg)
