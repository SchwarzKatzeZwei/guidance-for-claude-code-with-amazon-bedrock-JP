# テストスイート ドキュメント

このディレクトリには、「Claude Code with Bedrock」プロジェクトのすべてのテストが含まれます。テストはカテゴリ別に整理されており、テストフレームワークとして pytest を使用します。

## クイックスタート

```bash
# source ディレクトリへ移動
cd source

# 依存関係をインストール
poetry install

# すべてのテストを実行（注: まとめて実行すると失敗するテストがある場合があります。トラブルシューティング参照）
poetry run pytest ../tests

# 詳細（verbose）出力で実行
poetry run pytest ../tests -v

# 推奨: 最良の結果のため、カテゴリ別に実行
poetry run pytest ../tests/lambda/test_quota_monitor.py -v      # クォータ監視テスト
poetry run pytest ../tests/lambda/test_metrics_aggregator.py -v  # メトリクス集約テスト
poetry run pytest ../tests/cli/ -v                              # CLI コマンドのテスト
poetry run pytest ../tests/integration/ -v                      # 統合テスト
```

## 前提条件

テストを実行する前に、次を確認してください。

1. **Python 3.12+** がインストールされていること
2. 依存関係管理のための **Poetry**
3. **作業ディレクトリ**: テスト実行前に `source` ディレクトリへ移動していること

```bash
cd source
poetry install  # テスト要件を含むすべての依存関係をインストール
```

## テスト構成

```
tests/
├── cli/
│   └── commands/      # CLI コマンドのテスト
│       ├── test_init.py            # init コマンドの検証テスト
│       ├── test_init_e2e.py        # init コマンドの E2E テスト
│       ├── test_init_models.py     # init のモデル選択テスト
│       ├── test_init_quota.py      # init のクォータ設定テスト
│       ├── test_init_source_regions.py  # init のソースリージョン テスト
│       ├── test_deploy_quota.py    # deploy のクォータ監視テスト
│       ├── test_package.py         # package コマンドのテスト
│       ├── test_package_async.py   # package の非同期ビルド テスト
│       └── test_package_models.py  # package のモデル テスト
├── test_cloudformation.py  # CloudFormation テンプレート検証
├── test_config.py          # プロファイル／設定管理のテスト
├── test_config_models.py   # モデル設定の永続化テスト
├── test_models.py          # モデル設定テスト
├── test_smoke.py           # 包括的なスモークテスト
└── test_source_regions.py  # ソースリージョン テスト
```

### 将来のテストカテゴリ（未実装）

以下のカテゴリは計画されていますが、現時点では未実装です。

- **Lambda 関数テスト** — クォータ監視およびメトリクス集約 Lambda のテスト  
  - boto3 のモジュールレベル import による分離問題の修正が必要
- **統合テスト** — AWS サービスを用いたエンドツーエンド テスト  
  - LocalStack または専用のテスト用 AWS アカウントでの実施を予定
- **追加の CLI コマンド** — deploy/destroy/distribute/quota/status コマンドのテスト  
  - 全リストは guidance-docs/TESTING_TODO.md を参照

## テストの実行

### 全テスト

```bash
# 全テストを実行
poetry run pytest ../tests

# 全テストを verbose で実行
poetry run pytest ../tests -v

# カバレッジレポート付きで実行
poetry run pytest ../tests --cov=claude_code_with_bedrock --cov-report=term-missing
```

### カテゴリ別

#### CLI コマンドのテスト
```bash
# すべての CLI テスト
poetry run pytest ../tests/cli/commands/

# 特定コマンドのテスト
poetry run pytest ../tests/cli/commands/test_init*.py    # init コマンドのテスト
poetry run pytest ../tests/cli/commands/test_deploy*.py  # deploy コマンドのテスト
poetry run pytest ../tests/cli/commands/test_package*.py # package コマンドのテスト
```

