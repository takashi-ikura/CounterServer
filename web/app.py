import sqlite3
import os
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask import jsonify

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "data_store.db"))

# DB接続用の関数
def get_db_connection():
    # DB接続用の関数
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # カラム名でデータを取り出せるようにする設定
    return conn

# DBから最新のカウンタ値を取得する関数
def show_counter():
    # DBから最新のカウンタ値を取得する関数
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT sum(val) as total FROM measurements WHERE is_active = 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["total"]
    else:
        return 0  # データがない場合は0を返す

@app.route('/')
def counter():
    count = show_counter()  # DBから最新のカウンタ値を取得
    return render_template('counter.html',count=count)

@app.route('/api/notify_update')
def notify_update():
    # 接続中の全ブラウザに 'update_event' を送る
    socketio.emit('update_event', {'message': 'refresh_needed'})
    return "OK"

@app.route('/api/get_current_count')
def get_current_count():
    # 自作の関数を実行
    val = show_counter()
    # 結果をJSON（辞書のような形式）でブラウザに返却
    return jsonify({"count": val})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)