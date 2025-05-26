#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
簡単なWebアプリケーションテスト
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '''
    <html>
    <head>
        <title>RAG System Test</title>
    </head>
    <body>
        <h1>🎉 RAG System is Running!</h1>
        <p>Webアプリケーションが正常に動作しています。</p>
        <p>現在時刻: <span id="time"></span></p>
        <script>
            document.getElementById('time').textContent = new Date().toLocaleString();
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("簡単なWebアプリケーションを起動中...")
    print("http://localhost:5000 でアクセスできます")
    app.run(host='0.0.0.0', port=5000, debug=True)
