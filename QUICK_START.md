# クイックスタートガイド

IT 管理者が Amazon Bedrock を用いて Claude Code を導入するための、完全なデプロイ手順書です。

**所要時間:** 初回デプロイ 2～3 時間  
**必要スキル:** IAM / CloudFormation の経験がある AWS 管理者

---

## 前提条件

### ソフトウェア要件

- Python 3.10～3.13
- Poetry（依存関係管理）
- AWS CLI v2
- Git

### AWS 要件

以下を作成できる適切な IAM 権限を持つ AWS アカウント：

- CloudFormation スタック
- IAM OIDC プロバイダー または Cognito Identity Pool
- IAM ロールおよびポリシー
- （任意）Amazon Elastic Container Service（Amazon ECS）タスクおよび Amazon CloudWatch ダッシュボード
- （任意）Amazon Athena、AWS Glue、AWS Lambda、Amazon Data Firehose リソース
- （任意）AWS CodeBuild
- 対象リージョンで Amazon Bedrock が有効化されていること

### OIDC プロバイダー要件

- 既存の OIDC ID プロバイダー（Okta、Azure AD、Auth0 など）
- OIDC アプリケーションを作成できること
- `http://localhost:8400/callback` へのリダイレクト URI をサポートしていること

### 対応 AWS リージョン

本ガイダンスは、次をサポートする任意の AWS リージョンにデプロイできます。

- IAM OIDC プロバイダー または Amazon Cognito Identity Pool
- Amazon Bedrock
- （任意）Amazon Elastic Container Service（Amazon ECS）タスクおよび Amazon CloudWatch ダッシュボード
- （任意）Amazon Athena、AWS Glue、AWS Lambda、Amazon Data Firehose リソース
- （任意）AWS CodeBuild

### クロスリージョン推論

Claude Code は、性能と可用性を最適化するために Amazon Bedrock のクロスリージョン推論を使用します。セットアップ時に次を選択できます。

- 使用したい Claude モデル（Opus / Sonnet / Haiku）
- 最適なリージョンルーティングのためのクロスリージョンプロファイル（US / Europe / APAC）
- そのプロファイル内で、モデル推論に用いる特定のソースリージョン

これにより、最良の応答時間と高い可用性を確保するために、複数の AWS リージョンにまたがってリクエストが自動的にルーティングされます。最新の Claude モデル（3.7 以降）では、アクセスのためにクロスリージョン推論が必要です。

---

## デプロイ手順

### 手順 1: リポジトリのクローンと依存関係のインストール

```bash
# リポジトリをクローン
git clone https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock
cd guidance-for-claude-code-with-amazon-bedrock/source

# 依存関係をインストール
poetry install
```

### 手順 2: 設定の初期化

対話型セットアップウィザードを実行します。

```bash
poetry run ccwb init
```

ウィザードでは次を案内します。

- OIDC プロバイダー設定（ドメイン、クライアント ID）
- インフラを構築する AWS リージョンの選択
- Amazon Bedrock のクロスリージョン推論設定
- 認証情報の保存方法（keyring またはセッションファイル）
- （任意）VPC 設定を含む監視（モニタリング）設定

#### プロファイルについて（v2.0+）

**プロファイルとは？**  
プロファイルにより、1 台の端末から複数のデプロイ（異なる AWS アカウント、リージョン、組織など）を管理できます。

**よくある利用例:**
- 本番アカウントと開発アカウント
- US と EU のリージョン別デプロイ
- 複数の顧客／テナント向けデプロイ

**プロファイル関連コマンド:**
- `ccwb context list` - すべてのプロファイルを表示
- `ccwb context use <name>` - プロファイルを切り替え
- `ccwb context show` - 現在アクティブなプロファイルの詳細を表示

コマンド一覧の全体は [CLI Reference](assets/docs/CLI_REFERENCE.md) を参照してください。

