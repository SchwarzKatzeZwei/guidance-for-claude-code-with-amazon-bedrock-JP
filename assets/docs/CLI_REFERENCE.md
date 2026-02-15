# Claude Code with Bedrock - CLI リファレンス

本ドキュメントは、`ccwb`（Claude Code with Bedrock）の全コマンドを網羅したリファレンスです。

## 目次

- [Claude Code with Bedrock - CLI リファレンス](#claude-code-with-bedrock---cli-リファレンス)
  - [目次](#目次)
  - [概要](#概要)
  - [インストール](#インストール)
  - [コマンドリファレンス](#コマンドリファレンス)
    - [`init` - デプロイ設定](#init---デプロイ設定)
    - [`deploy` - インフラのデプロイ](#deploy---インフラのデプロイ)
    - [`test` - パッケージのテスト](#test---パッケージのテスト)
    - [`package` - 配布物の作成](#package---配布物の作成)
    - [`builds` - CodeBuild ビルドの一覧／管理](#builds---codebuild-ビルドの一覧管理)
    - [`distribute` - 配布 URL の作成](#distribute---配布-url-の作成)
    - [`status` - デプロイ状態の確認](#status---デプロイ状態の確認)
    - [`cleanup` - インストール済みコンポーネントの削除](#cleanup---インストール済みコンポーネントの削除)
  - [クォータ管理](#クォータ管理)
    - [`quota set-user` - ユーザーのクォータ設定](#quota-set-user---ユーザーのクォータ設定)
    - [`quota set-group` - グループのクォータ設定](#quota-set-group---グループのクォータ設定)
    - [`quota set-default` - デフォルトクォータ設定](#quota-set-default---デフォルトクォータ設定)
    - [`quota list` - ポリシー一覧](#quota-list---ポリシー一覧)
    - [`quota delete` - ポリシー削除](#quota-delete---ポリシー削除)
    - [`quota show` - 有効クォータ表示](#quota-show---有効クォータ表示)
    - [`quota usage` - 使用量表示](#quota-usage---使用量表示)
    - [`quota unblock` - ユーザーのブロック解除](#quota-unblock---ユーザーのブロック解除)
    - [`quota export` - ポリシーのエクスポート](#quota-export---ポリシーのエクスポート)
    - [`quota import` - ポリシーのインポート](#quota-import---ポリシーのインポート)
  - [プロファイル管理](#プロファイル管理)
    - [`context list` - 全プロファイル一覧](#context-list---全プロファイル一覧)
    - [`context current` - アクティブプロファイル表示](#context-current---アクティブプロファイル表示)
    - [`context use` - アクティブプロファイル切り替え](#context-use---アクティブプロファイル切り替え)
    - [`context show` - プロファイル詳細表示](#context-show---プロファイル詳細表示)
    - [`config validate` - プロファイル設定の検証](#config-validate---プロファイル設定の検証)
    - [`config export` - プロファイル設定のエクスポート](#config-export---プロファイル設定のエクスポート)
    - [`config import` - プロファイル設定のインポート](#config-import---プロファイル設定のインポート)
    - [`destroy` - インフラ削除](#destroy---インフラ削除)

## 概要

Claude Code with Bedrock CLI（`ccwb`）は、IT 管理者が次を行うためのコマンドを提供します。

- OIDC 認証の設定
- AWS インフラのデプロイ
- 配布パッケージの作成
- デプロイメントの管理

## インストール

```bash
# リポジトリをクローン
git clone https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock.git
cd guidance-for-claude-code-with-amazon-bedrock/source

# 依存関係をインストール
poetry install

# poetry 経由でコマンド実行
poetry run ccwb <command>
```

## コマンドリファレンス

### `init` - デプロイ設定

Claude Code デプロイの設定を作成または更新します。

```bash
poetry run ccwb init [options]
```

**オプション:**

- `--profile <name>` - 設定プロファイル名（任意。未指定の場合はプロンプト表示）

**内容（何をするか）:**

- 前提条件チェック（AWS CLI、認証情報、Python バージョン）
- OIDC プロバイダー設定の入力
- 認証方式の選択プロンプト:
  - Direct IAM: IAM OIDC Provider によるフェデレーション
  - Cognito: Cognito Identity Pool によるフェデレーション
- AWS 設定（リージョン、スタック名）の構成
- Claude モデル選択（Opus / Sonnet / Haiku）のプロンプト
- クロスリージョン推論プロファイル（US / Europe / APAC）の設定
- モデル推論に用いるソースリージョン選択のプロンプト
- モニタリング（監視）オプションの設定
- クォータ監視の設定:
  - ユーザーごとの月次トークン上限
  - バーストバッファ付き日次トークン上限（月次から自動算出）
  - 日次／月次の上限に対する強制モード（alert / block）
  - クォータ再チェック間隔（キャッシュ済み認証情報でクォータを再検証する頻度）
- Windows ビルド（AWS CodeBuild）対応のプロンプト（任意）
- 設定をプロジェクトディレクトリの `.ccwb-config/config.json` に保存

**注:** このコマンドは設定の作成のみです。AWS リソース作成には `deploy` を使用してください。

### `deploy` - インフラのデプロイ

認証およびモニタリングの CloudFormation スタックをデプロイします。

```bash
poetry run ccwb deploy [stack] [options]
```

**引数:**

- `stack` - デプロイ対象スタックの指定: auth / networking / monitoring / dashboard / analytics / quota（任意）

**オプション:**

- `--profile <name>` - 使用する設定プロファイル（既定: "default"）
- `--dry-run` - 実行せずにデプロイ内容のみ表示
- `--show-commands` - 実行の代わりに AWS CLI コマンドを表示

**内容（何をするか）:**

- 認証インフラ（IAM OIDC Provider または Cognito Identity Pool）をデプロイ
- Bedrock アクセス用の IAM ロール／ポリシーを作成
- （有効な場合）モニタリング基盤をデプロイ
- 認証リソース識別子を含むスタック出力を表示

**デプロイされるスタック:**

1. **auth** - 認証インフラと IAM ロール（常に必須）
2. **networking** - モニタリング用 VPC／ネットワーキング（任意）
3. **monitoring** - ECS Fargate 上の OpenTelemetry collector（任意）
4. **dashboard** - 利用状況メトリクス用 CloudWatch ダッシュボード（任意）
5. **analytics** - 分析用 Kinesis Firehose と Athena（任意）
6. **quota** - ユーザー別トークンクォータ監視／アラート（任意、dashboard が必要）
7. **codebuild** - Windows バイナリ生成用 AWS CodeBuild（任意、init で有効化した場合のみ）

**例:**

```bash
# 設定されたスタックをすべてデプロイ
poetry run ccwb deploy

# 認証のみデプロイ
poetry run ccwb deploy auth

# クォータ監視をデプロイ（事前に dashboard スタックが必要）
poetry run ccwb deploy quota

# 実行せずコマンドだけ表示
poetry run ccwb deploy --show-commands

# dry-run でデプロイ予定を確認
poetry run ccwb deploy --dry-run
```

> **注**: クォータ監視は dashboard スタックの事前デプロイが必要です。詳細は [Quota Monitoring Guide](QUOTA_MONITORING.md) を参照してください。

#### `ccwb deploy` と `ccwb deploy quota` の使い分け

| コマンド | 利用場面 |
|---------|----------|
| `ccwb deploy` | 初期セットアップ（有効化されたスタックを一括デプロイ。quota も有効なら含む） |
| `ccwb deploy quota` | クォータ設定の更新、後からの有効化、トラブルシュート |

**`ccwb deploy` が quota をデプロイする条件**: プロファイル内で `quota_monitoring_enabled=True`（`ccwb init` で設定）になっている場合、`ccwb deploy` はフルデプロイの一部として quota スタックを自動デプロイします。

**`ccwb deploy quota` を使う場面**:
- 他スタックを再デプロイせずにクォータ設定だけ更新したい
- 初回は quota なしでデプロイし、後から追加したい
- quota スタックだけを再デプロイして切り分けたい
- 段階的デプロイ（明示的制御）が必要な組織要件がある

### `test` - パッケージのテスト

エンドユーザー体験に近い形で、配布パッケージをテストします。

```bash
poetry run ccwb test [options]
```

**オプション:**

- `--profile, -p <name>` - テスト対象プロファイル名（既定: アクティブプロファイル）
- `--full` - 許可された全リージョンをテスト（既定: 代表 3 リージョンのみ）
- `--quota-only` - クォータ監視テストのみ実行（API／ポリシー／使用量の取得）
- `--quota-api <endpoint>` - クォータ API をテスト（任意でエンドポイント上書き）

**内容（何をするか）:**

- `dist/{profile}/{timestamp}/` からプロファイルの最新パッケージを検索
- パッケージ内容（バイナリ、設定、OTEL helper）を検証
- credential process バイナリの実行をテスト
- 認証および IAM ロール引き受け（assume）をテスト
- 設定されたリージョンで Bedrock API アクセスをテスト
- 推論プロファイル（inference profile）の可用性をテスト
- （有効な場合）クォータ監視 API をテスト

**クォータテスト（`--quota-only`）:**

`--quota-only` を使用すると、クォータ監視の包括的テストを実行します。

1. **Quota Config** - クォータ設定がすべて揃っていることを検証
2. **Quota API** - JWT 認証付きで `/check` エンドポイントをテスト
3. **Create Policy** - DynamoDB にテスト用ユーザーポリシーを作成
4. **List Policies** - 作成したポリシーが一覧に出ることを検証
5. **Resolve Quota** - ユーザーに対するポリシー解決をテスト
6. **Delete Policy** - テスト用ポリシーを削除して後片付け

**例:**

```bash
# 標準テストを実行
poetry run ccwb test

# クォータ監視テストのみ実行（クォータ検証の最短ルート）
poetry run ccwb test --quota-only

# ステージングのクォータ API エンドポイントでテスト
poetry run ccwb test --quota-only --quota-api https://staging-api.example.com/prod

# カスタムクォータエンドポイント付きで全テストを実行
poetry run ccwb test --quota-api https://my-api.execute-api.us-east-1.amazonaws.com/prod
```

**注:** API テストは既定で実行され、Bedrock への実呼び出しを行います（最小コストで約 ~$0.001）。

### `package` - 配布物の作成

エンドユーザー向け配布パッケージを作成します。

```bash
poetry run ccwb package [options]
```

**オプション:**

- `--target-platform <platform>` - バイナリのターゲットプラットフォーム（既定: "all"）
  - `macos` - 現在の macOS アーキテクチャ向けにビルド
  - `macos-arm64` - Apple Silicon Mac 向け
  - `macos-intel` - Intel Mac 向け（ARM Mac では Rosetta を使用）
  - `linux` - Linux（ネイティブ、現在のアーキテクチャ）
  - `linux-x64` - Docker により Linux x64 をビルド
  - `linux-arm64` - Docker により Linux ARM64 をビルド
  - `windows` - Windows（CodeBuild を使用。init 中に有効化が必要）
  - `all` - 利用可能な全プラットフォーム向けにビルド
- `--distribute` - パッケージをアップロードし、配布 URL を生成
- `--expires-hours <hours>` - 配布 URL の有効期限（`--distribute` 使用時）[既定: "48"]
- `--profile <name>` - 使用する設定プロファイル [既定: "default"]

**内容（何をするか）:**

- 認証コードから Nuitka 実行ファイルをビルド
- 次を含む設定ファイルを作成：
  - OIDC プロバイダー設定
  - デプロイ済みスタックから取得した Identity Pool ID
  - 認証情報の保存方式（keyring または session）
  - 選択した Claude モデルとクロスリージョンプロファイル
  - モデル推論のソースリージョン
- インストーラスクリプト生成（Unix は install.sh、Windows は install.bat）
- ユーザー向けドキュメント生成
- （任意）S3 へアップロードし事前署名 URL を生成（`--distribute` 使用時）

**プラットフォーム対応（ハイブリッドビルドシステム）:**

- **macOS**: PyInstaller によるアーキテクチャ別ビルド
  - ARM64: Apple Silicon Mac 上でネイティブビルド（すべての Mac で動作）
  - Intel: **任意** — ARM Mac 上で x86_64 の Python 環境が必要
  - Universal: 両アーキテクチャの Python ライブラリが必要（現状は自動化されていません）
- **Linux**: Docker コンテナ内で PyInstaller を使用
  - x64: `linux/amd64` Docker プラットフォームを使用
  - ARM64: `linux/arm64` Docker プラットフォームを使用
  - Docker Desktop がアーキテクチャエミュレーションを自動処理
- **Windows**: AWS CodeBuild 経由の Nuitka（init 中に有効化した場合）
  - 自動ビルドは 12～15 分
  - `init` 中に CodeBuild を有効化している必要あり
  - CodeBuild が無効ならスキップ

**Intel Mac ビルド環境のセットアップ（任意）:**

Apple Silicon Mac 上で Intel 向けビルドを有効化する手順（任意）：

```bash
# 手順 1: x86_64 Homebrew をインストール（未導入の場合）
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 手順 2: x86_64 Python をインストール
arch -x86_64 /usr/local/bin/brew install python@3.12

# 手順 3: x86_64 仮想環境を作成
arch -x86_64 /usr/local/bin/python3.12 -m venv ~/venv-x86

# 手順 4: 必要パッケージをインストール
arch -x86_64 ~/venv-x86/bin/pip install pyinstaller boto3 keyring
```

**Intel 環境が未セットアップの場合の挙動:**

- `--target-platform=all`: Intel ビルドは注記付きでスキップし、他プラットフォームをビルド
- `--target-platform=macos-intel`: 任意セットアップ手順を表示してビルドをスキップ
- Intel バイナリがなくてもパッケージ処理は成功
- ARM64 バイナリはすべての Mac ユーザー（Intel / Apple Silicon）に配布可能

**グレースフルなフォールバック挙動:**

package コマンドは、任意コンポーネントが欠けていても可能な限り処理を継続する設計です。

- **Intel Mac ビルド**: ARM Mac 上で x86_64 Python 環境がなければスキップ
- **Windows ビルド**: `init` 中に CodeBuild が有効化されていなければスキップ
- **Linux ビルド**: Docker が利用できなければスキップ
- package コマンドが成功するには、**少なくとも 1 プラットフォームのビルドが成功**する必要があります

これにより、任意プラットフォームが利用不能でもパッケージ作成は成立します。

**出力ファイル:**

- `credential-process-<platform>` - 認証実行ファイル
  - `credential-process-macos-arm64` - macOS Apple Silicon
  - `credential-process-macos-intel` - macOS Intel
  - `credential-process-linux-x64` - Linux x64
  - `credential-process-linux-arm64` - Linux ARM64
  - `credential-process-windows.exe` - Windows x64
- `otel-helper-<platform>` - OTEL helper（モニタリング有効時）
- `config.json` - 設定
- `install.sh` - Unix インストーラ（アーキテクチャ自動判別）
- `install.bat` - Windows インストーラ
- `README.md` - インストール手順
- Claude Code のテレメトリ設定を含む（モニタリング有効時）
- モデル選択用環境変数を設定（ANTHROPIC_MODEL、ANTHROPIC_SMALL_FAST_MODEL）

**出力構成:**

```
dist/
├── credential-process-macos-arm64     # macOS ARM64 実行ファイル
├── credential-process-macos-intel     # macOS Intel 実行ファイル
├── credential-process-linux-x64       # Linux x64 実行ファイル
├── credential-process-linux-arm64     # Linux ARM64 実行ファイル
├── credential-process-windows.exe     # Windows x64 実行ファイル
├── otel-helper-macos-arm64            # macOS ARM64 OTEL helper
├── otel-helper-macos-intel            # macOS Intel OTEL helper
├── otel-helper-linux-x64              # Linux x64 OTEL helper
├── otel-helper-linux-arm64            # Linux ARM64 OTEL helper
├── otel-helper-windows.exe            # Windows OTEL helper
├── config.json                        # 設定
├── install.sh                         # Unix インストーラ（アーキテクチャ自動判別）
├── install.bat                        # Windows インストーラ
├── README.md                          # ユーザー手順
└── .claude/
    └── settings.json                  # テレメトリ設定（任意）
```

### `builds` - CodeBuild ビルドの一覧／管理

Windows バイナリの最近のビルドと状態を表示します。

```bash
poetry run ccwb builds [options]
```

**オプション:**

- `--profile <name>` - 使用する設定プロファイル（既定: アクティブプロファイル）
- `--limit <n>` - 表示するビルド数（既定: "10"）
- `--project <name>` - CodeBuild プロジェクト名（既定: 自動検出）
- `--status <id>` - 特定ビルド ID の状態を確認
- `--download` - 完了した Windows 成果物を dist フォルダへダウンロード

**内容（何をするか）:**

- Windows バイナリ向け CodeBuild の最近のビルドを一覧表示
- ビルド状態、所要時間、完了時刻を表示
- 完全なビルドログ確認用のコンソールリンクを提示
- 進行中ビルドの監視
- アクティブプロファイル、または指定プロファイルを用いてプロジェクトを検出

**注:** このコマンドは `init` 中に CodeBuild を有効化している必要があります。無効化していた場合は `init` を再実行し、Windows ビルド対応を有効化してください。

**例:**

```bash
# アクティブプロファイルのビルドを一覧表示
poetry run ccwb builds

# 特定プロファイルのビルドを一覧表示
poetry run ccwb builds --profile production

# 特定ビルドの状態を確認
poetry run ccwb builds --status abc12345

# 最新ビルドの状態を確認して成果物をダウンロード
poetry run ccwb builds --status latest --download

# 直近 20 件を表示
poetry run ccwb builds --limit 20
```

**出力例:**

```
Recent Windows Builds

| Build ID | Status | Started | Duration |
|----------|--------|---------|----------|
| project:abc123 | SUCCEEDED | 2024-08-26 10:15 | 12m 34s |
| project:def456 | IN_PROGRESS | 2024-08-26 10:30 | - |
```

### `distribute` - 配布 URL の作成

事前署名付き S3 URL または認証付きランディングページを用いて、ビルド済みパッケージをアップロードし配布します。

```bash
poetry run ccwb distribute [options]
```

**オプション:**

- `--expires-hours <hours>` - URL の有効期限（時間）。(1-168) [既定: "48"]
- `--get-latest` - 最新の配布 URL を取得（presigned-s3 のみ）
- `--profile <name>` - 使用する設定プロファイル（未指定の場合はアクティブプロファイル）
- `--package-path <path>` - パッケージディレクトリへのパス [既定: "dist"]
- `--build-profile <name>` - プロファイル名でビルドを選択
- `--timestamp <timestamp>` - タイムスタンプでビルドを選択（形式: YYYY-MM-DD-HHMMSS）
- `--latest` - ウィザードなしで最新ビルドを自動選択
- `--allowed-ips <ranges>` - アクセス制御用の IP 範囲（カンマ区切り）（presigned-s3 のみ）
- `--show-qr` - URL の QR コードを表示（qrcode ライブラリが必要）

**内容（何をするか）:**

挙動は、設定済みの配布方式に依存します。

**事前署名付き S3 URL（シンプル）:**
- パッケージを S3 バケットにアップロード
- 安全な事前署名 URL を生成（既定 48 時間）
- チーム共有のため Parameter Store に URL を保存
- メール／Slack で URL を共有
- ダウンロードに認証は不要

**ランディングページ（エンタープライズ）:**
- プラットフォーム別パッケージ（windows/linux/mac/all-platforms）をアップロード
- S3 メタデータ（プロファイル、タイムスタンプ、リリース日）を更新
- 認証付きアクセスのためのランディングページ URL を提供
- ユーザーは IdP（Okta/Azure/Auth0/Cognito）で認証
- プラットフォーム自動判別と推奨提示

**配布ワークフロー:**

1. パッケージをビルド: `poetry run ccwb package`
2. アップロード／配布: `poetry run ccwb distribute`
3. **presigned-s3**: 生成された URL を開発者へ共有
4. **landing-page**: ユーザーをランディングページ URL に誘導

**例:**

```bash
# 最新ビルドを配布（対話的にビルド選択）
poetry run ccwb distribute

# 最新ビルドを自動配布（ウィザードをスキップ）
poetry run ccwb distribute --latest

# タイムスタンプ指定で配布
poetry run ccwb distribute --timestamp 2024-11-14-083022

# 有効期限を変更して配布（presigned-s3 のみ）
poetry run ccwb distribute --expires-hours=72

# 再アップロードせず既存 URL を取得（presigned-s3 のみ）
poetry run ccwb distribute --get-latest

# URL を QR コードで表示（モバイル共有向け）
poetry run ccwb distribute --show-qr
```

**ビルド選択:**

`dist/` 内に複数ビルドがある場合、コマンドは次を行います。
1. プロファイル／タイムスタンプで整理されたビルドをスキャン
2. 配布対象のビルドを選ぶ対話ウィザードを表示
3. ビルド日時、サイズ、含まれるプラットフォームを表示
4. プロファイル名またはタイムスタンプで選択可能

`--latest` を使うとウィザードをスキップし、最新ビルドを自動選択します。

**プラットフォーム別アップロード（ランディングページ）:**

landing-page 配布の場合、パッケージはプラットフォーム別に整理されます。
- `packages/windows/latest.zip` - Windows パッケージ
- `packages/linux/latest.zip` - Linux パッケージ
- `packages/mac/latest.zip` - macOS パッケージ
- `packages/all-platforms/latest.zip` - 全プラットフォームまとめ

ランディングページはユーザーの OS を自動判別し、適切なパッケージを推奨します。

### `status` - デプロイ状態の確認

現在のデプロイ状態と設定を表示します。

```bash
poetry run ccwb status [options]
```

**オプション:**

- `--profile <name>` - 確認対象プロファイル（未指定の場合はアクティブプロファイル）
- `--json` - JSON 形式で出力
- `--detailed` - 詳細情報を表示

**内容（何をするか）:**

- 次を含む現在の設定を表示:
  - 設定プロファイル名と AWS プロファイル名
  - OIDC プロバイダーとクライアント ID
  - 選択した Claude モデルとクロスリージョンプロファイル
  - モデル推論のソースリージョン
  - 分析／モニタリングの有効化状態
- CloudFormation スタックの状態を確認
- Identity Pool 情報を表示
- モニタリング設定とエンドポイントを表示

### `cleanup` - インストール済みコンポーネントの削除

test コマンドまたは手動インストールで導入されたコンポーネントを削除します。

```bash
poetry run ccwb cleanup [options]
```

**オプション:**

- `--force` - 確認プロンプトをスキップ
- `--profile <name>` - 削除対象の AWS プロファイル名（既定: "ClaudeCode"）

**内容（何をするか）:**

- `~/claude-code-with-bedrock/` ディレクトリを削除
- `~/.aws/config` から AWS プロファイルを削除
- `~/.claude/settings.json` から Claude 設定を削除
- 実行前に削除対象を表示

**用途:**

- テスト後のクリーンアップ
- 失敗したインストールの除去
- 新しい設定でやり直すための初期化

## クォータ管理

ユーザー単位およびグループ単位のトークンクォータを管理するコマンド群です。`init` 中にクォータ監視を有効化している必要があります。

アーキテクチャと設定の詳細は [QUOTA_MONITORING.md](QUOTA_MONITORING.md) を参照してください。

### `quota set-user` - ユーザーのクォータ設定

特定ユーザーのクォータポリシーを設定します。

```bash
poetry run ccwb quota set-user <email> [options]
```

**引数:**
- `<email>` - ユーザーのメールアドレス

**オプション:**
- `--monthly-limit, -m <tokens>` - 月次トークン上限（K/M/B サフィックス対応: 10M = 10,000,000）
- `--daily-limit, -d <tokens>` - 日次トークン上限（任意）
- `--enforcement, -e <mode>` - 強制モード: `alert`（監視のみ）または `block`（アクセス拒否）
- `--disabled` - 無効状態でポリシーを作成
- `--profile, -p <name>` - 設定プロファイル

**例:**
```bash
poetry run ccwb quota set-user alice@example.com -m 5M -e block
```

### `quota set-group` - グループのクォータ設定

グループのクォータポリシーを設定します（グループ内の全ユーザーに適用）。

```bash
poetry run ccwb quota set-group <group> [options]
```

**引数:**
- `<group>` - グループ名（OIDC の groups クレーム由来）

**オプション:**
- `set-user` と同一

**例:**
```bash
poetry run ccwb quota set-group engineering -m 20M -d 1M -e alert
```

### `quota set-default` - デフォルトクォータ設定

ユーザー／グループに個別ポリシーがない場合に適用されるデフォルトのクォータポリシーを設定します。

```bash
poetry run ccwb quota set-default [options]
```

**オプション:**
- `set-user` と同一

**例:**
```bash
poetry run ccwb quota set-default -m 225M -e alert
```

### `quota list` - ポリシー一覧

すべてのクォータポリシーを一覧表示します。

```bash
poetry run ccwb quota list [options]
```

**オプション:**
- `--type <type>` - 種別でフィルタ: `user` / `group` / `default`
- `--profile, -p <name>` - 設定プロファイル

### `quota delete` - ポリシー削除

クォータポリシーを削除します。

```bash
poetry run ccwb quota delete <type> <identifier> [options]
```

**引数:**
- `<type>` - ポリシー種別: `user` / `group` / `default`
- `<identifier>` - user の場合はメール、group の場合はグループ名、default の場合は "default"

**オプション:**
- `--profile, -p <name>` - 設定プロファイル

**例:**
```bash
poetry run ccwb quota delete user alice@example.com
```

### `quota show` - 有効クォータ表示

ユーザーに対する有効クォータポリシーを表示します（優先度は user > group > default）。

```bash
poetry run ccwb quota show <email> [options]
```

**引数:**
- `<email>` - ユーザーのメールアドレス

**オプション:**
- `--profile, -p <name>` - 設定プロファイル

### `quota usage` - 使用量表示

ユーザーの現在使用量とクォータ上限に対する状況を表示します。

```bash
poetry run ccwb quota usage <email> [options]
```

**引数:**
- `<email>` - ユーザーのメールアドレス

**オプション:**
- `--profile, -p <name>` - 設定プロファイル

### `quota unblock` - ユーザーのブロック解除

クォータ超過によりブロックされたユーザーを一時的に解除します。

```bash
poetry run ccwb quota unblock <email> [options]
```

**引数:**
- `<email>` - ユーザーのメールアドレス

**オプション:**
- `--duration <time>` - 解除期間: `24h` / `7d` / `until-reset` または任意（例: `48h`、`3d`）
- `--reason <text>` - 解除理由（監査証跡用）
- `--profile, -p <name>` - 設定プロファイル

**例:**
```bash
poetry run ccwb quota unblock alice@example.com --duration 24h --reason "Emergency project deadline"
```

### `quota export` - ポリシーのエクスポート

バックアップ、移行、監査のために、クォータポリシーを JSON または CSV にエクスポートします。

```bash
poetry run ccwb quota export <file> [options]
```

**引数:**
- `<file>` - 出力ファイルパス（.json または .csv）

**オプション:**
- `--type, -t <type>` - ポリシー種別でフィルタ: `user` / `group` / `default`
- `--stdout` - ファイルではなく stdout に出力
- `--profile, -p <name>` - 設定プロファイル

**例:**
```bash
# すべてのポリシーを JSON でエクスポート
poetry run ccwb quota export policies.json

# スプレッドシート編集のために CSV でエクスポート
poetry run ccwb quota export policies.csv

# ユーザーポリシーのみエクスポート
poetry run ccwb quota export users.json --type user

# stdout へ出力（パイプ用）
poetry run ccwb quota export --stdout > backup.json
```

**JSON 出力形式:**
```json
{
  "version": "1.0",
  "exported_at": "2025-11-29T10:30:00Z",
  "policies": [
    {
      "type": "user",
      "identifier": "alice@example.com",
      "monthly_token_limit": "300M",
      "daily_token_limit": "15M",
      "enforcement_mode": "alert",
      "enabled": true
    }
  ]
}
```

**CSV 出力形式:**
```csv
type,identifier,monthly_token_limit,daily_token_limit,enforcement_mode,enabled
user,alice@example.com,300M,15M,alert,true
group,engineering,500M,25M,block,true
default,default,225M,8M,alert,true
```

### `quota import` - ポリシーのインポート

JSON または CSV からクォータポリシーをインポートします。競合処理を含む一括作成をサポートします。

```bash
poetry run ccwb quota import <file> [options]
```

**引数:**
- `<file>` - 入力ファイルパス（.json または .csv）

**オプション:**
- `--skip-existing` - 既存ポリシーはスキップ
- `--update` - 既存ポリシーを更新（upsert）
- `--dry-run` - 適用せず変更内容をプレビュー
- `--type, -t <type>` - 指定種別のみインポート: `user` / `group` / `default`
- `--auto-daily` - `daily_token_limit` がないポリシーの分を日次上限として自動算出
- `--burst <percent>` - 自動算出のバーストバッファ率（既定: 10）
- `--profile, -p <name>` - 設定プロファイル

**例:**
```bash
# JSON からインポート（既存はスキップ）
poetry run ccwb quota import policies.json --skip-existing

# CSV からインポート（既存は更新）
poetry run ccwb quota import policies.csv --update

# 変更を適用せずプレビュー
poetry run ccwb quota import policies.json --dry-run

# user のみインポート
poetry run ccwb quota import all-policies.csv --type user --update

# バースト 15% で日次上限を自動算出
poetry run ccwb quota import users.csv --auto-daily --burst 15
```

**出力例:**
```
✓ Created: alice@example.com (user) - 300M
✓ Created: bob@example.com (user) - 200M
⚠ Skipped: engineering (group) - already exists
✓ Updated: ml-team (group) - 1B

Import Summary
  Created: 2
  Updated: 1
  Skipped: 1
  Errors:  0
```

**CSV 必須列:**
- `type` - ポリシー種別: `user` / `group` / `default`
- `identifier` - user メール、group 名、または `default`
- `monthly_token_limit` - 月次上限（K/M/B サフィックス対応。例: `300M`）

**CSV 任意列:**
- `daily_token_limit` - 日次上限（`--auto-daily` 時に自動算出可能）
- `enforcement_mode` - `alert`（既定）または `block`
- `enabled` - `true`（既定）または `false`

## プロファイル管理

以下は、複数のデプロイプロファイル（v2.0+）を管理するコマンドです。プロファイルにより、1 台の端末から異なる AWS アカウント／リージョン／組織の設定を管理できます。

### `context list` - 全プロファイル一覧

利用可能なすべてのプロファイルを、アクティブプロファイルの表示付きで一覧表示します。

```bash
poetry run ccwb context list
```

**内容（何をするか）:**

- `~/.ccwb/profiles/` 配下のプロファイルを一覧表示
- プロファイル名、AWS リージョン、スタック名を表示
- 現在アクティブなプロファイルを強調表示
- プロファイル数を表示

**出力例:**

```
Available Profiles:
  * production (us-east-1, stack: claude-code-prod)
    development (us-west-2, stack: claude-code-dev)
    eu-deployment (eu-west-1, stack: claude-code-eu)

Active profile: production
Total profiles: 3
```

### `context current` - アクティブプロファイル表示

現在アクティブなプロファイル名を表示します。

```bash
poetry run ccwb context current
```

**内容（何をするか）:**

- アクティブプロファイル名を表示
- アクティブプロファイルが未設定の場合はエラー終了

**出力例:**

```
Current profile: production
```

### `context use` - アクティブプロファイル切り替え

アクティブプロファイルを指定のものに切り替えます。

```bash
poetry run ccwb context use <profile-name>
```

**引数:**

- `profile-name` - 有効化するプロファイル名（必須）

**内容（何をするか）:**

- 指定プロファイルをアクティブに設定
- プロファイルが存在することを検証
- グローバル設定ファイルを更新

**例:**

```bash
# production に切り替え
poetry run ccwb context use production

# development に切り替え
poetry run ccwb context use development
```

### `context show` - プロファイル詳細表示

プロファイルの詳細設定を表示します。

```bash
poetry run ccwb context show [profile-name]
```

**引数:**

- `profile-name` - 表示対象プロファイル（任意。既定はアクティブプロファイル）

**オプション:**

- `--json` - JSON 形式で出力

**内容（何をするか）:**

- 次を含むプロファイル設定全体を表示:
  - AWS リージョンとアカウント
  - OIDC プロバイダー設定
  - スタック名
  - モデル選択
  - モニタリング設定
- 機微値（クライアントシークレット）をマスク

**例:**

```bash
# アクティブプロファイルの詳細を表示
poetry run ccwb context show

# 特定プロファイルを表示
poetry run ccwb context show production

# JSON 形式で出力
poetry run ccwb context show --json
```

### `config validate` - プロファイル設定の検証

プロファイル設定の誤りを検証します。

```bash
poetry run ccwb config validate [profile-name|all]
```

**引数:**

- `profile-name` - 検証対象プロファイル（任意。既定はアクティブプロファイル）
- `all` - 全プロファイルを検証

**内容（何をするか）:**

- 必須フィールドの有無をチェック
- フィールド形式を検証（リージョン、スタック名、URL など）
- AWS 認証情報の存在を検証
- 修正提案付きで検証エラーを報告

**例:**

```bash
# アクティブプロファイルを検証
poetry run ccwb config validate

# 特定プロファイルを検証
poetry run ccwb config validate production

# 全プロファイルを検証
poetry run ccwb config validate all
```

### `config export` - プロファイル設定のエクスポート

プロファイル設定を（機微情報を除去した形で）ファイルにエクスポートします。

```bash
poetry run ccwb config export [profile-name] [options]
```

**引数:**

- `profile-name` - エクスポート対象プロファイル（任意。既定はアクティブプロファイル）

**オプション:**

- `--output <file>` - 出力ファイルパス（既定: `<profile-name>.json`）
- `--include-secrets` - 機微値を含める（非推奨）

**内容（何をするか）:**

- プロファイル設定を JSON にエクスポート
- 既定で機微値（クライアントシークレット）を除去
- 可搬性のある設定ファイルを作成

**例:**

```bash
# アクティブプロファイルをエクスポート（シークレット除去）
poetry run ccwb config export

# 特定プロファイルを任意パスにエクスポート
poetry run ccwb config export production --output prod-config.json

# シークレット込みでエクスポート（注意）
poetry run ccwb config export --include-secrets
```

### `config import` - プロファイル設定のインポート

ファイルからプロファイル設定をインポートします。

```bash
poetry run ccwb config import <file> [name]
```

**引数:**

- `file` - 設定ファイルパス（必須）
- `name` - インポート後のプロファイル名（任意。ファイル内の name を使用）

**オプション:**

- `--overwrite` - 既存プロファイルがある場合に上書き
- `--set-active` - インポート後にアクティブプロファイルに設定

**内容（何をするか）:**

- JSON ファイルからプロファイル設定をインポート
- インポート前に設定を検証
- `~/.ccwb/profiles/` に新規プロファイルを作成
- （任意）アクティブプロファイルに設定

**例:**

```bash
# 既定名でインポート
poetry run ccwb config import prod-config.json

# 任意名でインポート
poetry run ccwb config import config.json staging

# インポートしてアクティブに設定
poetry run ccwb config import config.json --set-active

# 既存プロファイルを上書き
poetry run ccwb config import config.json production --overwrite
```

### `destroy` - インフラ削除

デプロイ済み AWS インフラを削除します。

```bash
poetry run ccwb destroy [stack] [options]
```

**引数:**

- `stack` - 削除対象スタック: auth / networking / monitoring / dashboard / analytics（任意）

**オプション:**

- `--profile <name>` - 使用する設定プロファイル（未指定の場合はアクティブプロファイル）
- `--force` - 確認プロンプトをスキップ

**内容（何をするか）:**

- CloudFormation スタックを逆順で削除（analytics → dashboard → monitoring → networking → auth）
- 実行前に削除されるリソースを表示
- 手動削除が必要なもの（例: CloudWatch LogGroup）を警告

**注:** CloudWatch LogGroup など一部リソースは手動削除が必要な場合があります。
