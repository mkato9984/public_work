#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
最小限のWebアプリケーション診断ツール
"""

try:
    print("🔍 診断開始...")
    
    # 1. Flaskのインポートテスト
    print("1. Flaskインポートテスト...")
    from flask import Flask
    print("   ✅ Flask正常")
    
    # 2. アプリ作成テスト
    print("2. Flaskアプリ作成テスト...")
    app = Flask(__name__)
    print("   ✅ アプリ作成成功")
    
    # 3. ルート定義テスト
    print("3. ルート定義テスト...")
    @app.route('/')
    def test_route():
        return '''
        <h1>🎉 Webアプリ診断成功！</h1>
        <p>Flaskは正常に動作しています。</p>
        <p>診断時刻: ''' + str(__import__('datetime').datetime.now()) + '''</p>
        '''
    print("   ✅ ルート定義成功")
    
    # 4. サーバー起動テスト
    print("4. サーバー起動テスト...")
    print("   📡 http://localhost:8080 で起動中...")
    print("   🌐 ブラウザでアクセスしてください")
    
    app.run(host='127.0.0.1', port=8080, debug=False)
    
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
except Exception as e:
    print(f"❌ エラー: {e}")
    import traceback
    traceback.print_exc()
