# エンタープライズ デプロイガイド

本ガイドでは、組織全体に Claude Code の認証を展開する手順を IT 管理者向けに解説します。既存の ID プロバイダーを、安全な Amazon Bedrock アクセスのためのゲートウェイへと変換します。

> **前提条件**: 詳細な要件は [main README](../../README.md#prerequisites) を参照してください。AWS の管理者権限、OIDC ID プロバイダー、Poetry を導入した Python 環境が必要です。

## デプロイプロセス

Claude Code 認証のデプロイは、4 つの主要フェーズで構成されます。ID プロバイダーの設定、AWS インフラのデプロイ、配布パッケージの作成、ユーザーサポートです。各フェーズは前フェーズを土台として積み上がり、エンドユーザーにとって透過的な完全な認証ソリューションを構築します。

## フェーズ 1: ID プロバイダーの設定

まずは組織の ID プロバイダーの管理コンソールから始めます。Okta、Azure AD、Auth0 のいずれを使っていても、Claude Code の認証ゲートウェイとして機能する新しいアプリケーションを作成します。

プロバイダーの管理コンソールにログインし、アプリケーション作成セクションへ移動します。OIDC の用語で「Native Application」と呼ばれる種類のアプリを作ります。これは、ユーザーが Web サーバーではなくローカル端末から認証することをプロバイダーに伝えるものです。ログイン時にユーザーが認識できるよう、「Claude Code Authentication」や「Amazon Bedrock CLI Access」など分かりやすい名前を付けてください。

重要なのは、OAuth2 フローの特定パラメータを正しく設定することです。「Authorization Code」と「Refresh Token」のグラントタイプを有効化してください。これにより安全な認証とトークン更新が可能になります。リダイレクト URI は **必ず** `http://localhost:8400/callback` にします。これはユーザーのログイン後に認証処理が戻ってくる先です。標準の OIDC スコープ `openid`、`profile`、`email` を要求してください。最も重要なのは、クライアントシークレット不要で安全性を提供する PKCE（Proof Key for Code Exchange）を有効化することです。

> **プロバイダー別ガイド**: 各 ID プロバイダー固有の詳細手順は、[Okta](providers/okta-setup.md)、[Azure AD](providers/microsoft-entra-id-setup.md)、[Auth0](providers/auth0-setup.md) のガイドを参照してください。

次に、誰にアクセスを許可するかを決めます。最もすっきりした方法は、「Claude Code Users」のような専用グループを作成し、そのグループをアプリケーションに割り当てることです。これによりアクセス制御を一元化できます。ユーザーをグループに追加すれば付与、削除すれば剥奪です。必要に応じて MFA やデバイストラストなど、組織の追加ポリシーも適用してください。

次へ進む前に、アプリ設定から次の 2 つの重要値を控えてください：プロバイダードメイン（例: `company.okta.com`、または `login.microsoftonline.com/{tenant-id}/v2.0`）と Client ID です。これらは AWS インフラのデプロイで必要になります。

## フェーズ 2: AWS インフラのデプロイ

ID プロバイダーの設定ができたら、組織の認証を Amazon Bedrock に橋渡しする AWS インフラをデプロイします。まずリポジトリをクローンし、デプロイツールをインストールします。

```bash
git clone https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock
cd guidance-for-claude-code-with-amazon-bedrock/source
poetry install
```

`ccwb`（Claude Code with Bedrock）CLI は、対話型ウィザードでデプロイを案内します。`poetry run ccwb init` を実行して開始してください。ウィザードは、最初に OIDC プロバイダーの詳細を求めます。先ほど控えたドメインと Client ID を入力してください。

次に、認証方式を選択します。組織要件に応じて、Direct IAM federation または Cognito Identity Pool のいずれかを選べます。どちらも安全な OIDC フェデレーションにより AWS 認証情報を提供します。

続いて Claude モデルとリージョンアクセスを設定します。利用可能な Claude モデル（Opus / Sonnet / Haiku）から選び、最適な性能のためにクロスリージョン推論プロファイル（US / Europe / APAC）を選択します。次に、選択したプロファイル内でモデル推論に利用するソースリージョンを選ぶよう求められます。最後に、認証インフラをデプロイするリージョン（通常は主要 AWS リージョン）を選び、任意のモニタリング設定を行います。モニタリングを有効化すると、OpenTelemetry により利用状況分析とコスト追跡が可能になります。

設定が完了したら、次でインフラをデプロイします。

```bash
poetry run ccwb deploy
```

この単一コマンドが複数の AWS リソース作成をオーケストレーションします。選択した認証方式に応じて、信頼関係を確立するために IAM OIDC Provider または Cognito Identity Pool を作成します。IAM ロールとポリシーは、Bedrock へのアクセスを必要最小限にスコープして付与します。モニタリングを有効化している場合は、OpenTelemetry collector を実行する ECS Fargate クラスターと CloudWatch ダッシュボードもデプロイします。

> **デプロイオプション**: さらに細かい制御が必要な場合は、特定スタックのデプロイや dry-run モードについて [CLI Reference](CLI_REFERENCE.md) を参照してください。

## フェーズ 3: 配布パッケージの作成

インフラのデプロイが完了したら、エンドユーザーがインストールするパッケージを作成します。

### マルチプラットフォーム ビルド対応

Claude Code は主要プラットフォームすべてのビルドに対応しています。

```bash
# 全プラットフォーム向けにビルド（推奨）
poetry run ccwb package --target-platform=all

# 特定プラットフォーム向けにビルド
poetry run ccwb package --target-platform=windows    # CodeBuild 経由の Windows
poetry run ccwb package --target-platform=macos      # 現在の macOS アーキテクチャ
poetry run ccwb package --target-platform=linux      # Docker 経由の Linux
```

**プラットフォーム別ビルド方式（ハイブリッド方式）:**

- **Windows**: AWS CodeBuild 経由の Nuitka
  - 高速実行と、アンチウイルスの誤検知最小化を目的に最適化
- **macOS**: PyInstaller によるアーキテクチャ別ビルド
  - ARM64: Apple Silicon Mac 上でネイティブビルド（Rosetta により Intel Mac でも動作）
  - Intel: **任意** — ARM Mac 上で x86_64 Python 環境が必要
  - Universal: 両アーキテクチャの Python ライブラリが必要
- **Linux x64/ARM64**: Docker コンテナ内の PyInstaller
  - Docker が利用可能なら両アーキテクチャを自動ビルド
  - Docker Desktop が Rosetta によるアーキテクチャエミュレーションを処理

**（任意）Intel Mac セットアップ**

Apple Silicon Mac 上で Intel バイナリをビルドするには x86_64 Python 環境が必要です。  
セットアップ手順は [CLI Reference](CLI_REFERENCE.md#intel-mac-build-setup-optional) を参照してください。

このセットアップがなくても、package コマンドは正常に完了するよう設計されています。

このコマンドはいくつかの操作を行います。まず、デプロイ済み CloudFormation スタックから Cognito Identity Pool ID を取得します。次に、macOS/Linux では PyInstaller、Windows では Nuitka により、Python の認証コードをスタンドアロン実行ファイルへコンパイルします。組織の設定（プロバイダードメイン、Client ID、インフラ詳細）は `config.json` に書き込まれ、実行ファイルは実行時にこれを読み取ります。

生成される `dist/` フォルダには、ユーザーが必要とするものがすべて入ります。

- プラットフォーム別実行ファイル（`credential-process-<platform>`）が OAuth2 認証フローを処理
- 設定ファイルに必要設定がすべて含まれる
- インテリジェントなインストーラスクリプト（Unix は `install.sh`、Windows は `install.bat`）が、ユーザーのアーキテクチャを判別し AWS プロファイルを自動設定
- モニタリング有効時は、OTEL helper 実行ファイルと、OpenTelemetry collector を指す Claude Code テレメトリ設定も同梱

### Windows ビルドシステム（任意）

Windows バイナリのビルドは、性能最適化のため AWS CodeBuild + Nuitka を使用します。Windows 対応は任意であり、`init` 時に設定します。

1. **init 中に有効化**: `poetry run ccwb init` 実行時に次のように尋ねられます。

   ```
   Enable Windows build support via AWS CodeBuild? (y/N)
   ```

   「yes」と答えた場合、`deploy` 実行時に CodeBuild スタックも自動デプロイされます。

2. **有効化されている場合**、次を実行すると Windows ビルドが自動的にトリガーされます。

   ```bash
   poetry run ccwb package --target-platform=all
   # または Windows のみ:
   poetry run ccwb package --target-platform=windows
   ```

3. **ビルド進捗の確認**:
   ```bash
   poetry run ccwb builds
   ```

**重要事項:**

- Windows ビルドは完全に任意です（なくてもパッケージは機能します）
- CodeBuild が有効化されていない場合、Windows ビルドは黙ってスキップされます
- Windows ビルドは 20 分以上かかります
- 初期セットアップ後に Windows ビルドを有効化したい場合は、`poetry run ccwb init` を再実行してください

## フェーズ 4: デプロイのテスト

ユーザーに配布する前に、パッケージが想定どおり動作することを十分に確認してください。CLI には、エンドユーザー体験をそのまま再現する包括的なテストコマンドがあります。

```bash
poetry run ccwb test
```

このテストはユーザージャーニー全体を通します。一時ディレクトリでインストーラを実行し、AWS プロファイルを設定し、認証フローを起動し、Amazon Bedrock へのアクセスを検証します。認証のためにブラウザが開くはずですが、これはユーザーが実際に目にする挙動と同じです。

より入念に検証するには、`--api` フラグを付けて実際に Bedrock API を呼び出します。

```bash
poetry run ccwb test --api
```

## フェーズ 5: ユーザーへの配布

テスト済みパッケージが用意できたら、最後のフェーズです。認証システムをユーザーへ届けます。Claude Code は 2 つの配布方法を提供します。

### オプション 1: セキュア URL 配布

AWS 認証情報なしで簡単・安全に配布できるよう、事前署名 URL を生成します。

```bash
# 48 時間の有効期限で配布物を作成
poetry run ccwb distribute

# 有効期限を指定（最大 7 日）
poetry run ccwb distribute --expires-hours=72
```

このコマンドはパッケージを S3 にアップロードし、安全な期限付き URL を生成します。この URL をメール、Slack、社内 Wiki などで開発者に共有します。ユーザーはダウンロードしてインストーラを実行するだけで、AWS 認証情報は不要です。

### オプション 2: 手動配布

通常のソフトウェア配布チャネル（共有ドライブ、社内サイト、アーティファクトリポジトリなど）で `dist/` フォルダを共有します。

**プラットフォーム別インストール:**

- **Windows**: `install.bat` を実行
- **macOS/Linux**: `./install.sh` を実行

どの配布方法でも、ユーザー体験はシンプルです。パッケージを受け取り、プラットフォームに応じたインストーラを実行すれば完了です。インストーラは次を行います。

- OS とアーキテクチャを判別
- 適切なバイナリをインストール
- AWS プロファイルを設定
- credential process をセットアップ
- 認証の複雑な仕組みをすべて裏側で処理

ユーザーが `AWS_PROFILE=ClaudeCode` で Claude Code を実行すると、バックグラウンドで自動的に認証が行われます。初回利用時には、組織の ID プロバイダーでの認証のためにブラウザが開きます。
