import os
from typing import Optional
import urllib.parse

class Config:
    """RAGシステムの設定クラス"""
    
    # 環境判定
    IS_PRODUCTION = os.getenv("FLASK_ENV") == "production"
    IS_HEROKU = os.getenv("DYNO") is not None
    IS_GITHUB_CODESPACES = os.getenv("CODESPACES") == "true"
    
    # データベース設定（Heroku対応）
    if IS_HEROKU and os.getenv("DATABASE_URL"):
        # HerokuのDATABASE_URLを解析
        database_url = os.getenv("DATABASE_URL")
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        parsed = urllib.parse.urlparse(database_url)
        DB_HOST = parsed.hostname
        DB_NAME = parsed.path[1:]  # 先頭の"/"を削除
        DB_USER = parsed.username
        DB_PASSWORD = parsed.password
        DB_PORT = parsed.port or 5432
    else:
        # ローカル・Codespaces環境
        DB_HOST: str = os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "localhost"))
        DB_NAME: str = os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "rag_db"))
        DB_USER: str = os.getenv("POSTGRES_USER", os.getenv("DB_USER", "postgres"))
        DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD", "test1234"))
        DB_PORT: int = int(os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432")))
    
    # Gemini API設定
    GOOGLE_API_KEY: Optional[str] = os.getenv("GOOGLE_API_KEY")
    
    # Flask設定
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # デバッグ設定
    DEBUG: bool = not IS_PRODUCTION
      # RAGシステム設定
    EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSION: int = 768
    DEFAULT_TOP_K: int = 3
    MAX_CONTEXT_LENGTH: int = 2000
    
    # 生成AI設定
    GENERATION_CONFIG = {
        "temperature": 0.2,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    }
    
    @classmethod
    def validate(cls) -> bool:
        """設定の妥当性をチェックします"""
        if not cls.GOOGLE_API_KEY:
            print("警告: GOOGLE_API_KEYが設定されていません。")
            return False
        return True
