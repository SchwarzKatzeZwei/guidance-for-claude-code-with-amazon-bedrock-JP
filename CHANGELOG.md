# 変更履歴（Changelog）

このプロジェクトにおける注目すべき変更はすべて、このファイルに記録します。

書式は [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) に基づいており、
本プロジェクトは [Semantic Versioning](https://semver.org/spec/v2.0.0.html) に準拠しています。

## [2.0.0] - 2025-11-17

### 追加（Added）

- **プロファイルシステム v2.0**：単一マシンからのマルチデプロイメント管理
  - 複数の AWS アカウント、リージョン、または組織を管理
  - プロファイル関連コマンド：`ccwb context list`、`ccwb context use`、`ccwb context show`
  - 設定関連コマンド：`ccwb config validate`、`ccwb config export`、`ccwb config import`
  - `~/.ccwb/profiles/` 配下に、プロファイルごとの設定ファイルを配置
  - アクティブなプロファイルを追跡し、簡単に切り替え可能
  - 代表的な用途：本番 vs 開発、マルチリージョン、マルチテナント
- **認証付きランディングページ配布**：エンタープライズ級のパッケージ配布
  - IdP でゲートされたセルフサービスのダウンロードポータル（Okta / Azure AD / Auth0 / Cognito）
  - プラットフォーム検出と OS の自動推奨
  - ACM 証明書によるカスタムドメイン対応
  - 監査証跡のための ALB アクセスログ
  - Lambda による署名付き URL（presigned URL）生成（有効期限 1 時間）
  - CloudFormation テンプレート：`landing-page-distribution.yaml`（1,038 行）
- **配布オプション**：パッケージ共有の 3 方式
  - 手動共有：Zip 化した dist/ フォルダーを、メール／社内ファイル共有で配布
  - S3 署名付き URL：期限付き URL（1〜168 時間で設定可能）
  - ランディングページ：IdP 認証つきセルフサービスポータル
- **QUICK_START.md**：包括的なデプロイ手順書（301 行）
  - 手順ごとのデプロイ方法
  - プラットフォーム別ビルド要件
  - 配布方式の比較
  - 基本的なトラブルシューティング
- **プロファイルのドキュメント**：プロファイルシステムの完全ドキュメント
  - README にプロファイルと用途を説明するセクションを追加
  - CLI_REFERENCE に、全 7 つのプロファイル関連コマンドを追加
  - v1.x 利用者向けの移行ノート

### 変更（Changed）

- **設定保存場所**（破壊的変更）：設定を `source/.ccwb-config/` から `~/.ccwb/` に移動
  - 初回実行時に自動移行
  - タイムスタンプ付きバックアップを作成：`config.json.backup.YYYYMMDD_HHMMSS`
  - プロファイル名とアクティブプロファイルは保持
  - 手動作業は不要
- **設定スキーマ**（破壊的変更）：スキーマバージョン 1.0 → 2.0
  - 単一の設定ファイル → プロファイルごとのファイルへ
  - プロファイルは `~/.ccwb/profiles/<profile-name>.json` に保存
  - アクティブプロファイルは `~/.ccwb/config.json` で管理
- **README を再構成**：アーキテクチャと意思決定にフォーカス（575 → 280 行、51% 削減）
  - 明確化：IdP 連携（AWS SSO / IAM Identity Center ではない）
  - デプロイ手順を削除（→ QUICK_START.md へ）
  - エンドユーザー向けセクションを削除（IT 管理者向けに集中）
  - 「What Gets Deployed」セクションを新設し、インフラ概要を追加
  - 配布オプションに手動共有（セットアップ 0 分）を追加
  - 前提条件を「デプロイ向け」「エンドユーザー向け」に分離
  - 監視セクションをメトリクス分類ごとに再構成
- **配布設定**：`enable_distribution` → `distribution_type`
  - 選択肢：`manual`、`presigned-s3`、`landing-page`
  - `ccwb init` 中に設定
  - `ccwb distribute` コマンドは、すべての自動化タイプで動作
- **deploy コマンド**：配布スタックのデプロイに対応
  - `ccwb deploy distribution` でランディングページ用インフラをデプロイ
  - デプロイ前に IdP 設定を検証
  - Cognito User Pool のクライアント自動作成を処理

### 移行（Migration）

**v1.x からの自動移行：**
- アップグレード後、最初の `ccwb` コマンド実行時に自動実行
- 既存設定のタイムスタンプ付きバックアップを作成
- すべてのプロファイルを新しい `~/.ccwb/profiles/` 構造に移行
- プロファイル名、アクティブプロファイル、全設定を保持
- 手動介入は不要

**検証：**
```bash
ccwb context list     # プロファイルが移行されたことを確認
ccwb context show     # アクティブプロファイルが保持されたことを確認
```

**必要に応じたロールバック：**
```bash
rm -rf ~/.ccwb
cp ~/.ccwb-config/config.json.backup.TIMESTAMP ~/.ccwb-config/config.json
```

### セキュリティ（Security）

- **クライアントシークレットの保管**：IdP のクライアントシークレットを AWS Secrets Manager に保存
  - Cognito User Pool：CloudFormation により自動的にシークレット保存
  - その他の IdP：init 時に手動でシークレットを入力し、Secrets Manager に保存
- **ALB アクセスログ**：ランディングページ認証のための S3 ロギングを自動有効化
- **署名付き URL の有効期限**：1〜168 時間で設定可能（デフォルト 48 時間）
- **S3 バケットポリシー**：配布バケットに対し最小権限アクセスを適用

### インフラ（Infrastructure）

- **ランディングページ・スタック**：ALB + Lambda + S3 の一式インフラ
  - OIDC 認証つき Application Load Balancer
  - 署名付き URL を生成する Lambda 関数
  - パッケージ保管用 S3 バケット
  - セキュリティグループと VPC 統合
  - ACM 証明書によるオプションのカスタムドメイン
- **配布バケット**：presigned-s3 と landing-page の両方で作成
  - オブジェクト期限切れ（expiration）のライフサイクルポリシー
  - バージョニング有効
  - サーバーサイド暗号化

### ドキュメント（Documentation）

- **新規ガイド：**
  - QUICK_START.md：完全なデプロイ手順
  - assets/docs/distribution/comparison.md：配布方式の比較
  - assets/docs/distribution/deployment-guide.md：ランディングページのセットアップ
- **更新ガイド：**
  - README.md：明確化のため再構成（IT 管理者向けに集中）
  - CLI_REFERENCE.md：プロファイル管理コマンドを追加
  - DEPLOYMENT.md：配布オプションを反映して更新
- **プロバイダー別ガイド：** すべての IdP 向けにランディングページ設定手順を用意
  - Okta の Web アプリケーション設定
  - Azure AD のアプリ登録
  - Auth0 の Regular Web Application
  - Cognito User Pool の Web クライアント（自動化）

### 非推奨（Deprecation）

- **旧配布フラグ**：`enable_distribution` は非推奨、`distribution_type` を使用
  - 移行ロジックが旧フィールドを自動的に処理
  - 既存デプロイに対する破壊的変更はなし

## [1.1.4] - 2025-11-04

### 修正（Fixed）

- **Auth0 OIDC プロバイダー URL の形式**：トークン交換時の issuer 検証失敗を修正
  - Auth0 OIDC プロバイダー URL に末尾スラッシュを追加（`https://${Auth0Domain}/`）
  - Auth0 の OIDC issuer は OAuth 2.0 仕様により末尾スラッシュを含む
  - Direct IAM federation での「issuer mismatch」エラーを防止
  - CloudFormation テンプレートのパラメータ説明を、対応ドメイン形式に合わせて更新

- **Auth0 セッション名のサニタイズ**：Auth0 利用時の AssumeRoleWithWebIdentity エラーを修正
  - Auth0 は sub クレームでパイプ区切り形式を使用（例：`auth0|12345`）
  - AWS の RoleSessionName 正規表現 `[\w+=,.@-]*` はパイプ文字を許容しない
  - セッション名内の不正文字を自動的にハイフンへ置換
  - 「Member must satisfy regular expression pattern」検証エラーを防止

- **Bedrock の list 権限**：モデル一覧取得操作での権限エラーを修正
  - list 操作の Resource を特定 ARN から `'*'` に変更
  - 対象：`ListFoundationModels`、`GetFoundationModel`、`GetFoundationModelAvailability`、`ListInferenceProfiles`、`GetInferenceProfile`
  - AWS Bedrock の list 操作は、AWS IAM ドキュメント上 `Resource: '*'` が必要
  - すべてのプロバイダーテンプレート（Auth0 / Azure AD / Okta / Cognito User Pool）に修正を適用

- **ダッシュボードのリージョン設定**：マルチリージョンデプロイにおける監視ダッシュボードを修正
  - ログウィジェット内のハードコード `us-east-1` を `${MetricsRegion}` パラメータに置換
  - deploy コマンドが `profile.aws_region` から `MetricsRegion` パラメータを渡すように変更
  - `us-east-1` 以外でのデプロイ時に発生する `ResourceNotFoundException` を防止
  - 監視ダッシュボードの CloudWatch Logs Insights ウィジェットが対象

### 変更（Changed）

- **コード品質の改善：**
  - `deploy.py` の `subprocess` import をモジュールレベルへ移動
  - 変数名のシャドーイングを修正：`platform_choice` → `platform_name`（`package.py`）

### ドキュメント（Documentation）

- Auth0 セットアップ文書を強化
  - 対応する Auth0 ドメイン形式（標準／リージョナル）の包括的な表を追加
  - AssumeRoleWithWebIdentity 検証エラー向けトラブルシューティングを追加
  - Auth0 のパイプ文字問題の自動処理を明記
  - 有効／無効なドメイン形式の例を追加
  - `https://` プレフィックスと末尾スラッシュは自動付与されることを明確化

## [1.1.3] - 2025-11-03

### 修正（Fixed）

- **Azure AD のテナント ID 抽出**：Azure AD プロバイダーで様々な URL 形式を使った際のデプロイ失敗を修正
  - 正規表現による抽出で、複数の入力形式からテナント GUID を取得できるように修正
  - フル URL（`/v2.0` の有無）、テナント ID のみ、`https://` 付きに対応
  - CloudFormation テンプレートを、正しい Microsoft OIDC v2.0 エンドポイント（`login.microsoftonline.com/{tenant}/v2.0`）を使うよう更新
  - Azure プロバイダーの対応ドメイン形式を、豊富な例とともに文書化
  - 「Parameter AzureTenantId failed to satisfy constraint」エラー向けトラブルシューティングを追加

## [1.1.1] - 2025-10-09

### 追加（Added）

- **高速な認証情報アクセス**：セッションモードが `~/.aws/credentials` を使用し、性能を 99.7% 改善
  - 認証情報ファイル I/O（アトミック書き込み）方式
  - CLI フラグ：`--check-expiration` および `--refresh-if-needed`
  - 期限管理（30 秒の安全バッファ）
  - ConfigParser ベースの INI ファイル処理
- **コード品質の基盤**：Ruff の pre-commit フックによる自動 lint
  - import 順序、スペース、フォーマットを自動修正
  - コミット時に一貫したコードスタイルを強制
- **UX 改善**：package コマンドを強化
  - questionary のチェックボックスによる対話的プラットフォーム選択
  - 共同著者（co-authorship）の希望を尋ねるプロンプト（任意、既定は False）
  - 詳細なビルドログ用の `--build-verbose` フラグ
  - 安定したビルドのためのユニークな Docker イメージタグ

### 変更（Changed）

- **セッション保存モード**：独自キャッシュではなく `~/.aws/credentials` に書き込むよう変更
  - credential_process のオーバーヘッドを解消（取得 300ms → 1ms）
  - 端末セッションをまたいだ認証情報の永続性が向上
  - 標準 AWS CLI ツールとの互換性が向上
  - 既存のセッションモード利用者は自動アップグレード
- **package コマンド**：対話プロンプトによるユーザー操作を改善

### セキュリティ（Security）

- **アトミック書き込み**：一時ファイル + `os.replace()` により、認証情報ファイル破損を防止
- **ファイル権限**：認証情報ファイルを自動的に 0600（所有者のみ読み書き）に設定
- **フェイルセーフな期限判定**：エラー時は期限切れとみなす（セキュリティ優先）

### パフォーマンス（Performance）

- **認証情報取得**：セッションモードで 99.7% 改善（300ms → 1ms）
- **破壊的変更なし**：Keyring モードは変更なし、セッションモードのみ自動アップグレード

## [1.1.0] - 2025-09-30

### 追加（Added）

- **Direct IAM Federation**：Cognito Identity Pool を使わない認証方式の代替案（#32）
  - Okta、Azure AD、Auth0、Cognito User Pools をサポート
  - セッション時間は最大 12 時間まで設定可能
  - プロバイダー別 CloudFormation テンプレート
  - 連携方式（federation type）の自動判定
- **Claude Sonnet 4.5 対応**：最新の Claude Sonnet 4.5 モデルをフルサポート
  - US CRIS プロファイル（us-east-1, us-east-2, us-west-1, us-west-2）
  - EU CRIS プロファイル（欧州 8 リージョン：フランクフルト、チューリッヒ、ストックホルム、アイルランド、ロンドン、パリ、ミラノ、スペイン）
  - Japan CRIS プロファイル（東京、大阪）
  - Global CRIS プロファイル（北米、欧州、アジア太平洋、南米を含む世界 23 リージョン）
- **推論プロファイル権限**：`bedrock:ListInferenceProfiles` と `bedrock:GetInferenceProfile` を追加（#33, #34）
- **CloudFormation ユーティリティ**：例外処理と CloudFormation ヘルパーの新ユーティリティ
- **グローバルエンドポイント対応**：IAM ポリシーが、グローバル推論プロファイル ARN を適切にサポート

### 変更（Changed）

- **モジュール名変更**：`cognito_auth` → `credential_provider`（より正確な命名）
- **IAM ポリシー構造**：IAM ポリシーステートメントをリージョン用とグローバル用に分離
  - リージョンリソースは `aws:RequestedRegion` 条件を使用
  - グローバルリソースはリージョン条件なし
- **deploy コマンド**：deploy.py をリファクタリングし、エラーハンドリングとプロバイダーテンプレート対応を改善
- **リージョン設定**：init ウィザードが、ハードコードされたフォールバックではなく、選択モデルのプロファイルからリージョンを動的に使用
- **CloudWatch メトリクス**：Resource 指定を Bedrock ARN ではなく `'*'` にするよう修正
- **設定スキーマ**：`federation_type` と `federated_role_arn` フィールドを追加

### 修正（Fixed）

- リージョン条件によるブロックがなくなり、グローバルエンドポイントへのアクセスが正しく動作
- すべてのコマンドにおける CloudFormation エラー処理を改善
- リージョンなしのグローバルエンドポイントに対し、リージョン条件が誤って適用されないよう修正
- 選択モデルに対するすべての CRIS プロファイルリージョンを init が正しく処理

### インフラ（Infrastructure）

- プロバイダー別 CloudFormation テンプレートを 4 つ追加（Okta / Azure AD / Auth0 / Cognito User Pool）
- プロバイダー別ロールを含む IAM ロール構成を改善
- CloudFormation の例外処理とユーティリティ

### ドキュメント（Documentation）

- README、ARCHITECTURE、DEPLOYMENT、CLI_REFERENCE を更新
- 両方の認証方式について明確に説明
- 全プロバイダーの設定オプションを文書化

## [1.0.0] - 以前のリリース（Previous Release）

エンタープライズ認証対応の初期リリース。
