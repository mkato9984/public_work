import pytest
import sys
import os

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app_github import create_app
from db_utils import DatabaseManager
from config import Config

@pytest.fixture
def app():
    """テスト用のFlaskアプリケーションを作成"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        # テスト用データベースの初期化をスキップ（モック環境のため）
        # データベース接続が必要なテストでは個別にモックを設定
        try:
            # データベース初期化のテスト（実際の接続は行わない）
            print("テスト環境: データベース初期化をスキップ")
        except Exception as e:
            print(f"テスト環境警告: {e}")
        
        yield app

@pytest.fixture
def client(app):
    """テスト用クライアント"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """テスト用ランナー"""
    return app.test_cli_runner()

def test_config():
    """設定テスト"""
    assert Config.DB_HOST is not None
    assert Config.DB_NAME is not None
    assert Config.DB_USER is not None
