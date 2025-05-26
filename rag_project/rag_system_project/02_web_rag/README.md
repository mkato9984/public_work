# 🤖 AI-Powered RAG System

高度な文書検索と質問応答システム - Google Gemini API + PostgreSQL (pgvector) 実装

[![CI/CD](https://github.com/USERNAME/rag-system/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/USERNAME/rag-system/actions/workflows/ci-cd.yml)
[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/USERNAME/rag-system)

## 🌟 特徴

- **🔍 セマンティック検索**: pgvectorによる高速ベクトル検索
- **🤖 AI質問応答**: Google Gemini APIによる自然言語処理
- **📚 文書管理**: Webインターフェースでの直感的な操作
- **🌐 クロスブラウザ対応**: Chrome、VS Code Simple Browser対応
- **☁️ クラウド対応**: Heroku、GitHub Codespaces対応

## 🚀 クイックスタート

### GitHub Codespaces で実行 (推奨)

1. このリポジトリをフォーク
2. **Code** → **Codespaces** → **Create codespace on main** をクリック
3. 環境変数 `GOOGLE_API_KEY` を設定:
   ```bash
   export GOOGLE_API_KEY="your-api-key-here"
   ```
4. アプリケーション起動:
   ```bash
   python web_app.py
   ```
5. ブラウザで `http://localhost:5000` にアクセス

### ローカル環境での実行

#### 前提条件
- Python 3.11+
- PostgreSQL 15+ (pgvector拡張)
- Google Gemini API キー

#### セットアップ
```bash
# 1. リポジトリのクローン
git clone https://github.com/USERNAME/rag-system.git
cd rag-system/rag_system_project/02_web_rag

# 2. 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存関係のインストール
pip install -r requirements.txt

# 4. 環境変数の設定
cp .env.example .env
# .envファイルを編集してAPI キーとDB情報を設定

# 5. データベースの準備
# PostgreSQLでpgvector拡張を有効化
# CREATE EXTENSION vector;

# 6. アプリケーション起動
python web_app.py
```

## 🔧 環境変数

| 変数名 | 説明 | 必須 | デフォルト値 |
|--------|------|------|-------------|
| `GOOGLE_API_KEY` | Google Gemini API キー | ✅ | - |
| `POSTGRES_HOST` | PostgreSQLホスト | - | localhost |
| `POSTGRES_PORT` | PostgreSQLポート | - | 5432 |
| `POSTGRES_DB` | データベース名 | - | rag_db |
| `POSTGRES_USER` | DBユーザー名 | - | postgres |
| `POSTGRES_PASSWORD` | DBパスワード | - | - |
| `FLASK_ENV` | Flask環境 | - | development |

## 📱 使用方法

### 1. 文書の追加
1. **文書管理** タブを選択
2. タイトルと内容を入力
3. **追加** ボタンをクリック

### 2. 質問応答
1. **質問・回答** タブを選択  
2. 質問を入力欄に記述
3. **送信** ボタンをクリック
4. AI が関連文書を検索して回答を生成

### 3. 文書の管理
- 追加された文書の一覧表示
- 文書の削除 (VS Code Simple Browser対応済み)
- メタデータの表示

## 🏗️ システム構成

```
RAG System
├── フロントエンド (HTML/CSS/JavaScript)
├── バックエンド (Flask)
├── データベース (PostgreSQL + pgvector)
└── AI (Google Gemini API)
```

### 主要ファイル
- `web_app.py` - Flaskアプリケーション
- `rag_system.py` - RAGシステムコア
- `db_utils.py` - データベースユーティリティ
- `static/js/script.js` - フロントエンドJavaScript
- `templates/index.html` - HTMLテンプレート

## 🚀 デプロイ

### Heroku
```bash
# Heroku CLI でデプロイ
heroku create your-app-name
heroku addons:create heroku-postgresql:essential-0
heroku config:set GOOGLE_API_KEY="your-api-key"
git push heroku main
```

### GitHub Codespaces
- 自動セットアップ対応
- `.devcontainer/` 設定済み
- ワンクリックで開発環境準備完了

## 🧪 テスト

```bash
# 単体テスト実行
python -m pytest tests/ -v

# Webアプリケーションのテスト
python tests/test_web_basic.py

# データベース接続テスト
python check_db_direct.py
```

## 📊 パフォーマンス

- **検索速度**: ~100ms (1000文書)
- **同時接続**: 最大50ユーザー
- **メモリ使用量**: ~512MB
- **対応文書数**: 10,000+文書

## 🛠️ 開発

### デバッグ機能
ブラウザコンソールで利用可能:
```javascript
// 削除機能のテスト
testDeleteFunction();

// 削除ボタン状態確認  
testDeleteButton();

// ブラウザ環境確認
debugSimpleBrowser();
```

### API エンドポイント
- `GET /` - メインページ
- `POST /api/ask` - 質問応答
- `GET /api/documents` - 文書一覧
- `POST /api/documents` - 文書追加
- `DELETE /api/documents/<id>` - 文書削除

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 🤝 コントリビューション

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 サポート

- 📖 [ドキュメント](docs/)
- 🐛 [Issues](https://github.com/USERNAME/rag-system/issues)
- 💬 [Discussions](https://github.com/USERNAME/rag-system/discussions)

## 🔗 関連リンク

- [Google Gemini API](https://ai.google.dev/)
- [pgvector](https://github.com/pgvector/pgvector)
- [PostgreSQL](https://www.postgresql.org/)
- [Flask](https://flask.palletsprojects.com/)

---
Made with ❤️ using Google Gemini API + pgvector