#### コア機能のテスト
```bash
# モデル設定テスト
poetry run pytest ../tests/test_models.py

# ソースリージョン テスト
poetry run pytest ../tests/test_source_regions.py

# CloudFormation テンプレート検証
poetry run pytest ../tests/test_cloudformation.py

# 設定／プロファイルのテスト
poetry run pytest ../tests/test_config*.py

# スモークテスト（import、インスタンス生成）
poetry run pytest ../tests/test_smoke.py
```

### 特定のテストファイル／関数

```bash
# 特定ファイルを実行
poetry run pytest ../tests/lambda/test_quota_monitor.py

# 特定クラスを実行
poetry run pytest ../tests/lambda/test_quota_monitor.py::TestQuotaMonitorLambda

# 特定関数を実行
poetry run pytest ../tests/lambda/test_quota_monitor.py::TestQuotaMonitorLambda::test_lambda_handler_no_usage
```

## テストオプション

### 出力制御

```bash
# quiet モード（最小出力）
poetry run pytest ../tests -q

# verbose モード（詳細出力）
poetry run pytest ../tests -v

# さらに詳細（テスト出力を表示）
poetry run pytest ../tests -vv

# テスト中の print を表示
poetry run pytest ../tests -s

# verbose + print を併用
poetry run pytest ../tests -xvs
```

### 失敗時の挙動

```bash
# 最初の失敗で停止
poetry run pytest ../tests -x

# N 件失敗したら停止
poetry run pytest ../tests --maxfail=3

# 前回失敗したテストのみ実行
poetry run pytest ../tests --lf

# 失敗したテストを先に実行し、その後成功分を実行
poetry run pytest ../tests --ff
```

### パフォーマンス

```bash
# 並列実行（pytest-xdist が必要）
poetry run pytest ../tests -n auto

# 遅いテスト上位を表示
poetry run pytest ../tests --durations=10

# タイムアウト設定（pytest-timeout が必要）
poetry run pytest ../tests --timeout=60
```

### カバレッジレポート

```bash
# カバレッジレポートを生成
poetry run pytest ../tests --cov=claude_code_with_bedrock

# 未カバー行を表示
poetry run pytest ../tests --cov=claude_code_with_bedrock --cov-report=term-missing

# HTML カバレッジレポートを生成
poetry run pytest ../tests --cov=claude_code_with_bedrock --cov-report=html

# 特定モジュールのカバレッジ
poetry run pytest ../tests --cov=claude_code_with_bedrock.cli.commands
```

## テストカテゴリの説明

### ユニットテスト
- **test_models.py**: Claude モデル設定、クロスリージョンプロファイル、モデル ID マッピングのテスト
- **test_source_regions.py**: ソースリージョン設定とリージョン利用可否のテスト

### CLI コマンドのテスト
- **test_init_*.py**: `ccwb init`（設定ウィザード）のテスト
- **test_deploy_*.py**: `ccwb deploy`（インフラデプロイ）のテスト
- **test_package_*.py**: `ccwb package`（配布物作成）のテスト

### Lambda 関数テスト
- **test_quota_monitor.py**: ユーザー利用状況をチェックしアラートを送信する、クォータ監視 Lambda のテスト
- **test_metrics_aggregator.py**: CloudWatch Logs を処理する、メトリクス集約 Lambda のテスト

### 統合テスト
- **test_quota_monitoring_integration.py**: クォータ監視フローのエンドツーエンド テスト

### フィクスチャ
- **quota_fixtures.py**: クォータ監視テスト向けの再利用可能なテストデータ／モックオブジェクト

## よく使うコマンド（リファレンス）

```bash
# 手早いテスト（失敗しない限りほぼ出力なし）
poetry run pytest ../tests -q

# 開発時のテスト（verbose、失敗で停止、print 表示）
poetry run pytest ../tests -xvs

# カバレッジ付きで全体実行
poetry run pytest ../tests --cov=claude_code_with_bedrock --cov-report=term-missing

# 特定領域に関するテストだけ実行
poetry run pytest ../tests -k "quota"  # 名前に quota を含むテストをすべて実行

# パターン一致で実行
poetry run pytest ../tests -k "test_deploy or test_init"

# 遅いテストを除外（マークされている場合）
poetry run pytest ../tests -m "not slow"
```

