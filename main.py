import asyncio
import sqlite3
import datetime
import websockets
import json
import clsLog
import requests

# --- データベース設定 ---
DB_NAME = "data_store.db"
PORT_NO = 8765

LOG = clsLog.AppLogger(log_dir="/app", log_name="server.log")

# --- ブラウザ更新通知関数 ---
def notify_update():
    try:
        requests.get("http://localhost:5000/api/notify_update")
    except Exception as e:
        LOG.error(f"notify_update(): {e}")

# --- データベース初期化関数 ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            val INTEGER NOT NULL,
            savetime TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

# --- データ保存関数 ---
def save_to_db(value):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO measurements (val, savetime, is_active) VALUES (?, ?, ?)",
            (value, now, True)
        )
        conn.commit()
        LOG.info(f"Saved: {value} at {now}")
    except Exception as e:
        LOG.error(f"Database error: {e}")
    finally:
        conn.close()

# --- カウンターリセット関数---
def reset_counter():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        sql = "UPDATE measurements SET is_active = 0 WHERE is_active = 1"
        cursor.execute(sql)
        conn.commit()
        LOG.info(f"Counter Reset")
    except Exception as e:
        LOG.error(f"Database error: {e}")
    finally:
        conn.close()

async def handler(websocket):
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                DataType = data.get("type")

                ###################
                #カウント
                ###################
                if DataType == "counter":
                    number = data.get("value")
                    save_to_db(number)
                    await websocket.send(f"Received and saved: {number}")
                    notify_update()  # ブラウザ更新通知

                ###################
                #カウントのリセット
                ###################
                if DataType == "reset":
                    reset_counter()
                    await websocket.send("Counter reset.")
                    notify_update()  # ブラウザ更新通知

            except (ValueError, TypeError):
                await websocket.send("Error: Please send a valid integer.")
    except websockets.exceptions.ConnectionClosed:
        pass # クライアントが切断した場合は何もしない

async def main():
    init_db()
    
    # サーバーを起動し、そのオブジェクトを保持
    async with websockets.serve(handler, "localhost", PORT_NO):
        LOG.info(f"WebSocket Server started on ws://localhost:{PORT_NO} ")
        LOG.info("Press Ctrl+C to stop the server.")
        
        try:
            # 終了信号を待機する仕組み
            await asyncio.Future() 
        except asyncio.CancelledError:
            # Ctrl+C などによるキャンセルをここでキャッチ
            LOG.info("Shutting down server...")

if __name__ == "__main__":
    try:

        asyncio.run(main())

        #デバッグ用 ----------------------
        #カウンターのリセット
        #reset_counter() 
        #カウントの追加
        #save_to_db(10)

    except KeyboardInterrupt:
        # Ctrl+Cによるエラー出力をここで食い止める
        LOG.info("\nServer stopped.")