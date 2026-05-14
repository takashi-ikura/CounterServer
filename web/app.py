import sqlite3
import os
from flask import Flask, render_template
from flask_socketio import SocketIO
from flask import jsonify
from dotenv import load_dotenv

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

load_dotenv()
SERVER_WS_URL = os.getenv("SERVER_WS_URL")
PORT_NO = int(os.getenv("PORT_NO"))

@app.route('/')
def counter():
    return render_template('counter.html', SERVER_WS_URL=SERVER_WS_URL)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/api/notify_update')
def notify_update():
    # 接続中の全ブラウザに 'update_event' を送る
    socketio.emit('update_event', {'message': 'refresh_needed'})
    return "OK"

if __name__ == '__main__':
    socketio.run(app, debug=True, port=PORT_NO)