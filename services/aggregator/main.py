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

# Cassandraセッションを取得するヘルパー関数
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

def update_daily_summaries(session, date):
    # 指定日付の全注文を取得（ALLOW FILTERINGを一時的に使用）
    rows = session.execute(
        "SELECT menu_type FROM raw_orders "
        "WHERE order_date = %s",
        [date]
    )
    
    # アプリケーション側で集計
    washoku_count = 0
    yoshoku_count = 0
    for i, row in enumerate(rows):
        if row.menu_type == 'washoku':
            washoku_count += 1
        elif row.menu_type == 'yoshoku':
            yoshoku_count += 1
        
    # daily_order_summariesに挿入/更新
    session.execute(
        "INSERT INTO daily_order_summaries (order_date, menu_type, cnt) "
        "VALUES (%s, 'washoku', %s)",
        [date, washoku_count]
    )
    session.execute(
        "INSERT INTO daily_order_summaries (order_date, menu_type, cnt) "
        "VALUES (%s, 'yoshoku', %s)",
        [date, yoshoku_count]
    )

def update_user_preferences(session, date):
    # 指定日付に注文したユーザーIDを取得
    user_rows = session.execute(
        "SELECT user_id FROM raw_orders WHERE order_date = %s GROUP BY order_date, user_id",
        [date]
    )
    
    # 各ユーザーの注文カウントを取得して嗜好を更新
    for user_row in user_rows:
        user_id = user_row.user_id
        
        # user_order_countsから現在のカウントを取得 (存在しない場合は0で初期化)
        count_row = session.execute(
            "SELECT washoku_cnt, yoshoku_cnt FROM user_order_counts WHERE user_id = %s",
            [user_id]
        ).one()
        
        # カウンタの初期化 (count_rowがNoneまたは各カウンタがNoneの場合に対応)
        washoku_cnt = 0
        yoshoku_cnt = 0
        if count_row:
            washoku_cnt = int(count_row.washoku_cnt) if count_row.washoku_cnt is not None else 0
            yoshoku_cnt = int(count_row.yoshoku_cnt) if count_row.yoshoku_cnt is not None else 0

        # 嗜好を決定
        new_pref = 'washoku' if washoku_cnt > yoshoku_cnt else 'yoshoku'
        
        # 反対の嗜好レコードを削除
        session.execute(
            "DELETE FROM user_preferences WHERE preferred_menu_type = %s AND user_id = %s",
            ['yoshoku' if new_pref == 'washoku' else 'washoku', user_id]
        )
        # 新しい嗜好を挿入
        session.execute(
            "INSERT INTO user_preferences (preferred_menu_type, user_id) "
            "VALUES (%s, %s)",
            [new_pref, user_id]
        )

# Entry point for the aggregation service
def aggregate_orders(date_str=None):
    session = get_cassandra_session()
    
    # 日付が指定されていない場合は前日の日付を使う
    if date_str is None:
        yesterday = datetime.utcnow() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
    else:
        # 日付フォーマットを検証
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD")
            return
    
    # 日次サマリ更新
    update_daily_summaries(session, date)
    
    # ユーザー嗜好更新
    update_user_preferences(session, date)
    
    print(f"Aggregated data for {date_str}")

if __name__ == '__main__':
    import sys
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    aggregate_orders(date_arg)