**v1.x からのアップグレード:**  
初回実行時に、プロファイル設定は `source/.ccwb-config/` から `~/.ccwb/` に自動移行されます。プロファイル名およびアクティブなプロファイルは保持されます。タイムスタンプ付きバックアップも自動作成されます。

### 手順 3: インフラのデプロイ

AWS CloudFormation スタックをデプロイします。

```bash
poetry run ccwb deploy
```

これにより、次の AWS リソースが作成されます。

**認証インフラ:**

- OIDC フェデレーション用の IAM OIDC プロバイダー または Amazon Cognito Identity Pool
- フェデレーテッドアクセスのための IAM 信頼関係
- 次の権限を付与するポリシーを持つ IAM ロール：
  - 指定リージョンにおける Bedrock モデル呼び出し
  - （モニタリング有効時）CloudWatch メトリクス

**（任意）モニタリング用インフラ:**

- VPC およびネットワークリソース（または既存 VPC との統合）
- OpenTelemetry Collector を実行する ECS Fargate クラスター
- OTLP 取り込み用 Application Load Balancer
- CloudWatch Log Group およびメトリクス
- 利用状況分析を網羅した CloudWatch ダッシュボード
- メトリクス集計・保存用 DynamoDB テーブル
- カスタムダッシュボードウィジェット用 Lambda 関数
- （分析有効時）メトリクスを S3 にストリーミングする Kinesis Data Firehose
- （分析有効時）収集メトリクスに対する SQL 分析用 Amazon Athena
- （分析有効時）長期保管用の S3 バケット

### 手順 4: 配布パッケージの作成

エンドユーザー向けのパッケージをビルドします。

```bash
# 全プラットフォーム向けにビルド（Windows ビルドはバックグラウンドで開始）
poetry run ccwb package --target-platform all

# Windows ビルド状況を確認（任意）
poetry run ccwb builds

# 準備ができたら配布用 URL を作成（任意）
poetry run ccwb distribute
```

**パッケージ作成ワークフロー:**

1. **ローカルビルド**: macOS/Linux の実行ファイルは PyInstaller によりローカルでビルド
2. **Windows ビルド**: Windows 実行ファイルは AWS CodeBuild を起動して生成（20 分以上）— `init` 時に CodeBuild を有効化している必要があります
3. **状況確認**: `poetry run ccwb builds` で進捗を監視
4. **配布作成**: `distribute` でアップロードし、事前署名 URL を生成

> **注**: Windows ビルドは任意で、`init` プロセス中に CodeBuild を有効化している必要があります。有効化していない場合、package コマンドは Windows ビルドをスキップし、他プラットフォームの処理を続行します。

`dist/` フォルダには次が含まれます。

- `credential-process-macos-arm64` - macOS ARM64 向け認証実行ファイル
- `credential-process-macos-intel` - macOS Intel 向け認証実行ファイル（ビルドした場合）
- `credential-process-windows.exe` - Windows 向け認証実行ファイル
- `credential-process-linux` - Linux 向け認証実行ファイル（Linux 上でビルドした場合）
- `config.json` - 埋め込み設定
- `install.sh` - Unix 系 OS 向けインストールスクリプト
- `install.bat` - Windows 向けインストールスクリプト
- `README.md` - ユーザー向け手順
- `.claude/settings.json` - Claude Code のテレメトリ設定（モニタリング有効時）
- `otel-helper-*` - 各プラットフォーム向け OTEL ヘルパー実行ファイル（モニタリング有効時）

パッケージビルダーの特長：

- 既定で macOS と Linux の両方のバイナリを自動ビルド
- macOS 上で実行する場合、Docker を用いて Linux のクロスプラットフォームビルドを実施
- JWT トークンからユーザー属性を抽出するための OTEL ヘルパーを同梱
- ユーザーのプラットフォームを自動判別する統合インストーラーを作成

### 手順 5: セットアップのテスト

正しく動作することを確認します。

```bash
poetry run ccwb test
```

このコマンドは次を実行します。

- エンドユーザーのインストール手順をシミュレーション
- OIDC 認証をテスト
- AWS 認証情報の取得を検証
- Amazon Bedrock へのアクセスを確認
- （任意）`--api` フラグで実際の API 呼び出しをテスト