## トラブルシューティング

### モジュール import エラー
Lambda 関数で import エラーが発生する場合：

- Lambda 関数ディレクトリにハイフン（`-`）が含まれており、Python のモジュール名として無効
- テスト側で `sys.path` にパスを動的に追加して対処しています
- テストは `source` ディレクトリから実行していることを確認してください

### テスト分離（Isolation）の問題
Lambda テストは、個別に実行すると通るのにまとめて実行すると失敗する場合があります（モジュール状態の汚染が原因）。

```bash
# 推奨: Lambda テストはファイル単位で別々に実行
poetry run pytest ../tests/lambda/test_quota_monitor.py -v       # ✅ すべて成功
poetry run pytest ../tests/lambda/test_metrics_aggregator.py -v  # ✅ すべて成功

# まとめて実行すると、共有されたモジュール状態により失敗することがあります
poetry run pytest ../tests/lambda/ -v  # ⚠️ 一部失敗する可能性

# CLI やその他のテストはまとめて実行しても問題ありません
poetry run pytest ../tests/cli/ -v          # ✅ 問題なし
poetry run pytest ../tests/integration/ -v  # ✅ 問題なし
```

**原因:** Lambda 関数がモジュール import 時に boto3 クライアントを作成します。複数のテストファイルが、異なるモック設定で同一 Lambda モジュールを import すると、モジュール状態が汚染されます。テストでは module スコープのフィクスチャで影響を最小化していますが、完全な分離には、テストファイル間でのより複雑なモジュール再読み込みが必要になります。

### 環境変数
テストスイートは boto3 エラー回避のため、AWS リージョンを自動設定します（`tests/conftest.py`）。

手動テスト／デバッグでは、以下の設定が必要になる場合があります。

```bash
# テスト用環境変数を設定
export AWS_DEFAULT_REGION=us-east-1
export AWS_REGION=us-east-1
export AWS_PROFILE=test-profile
```

### テストの独立性
テストは互いに独立しており、影響し合わないべきです。

- セットアップ／後片付けにフィクスチャを使用する
- 外部依存をモックする
- 作成したリソースはクリーンアップする

## 新しいテストの書き方

### 命名規則
- テストファイル: `test_<module_name>.py`
- テストクラス: `Test<ClassName>`
- テスト関数: `test_<description>`

### 基本的なテスト構造
```python
import pytest
from unittest.mock import Mock, patch

class TestMyFeature:
    @pytest.fixture(autouse=True)
    def setup(self):
        """各テスト前のセットアップ。"""
        # セットアップ処理をここに記述
        pass

    def test_feature_behavior(self):
        """特定の挙動をテストする。"""
        # Arrange
        # Act
        # Assert
        assert result == expected
```

### AWS サービスのモック
```python
@patch("boto3.client")
def test_aws_operation(mock_client):
    """AWS クライアントをモックしてテストする。"""
    mock_client.return_value.operation.return_value = {"Result": "Success"}
    # テストコードをここに記述
```

## CI/CD 連携

継続的インテグレーションでは、以下を使用してください。

```bash
# CI 向け出力（カバレッジ付き）
poetry run pytest ../tests --junitxml=test-results.xml --cov=claude_code_with_bedrock --cov-report=xml

# CI 向け厳格モード（警告をエラー扱い）
poetry run pytest ../tests --strict-markers -W error
```

## サポート

テスト関連の問題がある場合：

1. テスト出力の詳細なエラーメッセージを確認する
2. デバッグ情報を最大化するため `-xvs` フラグで実行する
3. テストフィクスチャとモックが正しいか確認する
4. `poetry install` で依存関係がすべてインストールされていることを確認する
