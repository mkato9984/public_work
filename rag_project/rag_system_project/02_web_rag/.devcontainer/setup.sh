#!/bin/bash

echo "🚀 RAGシステム環境セットアップを開始します..."

# Python依存関係のインストール
echo "📦 Python依存関係をインストール中..."
pip install --upgrade pip
pip install -r requirements.txt

# PostgreSQLサービスの開始
echo "🗄️ PostgreSQLサービスを開始中..."
sudo service postgresql start

# PostgreSQLユーザーとデータベースの作成
echo "👤 PostgreSQLユーザーとデータベースを設定中..."
sudo -u postgres createuser -s vscode 2>/dev/null || echo "ユーザー 'vscode' は既に存在します"
sudo -u postgres createdb rag_db -O vscode 2>/dev/null || echo "データベース 'rag_db' は既に存在します"

# pgvector拡張の有効化
echo "🔧 pgvector拡張を有効化中..."
sudo -u postgres psql -d rag_db -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 環境変数の設定
echo "⚙️ 環境変数を設定中..."
if [ ! -f .env ]; then
    cat > .env << EOL
# PostgreSQL設定
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=vscode
POSTGRES_PASSWORD=

# Google Gemini API (GitHub Codespacesでは環境変数から取得)
GOOGLE_API_KEY=\${GOOGLE_API_KEY}

# Flask設定
FLASK_ENV=development
FLASK_DEBUG=True
EOL
    echo "📄 .envファイルを作成しました"
fi

# データベーステーブルの初期化
echo "🗂️ データベーステーブルを初期化中..."
python -c "
from db_utils import create_tables
try:
    create_tables()
    print('✅ データベーステーブルが正常に作成されました')
except Exception as e:
    print(f'❌ データベース初期化エラー: {e}')
"

echo "✅ セットアップ完了！"
echo "🌐 Codespaces環境でアプリケーションを起動するには: python web_app_codespaces.py"
echo "📋 ポート5000でWebアプリケーションにアクセスできます"
echo ""
echo "💡 ヒント:"
echo "   - GOOGLE_API_KEYが未設定でもデモモードで動作します"
echo "   - 完全な機能を利用するには: export GOOGLE_API_KEY='your-key'"
