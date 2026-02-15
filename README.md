# Amazon Bedrock を用いた Claude Code 導入ガイダンス

本ガイダンスは、既存の ID プロバイダーを利用して Amazon Bedrock 上の Claude Code をエンタープライズ展開するためのデプロイパターンを提供します。組織の IdP（Okta、Azure AD、Auth0、Cognito User Pools）と統合し、組織全体でのアクセス制御の一元化、監査証跡、利用状況モニタリングを実現します。

## 主な機能

### 組織向け

- **エンタープライズ IdP 連携**: 既存の OIDC ID プロバイダー（Okta、Azure AD、Auth0 など）を活用
- **アクセス制御の一元化**: IdP を通じて Claude Code へのアクセスを管理
- **API キー管理不要**: 長期的な認証情報の配布やローテーションを不要に
- **利用状況モニタリング**: （任意）CloudWatch ダッシュボードで利用状況とコストを追跡
- **マルチリージョン対応**: ユーザーが Bedrock にアクセス可能な AWS リージョンを設定可能
- **マルチパーティション対応**: AWS 商用（Commercial）または AWS GovCloud（US）リージョンへデプロイ可能
- **マルチプラットフォーム対応**: Windows、macOS（ARM/Intel）、Linux 向け配布物を提供

### エンドユーザー向け

- **シームレスな認証**: 企業の認証情報でログイン
- **認証情報の自動更新**: 手動のトークン管理が不要
- **AWS CLI/SDK 連携**: あらゆる AWS ツール／SDK と連携可能
- **マルチプロファイル対応**: 複数の認証プロファイルを管理可能
- **クロスプラットフォーム**: Windows、macOS、Linux で動作

## 目次

