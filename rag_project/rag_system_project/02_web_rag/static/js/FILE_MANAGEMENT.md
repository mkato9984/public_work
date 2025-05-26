# JavaScript ファイル管理記録

## ファイル構成と用途

### 現在使用中
- `script.js` - **メインファイル** (削除機能修正済み、本番使用)

### バックアップ・履歴ファイル
- `script_fixed.js` - 修正前のクリーンバージョン
- `script_backup.js` - 最初期のバックアップ
- `script_new.js` - 中間バージョン 
- `script_test.js` - タブ切り替えテスト用

## 推奨管理方法

### 保持すべきファイル
1. `script.js` - 現在の本番ファイル
2. `script_fixed.js` - 作業開始前のクリーンバックアップ

### 整理可能ファイル（必要に応じて削除）
1. `script_backup.js` - 古いバックアップ
2. `script_new.js` - 中間バージョン
3. `script_test.js` - テスト専用（機能確認後不要）

## ファイルサイズ確認
- script.js: 最新（削除機能完全版）
- script_fixed.js: クリーンバージョン（参考用）

## 備考
- 今後の開発では script.js をベースに作業
- 大きな変更前は script_fixed.js をベースにコピー作成を推奨