### 手順 6: パッケージをユーザーへ配布

ユーザーに配布する方法は 3 つあります。配布方式は `ccwb init`（手順 2）中に設定します。

#### オプション 1: 手動共有

追加インフラは不要です。ビルドしたパッケージを直接共有します。

```bash
# dist ディレクトリへ移動
cd dist

# すべてのパッケージを zip 化
zip -r claude-code-packages.zip .

# メールや社内ファイル共有で配布
# ユーザーは展開後、install.sh（Unix）または install.bat（Windows）を実行
```

**適したケース:** 規模を問わず（自動化不要）

#### オプション 2: 事前署名付き S3 URL

期限付きの S3 URL による自動配布：

```bash
poetry run ccwb distribute
```

（既定で 48 時間の）事前署名 URL を生成し、メールやメッセージでユーザーに共有します。

**適したケース:** 認証不要で自動配布したい場合  
**セットアップ:** `ccwb init`（手順 2）で配布種別として「presigned-s3」を選択

#### オプション 3: 認証付きランディングページ

IdP 認証（SSO）付きのセルフサービスポータル：

```bash
# ランディングページ用インフラをデプロイ（手順 3 で未実施の場合）
poetry run ccwb deploy distribution

# パッケージをランディングページへアップロード
poetry run ccwb distribute
```

ユーザーはランディングページ URL にアクセスし、SSO で認証して、自分のプラットフォーム向けパッケージをダウンロードします。

**適したケース:** コンプライアンス／監査要件があるセルフサービスポータル  
**セットアップ:** `ccwb init`（手順 2）で「landing-page」を選択し、その後配布用インフラをデプロイ

詳細な機能比較と手順は [Distribution Comparison](assets/docs/distribution/comparison.md) を参照してください。

---

## プラットフォーム別ビルド

### ビルド要件

- **Windows**: Nuitka を用いた AWS CodeBuild（自動）
- **macOS**: PyInstaller によるアーキテクチャ別ビルド
  - ARM64: Apple Silicon Mac 上でネイティブビルド
  - Intel: 任意 — ARM Mac 上で x86_64 の Python 環境が必要
  - Universal: 両アーキテクチャの Python ライブラリが必要
- **Linux**: Docker + PyInstaller（非 Linux ホストでビルドする場合）

### （任意）Intel Mac 向けビルド

Intel Mac 向けビルドには、Apple Silicon Mac 上で x86_64 の Python 環境が必要です。

手順は [CLI Reference - Intel Mac Build Setup](assets/docs/CLI_REFERENCE.md#intel-mac-build-setup-optional) を参照してください。

未設定の場合、package コマンドは Intel 向けビルドをスキップし、他プラットフォームの処理を続行します。

---

## クリーンアップ

本ガイダンスを稼働させている間に発生する AWS サービスの費用は利用者の負担となります。不要になった場合は、インフラリソースが確実に削除されるようにしてください。

```bash
poetry run ccwb destroy
```

---

## トラブルシューティング

### 認証の問題

再認証を強制します。

```bash
~/claude-code-with-bedrock/credential-process --clear-cache
```

### ビルド失敗

Windows ビルド状況を確認します。

```bash
poetry run ccwb builds
```

### スタックのデプロイ問題

スタックの状態を表示します。

```bash
poetry run ccwb status
```

詳細は [Deployment Guide](assets/docs/DEPLOYMENT.md) を参照してください。

---

## 次のステップ

- [Architecture Deep Dive](assets/docs/ARCHITECTURE.md) - 技術アーキテクチャの詳細
- [Enable Monitoring](assets/docs/MONITORING.md) - OpenTelemetry モニタリングの設定
- [Setup Analytics](assets/docs/ANALYTICS.md) - S3 データレイクと Athena クエリの設定
- [CLI Reference](assets/docs/CLI_REFERENCE.md) - コマンドリファレンス全体