1. [クイックスタート](#quick-start)
2. [アーキテクチャ概要](#architecture-overview)
3. [前提条件](#prerequisites)
4. [AWS パーティション対応](#aws-partition-support)
5. [デプロイされるもの](#what-gets-deployed)
6. [モニタリングと運用](#monitoring-and-operations)
7. [追加リソース](#additional-resources)

## クイックスタート

本ガイダンスは、既存の OIDC ID プロバイダー（Okta、Azure AD、Auth0、Cognito User Pools）と Claude Code を統合し、Amazon Bedrock へのフェデレーテッドアクセスを提供します。

### 必要なもの

**既存の ID プロバイダー:**
アプリケーション登録を作成できる有効な OIDC プロバイダーが必要です。本ガイダンスは、この IdP を AWS IAM とフェデレーションし、Bedrock へのアクセスに必要な一時的認証情報を発行します。

**AWS 環境:**

- IAM と CloudFormation の権限を持つ AWS アカウント
- 対象リージョンで Amazon Bedrock が有効化されていること
- デプロイ用の Python 3.10+ 開発環境

### デプロイされるもの

デプロイにより、次が作成されます。

- フェデレーション用の IAM OIDC プロバイダー または Cognito Identity Pool
- Bedrock へのアクセスをスコープした IAM ポリシーを持つ IAM ロール
- プラットフォーム別インストールパッケージ（Windows/macOS/Linux）
- （任意）OpenTelemetry モニタリング基盤

**デプロイ時間:** IdP 設定を含む初回セットアップで 2～3 時間。

手順の詳細は [QUICK_START.md](QUICK_START.md) を参照してください。

## アーキテクチャ概要

本ガイダンスでは、推奨の認証パターンとして **直接 IAM OIDC フェデレーション**を使用します。これにより、監査証跡および利用状況モニタリングに必要な完全なユーザー帰属情報（ユーザー属性）を伴った一時的な AWS 認証情報を提供できます。

**代替案:** レガシーな IdP 連携のために Cognito Identity Pool もサポートしています。比較は [Deployment Guide](assets/docs/DEPLOYMENT.md) を参照してください。

### 認証フロー（直接 IAM フェデレーション）

![アーキテクチャ図](assets/images/credential-flow-direct-diagram.png)

1. **ユーザーが認証を開始**: Claude Code から Amazon Bedrock へのアクセスを要求
2. **OIDC 認証**: ユーザーが OIDC プロバイダーで認証し、ID トークンを取得
3. **IAM へのトークン送信**: アプリケーションが OIDC の ID トークンを Amazon Cognito に送信
4. **IAM が認証情報を返却**: AWS IAM が検証し、一時的な AWS 認証情報を返却
5. **Amazon Bedrock へアクセス**: アプリケーションが一時的認証情報を使って Amazon Bedrock を呼び出し
6. **Bedrock が応答**: Amazon Bedrock が処理し、応答を返却

## 前提条件

### デプロイ（IT 管理者向け）

**ソフトウェア要件:**

- Python 3.10～3.13
- Poetry（依存関係管理）
- AWS CLI v2
- Git

**AWS 要件:**

以下を作成できる適切な IAM 権限を持つ AWS アカウント：

- CloudFormation スタック
- IAM OIDC プロバイダー または Cognito Identity Pool
- IAM ロールおよびポリシー
- （任意）Amazon Elastic Container Service（Amazon ECS）タスクおよび Amazon CloudWatch ダッシュボード
- （任意）Amazon Athena、AWS Glue、AWS Lambda、Amazon Data Firehose リソース
- （任意）AWS CodeBuild
- 対象リージョンで Amazon Bedrock が有効化されていること

**OIDC プロバイダー要件:**

- 既存の OIDC ID プロバイダー（Okta、Azure AD、Auth0 など）
- OIDC アプリケーションを作成できること
- `http://localhost:8400/callback` へのリダイレクト URI をサポートしていること

### エンドユーザー向け

**ソフトウェア要件:**

- AWS CLI v2（credential process 連携のため）
- Claude Code がインストール済みであること
- SSO 認証用の Web ブラウザ

**AWS アカウントは不要** — ユーザーは組織の ID プロバイダーで認証し、自動的に一時的な認証情報を受け取ります。

**Python / Poetry / Git は不要** — ユーザーには IT 管理者が作成したインストールパッケージが提供されます。

### 対応 AWS リージョン

本ガイダンスは、次をサポートする任意の AWS リージョンにデプロイできます。

- IAM OIDC プロバイダー または Amazon Cognito Identity Pool
- Amazon Bedrock
- （任意）Amazon Elastic Container Service（Amazon ECS）タスクおよび Amazon CloudWatch ダッシュボード
- （任意）Amazon Athena、AWS Glue、AWS Lambda、Amazon Data Firehose リソース
- （任意）AWS CodeBuild

AWS 商用（Commercial）および AWS GovCloud（US）の両パーティションをサポートします。詳細は [AWS パーティション対応](#aws-partition-support) を参照してください。

### クロスリージョン推論

Claude Code は、性能と可用性を最適化するために Amazon Bedrock のクロスリージョン推論を使用します。セットアップ時に次を選択できます。

- 使用したい Claude モデル（Opus / Sonnet / Haiku）
- 最適なリージョンルーティングのためのクロスリージョンプロファイル（US / Europe / APAC）
- そのプロファイル内で、モデル推論に用いる特定のソースリージョン

これにより、最良の応答時間と高い可用性を確保するために、複数の AWS リージョンにまたがってリクエストが自動的にルーティングされます。最新の Claude モデル（3.7 以降）では、アクセスのためにクロスリージョン推論が必要です。

### プラットフォーム対応

認証ツールは主要プラットフォームをすべてサポートします。

| プラットフォーム | アーキテクチャ | ビルド方式 | インストール |
| --- | --- | --- | --- |
| Windows | x64 | AWS CodeBuild（Nuitka） | install.bat |
| macOS | ARM64（Apple Silicon） | ネイティブ（PyInstaller） | install.sh |
| macOS | Intel（x86_64） | クロスコンパイル（PyInstaller） | install.sh |
| macOS | Universal（両対応） | Universal2（PyInstaller） | install.sh |
| Linux | x86_64 | Docker（PyInstaller） | install.sh |
| Linux | ARM64 | Docker（PyInstaller） | install.sh |

**ビルドシステム:**

パッケージビルダーは、PyInstaller（macOS/Linux）および Nuitka を用いた AWS CodeBuild（Windows）により、全プラットフォーム向けの実行ファイルを自動作成します。いずれのビルドもスタンドアロン実行ファイルを生成するため、エンドユーザー側で Python をインストールする必要はありません。

詳細なビルド設定は [QUICK_START.md](QUICK_START.md#platform-builds) を参照してください。

## AWS パーティション対応

本ガイダンスは、単一の統一コードベースで複数の AWS パーティションにまたがるデプロイをサポートします。同一の CloudFormation テンプレートとデプロイ手順が、AWS 商用と AWS GovCloud（US）の両リージョンでシームレスに動作します。

### 対応パーティション

| パーティション | リージョン | 想定用途 |
|---|---|---|
| **AWS Commercial**（`aws`） | Bedrock が利用可能なすべてのリージョン | 一般的な商用ワークロード |
| **AWS GovCloud (US)**（`aws-us-gov`） | us-gov-west-1, us-gov-east-1 | 米国政府機関、請負業者、規制対象ワークロード |

### 仕組み

デプロイ時に AWS パーティションを自動検出し、リソースを適切に構成します。

**リソース ARN:**
- CloudFormation は疑似パラメータ `${AWS::Partition}` を使用
- `aws` または `aws-us-gov` に自動解決
- 例: `arn:${AWS::Partition}:bedrock:*::foundation-model/*`

**サービスプリンシパル:**
- Cognito Identity のサービスプリンシパルはパーティション／リージョン依存
- 商用: `cognito-identity.amazonaws.com`
- GovCloud West: `cognito-identity-us-gov.amazonaws.com`
- GovCloud East: `cognito-identity.us-gov-east-1.amazonaws.com`
- IAM ロールの信頼ポリシーは、リージョンに応じて正しいプリンシパルを自動的に使用

**S3 エンドポイント:**
- 商用: `s3.region.amazonaws.com`
- GovCloud: `s3.region.amazonaws.com`

### AWS GovCloud へのデプロイ

GovCloud の認証情報を有効にしたうえで、同じ [クイックスタート](#quick-start) 手順に従ってください。`ccwb init` の際に GovCloud リージョン（us-gov-west-1 または us-gov-east-1）を選択すると、ウィザードが GovCloud 互換のモデルおよびエンドポイントを自動構成します。

**GovCloud 固有の考慮事項:**

1. **認証情報:** GovCloud は商用アカウントとは別の AWS 認証情報が必要です
2. **モデル ID:** GovCloud ではリージョン接頭辞付きモデル ID（例: `us-gov.anthropic.*`）を使用します
3. **FIPS エンドポイント:** Cognito のホステッド UI は `{prefix}.auth-fips.{region}.amazoncognito.com` を使用します
4. **Managed Login:** ブランディングは Cognito の各アプリクライアントごとに作成する必要があります

### 検証

デプロイ後、正しいパーティション設定になっていることを確認します。

```bash
# IAM ロール ARN が正しいパーティションになっているか確認
aws iam get-role \
  --role-name BedrockCognitoFederatedRole \
  --region <region> \
  --query 'Role.Arn'

# 期待される ARN 形式:
# Commercial: arn:aws:iam::ACCOUNT:role/BedrockCognitoFederatedRole
# GovCloud: arn:aws-us-gov:iam::ACCOUNT:role/BedrockCognitoFederatedRole
```

### 後方互換性

✅ **変更はすべて完全に後方互換です**

- 既存の商用デプロイは修正なしで引き続き動作します
- CloudFormation の更新を既存スタックに適用できます
- ユーザー向け機能に変更はありません
- データ移行は不要です

## デプロイされるもの

### 認証インフラ

`ccwb deploy` コマンドは次を作成します。

**IAM リソース:**

- IAM OIDC プロバイダー（直接 IAM フェデレーション用）または Cognito Identity Pool（レガシー IdP 用）
- フェデレーテッドアクセスのための信頼関係を持つ IAM ロール
- 次にスコープした IAM ポリシー：
  - 設定したリージョンにおける Bedrock モデル呼び出し
  - （モニタリング有効時）CloudWatch メトリクスの発行

**ユーザー配布パッケージ:**

- プラットフォーム別実行ファイル（Windows、macOS ARM64/Intel、Linux x64/ARM64）
- AWS CLI の credential process を設定するインストールスクリプト
- 事前設定済みの設定（OIDC プロバイダー、モデル選択、モニタリングエンドポイント）

### 配布オプション（任意）

パッケージをビルドした後、ユーザーへの共有方法は 3 つあります。

| 方法 | 適したケース | 認証 |
| --- | --- | --- |
| **手動共有** | 規模を問わず | なし |
| **事前署名付き S3 URL** | 自動配布 | なし |
| **ランディングページ** | セルフサービスポータル | IdP（Okta/Azure/Auth0/Cognito） |

**手動共有:** `dist/` フォルダを zip 化し、メールや社内ファイル共有で配布します。追加インフラは不要です。

**事前署名 URL:** 期限付きの S3 URL を生成して直接ダウンロードさせます。自動化できますが、S3 バケットの準備が必要です。

**ランディングページ:** IdP 認証、プラットフォーム判別、カスタムドメイン対応を備えたセルフサービス型ポータルです。コンプライアンス向け機能を含む完全自動化が可能です。

詳細は [Distribution Comparison](assets/docs/distribution/comparison.md) を参照してください。

### モニタリング基盤（任意）

OpenTelemetry によるモニタリングスタックを有効化して利用状況の可視化を行えます。

**構成要素:**

- VPC およびネットワークリソース（または既存 VPC を使用）
- OpenTelemetry Collector を実行する ECS Fargate クラスター
- メトリクス取り込み用 Application Load Balancer
- リアルタイムの利用状況メトリクスを表示する CloudWatch ダッシュボード
- メトリクス集計用 DynamoDB

**（任意）分析アドオン:**

- メトリクスを S3 にストリーミングする Kinesis Data Firehose
- 長期保管のための S3 データレイク
- 過去データに対する SQL クエリ用 Amazon Athena
- スキーマ管理のための AWS Glue Data Catalog

手順の詳細は [QUICK_START.md](QUICK_START.md) を参照してください。

## モニタリングと運用

（任意の）OpenTelemetry モニタリングにより、コスト配賦、キャパシティ計画、生産性の把握のための包括的な利用状況可視化を提供します。

### 利用可能なメトリクス

**トークン経済:**

- ユーザー／モデル／種別ごとの入力・出力・キャッシュトークン消費
- プロンプトキャッシュの有効性（ヒット率、トークン節約量）
- ユーザー、チーム、部門別のコスト配賦

**コード活動:**

- 記述行数と採用（accepted）行数の比較（生産性のシグナル）
- ファイル操作の内訳（編集、検索、読み取り）
- プログラミング言語の分布

**運用健全性:**

- アクティブユーザー数と上位消費者
- 利用パターン（時間別／日別ヒートマップ）
- 認証および API のエラー率

### インフラ

モニタリングスタック（`ccwb deploy monitoring` でデプロイ）には次が含まれます。

- OpenTelemetry Collector を実行する ECS Fargate
- メトリクス取り込み用 Application Load Balancer
- リアルタイム可視化のための CloudWatch ダッシュボード
- （任意）S3 データレイク + Athena による履歴分析

セットアップとダッシュボード例は [Monitoring Guide](assets/docs/MONITORING.md) を参照してください。  
履歴データに対する SQL クエリは [Analytics Guide](assets/docs/ANALYTICS.md) を参照してください。

## 追加リソース

### はじめに

- [Quick Start Guide](QUICK_START.md) - ステップバイステップのデプロイ手順
- [CLI Reference](assets/docs/CLI_REFERENCE.md) - `ccwb` ツールのコマンドリファレンス全体

### アーキテクチャ／デプロイ

- [Architecture Guide](assets/docs/ARCHITECTURE.md) - システムアーキテクチャと設計判断
- [Deployment Guide](assets/docs/DEPLOYMENT.md) - 高度なデプロイオプション
- [Distribution Comparison](assets/docs/distribution/comparison.md) - 事前署名 URL とランディングページの比較
- [Local Testing Guide](assets/docs/LOCAL_TESTING.md) - デプロイ前のテスト

### モニタリング／分析

- [Monitoring Guide](assets/docs/MONITORING.md) - OpenTelemetry のセットアップとダッシュボード
- [Analytics Guide](assets/docs/ANALYTICS.md) - S3 データレイクと Athena の SQL クエリ

### ID プロバイダー設定

- [Okta](assets/docs/providers/okta-setup.md)
- [Microsoft Entra ID（Azure AD）](assets/docs/providers/microsoft-entra-id-setup.md)
- [Auth0](assets/docs/providers/auth0-setup.md)

## ライセンス

本プロジェクトは MIT ライセンスの下で提供されます。詳細は [LICENSE](LICENSE) ファイルを参照してください。
