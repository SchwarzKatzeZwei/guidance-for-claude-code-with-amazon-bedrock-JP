# 配布（Distribution）デプロイガイド

事前署名付き S3 URL（シンプル）または認証付きランディングページ（エンタープライズ）のいずれかを用いて、Claude Code パッケージ配布をデプロイするための完全ガイドです。

---

## 概要

Bedrock 版 Claude Code は、パッケージ化したバイナリと設定をエンドユーザーへ配布する **2 つの方法** をサポートしています。

1. **事前署名付き S3 URL（Presigned S3 URLs）** — 有効期限付き URL によるシンプルな配布（認証不要）
2. **認証付きランディングページ（Authenticated Landing Page）** — ALB + Lambda 経由で IdP 認証を行う、エンタープライズ向け配布

**適切な配布方式の選び方:** 詳細な比較、コスト分析、判断指針は [comparison.md](./comparison.md) を参照してください。

### アーキテクチャ概要

#### 事前署名付き S3 による配布

```
管理者端末 → S3 バケット → 事前署名付き URL（7 日） → ユーザーが直接ダウンロード
```

- **構成要素**: S3 バケット + 事前署名 URL を生成する IAM ユーザー  
- **認証**: なし（URL ベースのアクセス）  
- **最適な対象**: 小規模チーム（20 名未満）、社内の信頼できるユーザー  

#### ランディングページによる配布

```
ユーザー → ALB（HTTPS） → OIDC 認証（IdP） → Lambda → S3（事前署名付き URL）
```

- **構成要素**: ALB + Lambda + S3 + VPC + セキュリティグループ  
- **認証**: OIDC 経由の IdP（Okta / Azure / Auth0 / Cognito）  
- **最適な対象**: 大規模チーム（20〜100 名）、エンタープライズのコンプライアンス要件がある場合  

---

## 前提条件

### 共通の前提条件（両方式共通）

- **AWS CLI**: インストール済みで、認証情報（credentials）が設定済み
- **Python 3.10+**: ccwb CLI に必要
- **Poetry**: Python パッケージマネージャ（`curl -sSL https://install.python-poetry.org | python3 -`）
- **基本認証の設定完了**: Bedrock 認証のため `ccwb init` を完了していること
- **パッケージのビルド済み**: `ccwb package` を実行して配布パッケージを作成済みであること

### ランディングページ方式の追加前提条件

- **サブネット付き VPC**:
  - ALB 用に、2 つ以上の AZ に跨るパブリックサブネット
  - Lambda 用に、2 つ以上の AZ に跨るプライベートサブネット
  - `ccwb deploy networking` で作成するか、既存 VPC を利用可能

- **管理者権限のある IdP アカウント**:
  - Web アプリケーション（OAuth2 の confidential client）を作成できること
  - クライアントシークレットにアクセスできること
  - リダイレクト URI を設定できること

- **OAuth2/OIDC の理解**:
  - Authorization Code フロー
  - クライアント資格情報（ID + secret）
  - Redirect URI / Callback URL

---

## Presigned-S3 方式のデプロイ

認証要件のない小規模チーム向けの、シンプルな配布ワークフローです。

### 手順 1: 配布設定の初期化

init ウィザードを実行し、presigned S3 配布を選択します。

```bash
poetry run ccwb init
```

配布方式の選択プロンプトでは:

- 選択: **"Presigned S3 URLs (simple, no authentication)"**

ウィザードは次を行います。

- プロファイルに配布設定を構成
- 設定を `~/.ccwb/profiles/<profile-name>.json` に保存

### 手順 2: 配布スタックのデプロイ

presigned-s3 配布に必要なインフラをデプロイします。

```bash
poetry run ccwb deploy distribution
```

作成されるもの:

- **S3 バケット**: `{identity-pool-name}-dist-{account-id}`
- **IAM ユーザー**: 事前署名 URL を生成する権限を付与
- **Secrets Manager のシークレット**: IAM ユーザーの認証情報を保存

**デプロイ時間**: 約 2〜3 分

### 手順 3: パッケージのビルド

全プラットフォーム向けにパッケージをビルドします。

```bash
poetry run ccwb package --target-platform all
```

`dist/` ディレクトリに実行ファイルが生成されます。

- `credential-process-macos-arm64`
- `credential-process-macos-intel`
- `credential-process-linux-x64`
- `credential-process-linux-arm64`
- `credential-process-windows.exe`
- インストールスクリプトおよび設定

### 手順 4: パッケージの配布

パッケージをアップロードし、事前署名 URL を生成します。

```bash
poetry run ccwb distribute
```

出力に含まれるもの:

- **事前署名 URL**: 7 日間有効（または `--expires-hours` による任意の期限）
- **SHA256 チェックサム**: パッケージ整合性の検証用
- **ダウンロード手順**: macOS/Linux および Windows 向け
- **ファイルサイズ**: パッケージサイズ情報

### 手順 5: ユーザーへの共有

**事前署名 URL をコピーして、次の手段で共有します。**

- メッセージングアプリ
- メール
- 社内ドキュメント

**URL は 7 日で失効**します。必要に応じて `ccwb distribute` を再実行して再生成してください。

再生成せずに **最新 URL を取得**するには:

```bash
poetry run ccwb distribute --get-latest
```

### Presigned-S3 スタックの出力（Outputs）

スタックの Outputs を確認するには:

```bash
aws cloudformation describe-stacks \
  --stack-name {identity-pool-name}-distribution \
  --query 'Stacks[0].Outputs'
```

主要な出力:

- `DistributionBucket`: S3 バケット名
- `IAMUserName`: 事前署名 URL 生成用の IAM ユーザー
- `IAMUserAccessKeySecretArn`: 認証情報を格納した Secrets Manager の ARN

---

## ランディングページ方式のデプロイ

IdP 認証を伴うエンタープライズ向け配布です。**重要**: IdP の Web アプリケーションは、デプロイの **前** と **後** の両方で設定が必要です。

### デプロイ概要

ランディングページのデプロイには、IdP 設定の **2 段階（実質 3 フェーズ）** が必要です。

1. **フェーズ 1（事前）**: IdP に Web アプリを作成（仮の redirect URI を設定）
2. **フェーズ 2（実行中）**: ccwb でインフラをデプロイ
3. **フェーズ 3（事後）**: 実際の ALB DNS / ドメインで IdP の redirect URI を更新

これが必要な理由:

- CloudFormation は ALB の OIDC デプロイに client ID/secret を必要とする
- ALB の DNS 名はデプロイ完了後にしか確定しない
- IdP の redirect URI は ALB の DNS と **完全一致**している必要がある

---

### フェーズ 1: IdP の Web アプリ設定（ccwb init の前）

IdP 上で **Web アプリケーション（OAuth2 confidential client）** を作成する必要があります。これはネイティブ CLI アプリとは **別物** です。

#### なぜ 2 つのアプリが必要か？

|  | CLI ネイティブアプリ | 配布用 Web アプリ |
| --- | --- | --- |
| **OAuth2 フロー** | Authorization Code + PKCE | Authorization Code |
| **クライアント種別** | Public（secret なし） | Confidential（secret あり） |
| **Redirect URI** | `http://localhost:8400/callback` | `https://<alb-dns>/oauth2/idpresponse` |
| **用途** | CLI の credential process | ALB の OIDC 認証 |
| **作成タイミング** | 初回の ccwb init 中 | 配布設定の前 |

---

#### Okta の Web アプリ設定

1. **Applications へ移動**:
   - Okta Admin Console → Applications → Applications → Create App Integration

2. **OIDC Web アプリを作成**:
   - Sign-in method: **"OIDC - OpenID Connect"**
   - Application type: **"Web Application"**
   - **Next**

3. **アプリ設定**:
   - **App integration name**: `Claude Code Distribution`
   - **Grant type**: ✅ Authorization Code、✅ Refresh Token
   - **Sign-in redirect URIs**:
     - `https://placeholder.example.com/oauth2/idpresponse`（仮。デプロイ後に更新）
   - **Sign-out redirect URIs**:
     - `https://placeholder.example.com`（仮）
   - **Controlled access**: 組織要件に合わせて設定
   - **Save**

4. **認証情報を控える**:
   - **Client ID**: General タブからコピー
   - **Client Secret**: General タブからコピー（Show で表示）
   - **Okta Domain**: 例 `company.okta.com`

5. **ユーザー/グループ割り当て（任意）**:
   - Assignments タブで、配布にアクセスできるユーザー/グループを割り当て

**デプロイ後（フェーズ 3）**: ここに戻り、redirect URI を実際の ALB DNS に更新します。

---

#### Azure AD / Entra ID の Web アプリ設定

1. **アプリ登録へ移動**:
   - Azure Portal → Azure Active Directory → App registrations → New registration

2. **アプリ登録**:
   - **Name**: `Claude Code Distribution`
   - **Supported account types**: **"Accounts in this organizational directory only (Single tenant)"**
   - **Redirect URI**:
     - Platform: **Web**
     - URL: `https://placeholder.example.com/oauth2/idpresponse`（仮）
   - **Register**

3. **Tenant / Client ID を控える**:
   - Overview で次をコピー:
     - **Application (client) ID**（client ID）
     - **Directory (tenant) ID**（tenant ID）

4. **クライアントシークレットの作成**:
   - Certificates & secrets → Client secrets
   - **New client secret**
   - Description: `Claude Code Distribution Landing Page`
   - Expires: 有効期限を選択（推奨 24 か月）
   - **Add**
   - **secret value は即時にコピー**（以後表示されない）

5. **API 権限の設定（必要に応じて）**:
   - API permissions で OpenID Connect 権限が付与済みであることを確認

**デプロイ後（フェーズ 3）**: Authentication タブで redirect URI を更新します。

---

#### Auth0 の Web アプリ設定

1. **Applications へ移動**:
   - Auth0 Dashboard → Applications → Applications → Create Application

2. **アプリ作成**:
   - **Name**: `Claude Code Distribution`
   - **Application type**: **"Regular Web Applications"**
   - **Create**

3. **設定**（Settings タブ）:
   - **Allowed Callback URLs**:
     - `https://placeholder.example.com/oauth2/idpresponse`（仮）
   - **Allowed Logout URLs**:
     - `https://placeholder.example.com`（仮）
   - **Allowed Web Origins**: 空のままで可
   - **Save Changes**

4. **認証情報を控える**（Basic Information）:
   - **Domain**: 例 `company.auth0.com` / `company.us.auth0.com`
   - **Client ID**
   - **Client Secret**

5. **コネクション設定（任意）**:
   - Connections で SAML / AD 等のエンタープライズ接続を有効化

**デプロイ後（フェーズ 3）**: callback URL を実値に更新します。

---

#### Cognito User Pool の Web クライアント設定

**✨ 自動化**: Cognito 設定は、コピー＆ペースト不要で完全自動化されています。

**前提**:

- `cognito-user-pool-setup.yaml`（最新）で Cognito User Pool をデプロイ済み
- 最新テンプレートには `DistributionWebClient` と自動の secret 保存が含まれる

##### 手順 1: Cognito スタックのデプロイ/更新

配布対応の最新テンプレートを使っていることを確認します。

```bash
aws cloudformation deploy \
  --template-file deployment/infrastructure/cognito-user-pool-setup.yaml \
  --stack-name <your-cognito-stack-name> \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    UserPoolName=<your-pool-name> \
    DomainPrefix=<your-domain-prefix>
```

**作成されるもの**:

- ✅ CLI ネイティブ app client（既存）
- ✅ 配布用 Web app client（secret あり、新規）
- ✅ client secret の Secrets Manager 自動保存（新規）
- ✅ 自動検出に必要な Outputs（新規）

**デプロイ時間**: 約 3〜5 分

##### 手順 2: 設定は自動！

`poetry run ccwb init`（フェーズ 2）を実行すると、ウィザードが:

1. Cognito スタックを **自動検出**
2. 配布対応の Outputs が揃っているかを **検証**
3. 検出した設定を表示

   ```
   ✓ Found Cognito stack: my-cognito-stack
   ✓ Stack has all required outputs for distribution

   Detected Configuration:
     • User Pool ID: us-east-1_ABC123XYZ
     • Domain: my-company
     • Client ID: 7a8b9c0d1e2f3g4h
     • Secret ARN: arn:aws:secretsmanager:...

   Use these detected values? [Y/n] █
   ```

4. Enter を押せば設定完了（コピー＆ペースト不要）

---

### フェーズ 2: 配布の初期化とデプロイ

IdP Web アプリの認証情報が準備できたら、ランディングページを設定・デプロイします。

#### 手順 2.1: 配布設定の初期化

init ウィザードを実行します。

```bash
poetry run ccwb init
```

配布方式の選択プロンプトでは:

- 選択: **"Authenticated Landing Page (IdP + ALB)"**

**IdP 設定プロンプト**:

1. **Web 認証に使う IdP**:
   - Okta / Azure AD / Auth0 / Cognito から選択

**Cognito の場合**: 自動検出が動作します（✨）

- Cognito スタックを検索
- 検出した設定（User Pool ID、Domain、Client ID、Secret ARN）を表示
- Enter で承認 → 完了（カスタムドメインのプロンプトへ）

**Okta/Azure/Auth0 の場合**: 手入力が必要です

2. **IdP ドメイン**（Okta/Azure/Auth0 のみ）:
   - **Okta**: `company.okta.com`
   - **Azure**: テナント ID（Azure のアプリ登録で得た GUID）
   - **Auth0**: `company.auth0.com`

3. **IdP Web アプリの Client ID**（Okta/Azure/Auth0 のみ）:
   - フェーズ 1 で取得した client ID を入力

4. **IdP Web アプリの Client Secret**（Okta/Azure/Auth0 のみ）:
   - secret を直接入力（Secrets Manager に自動保存）

5. **カスタムドメイン**（任意、全 IdP 共通）:
   - カスタムドメインを有効化するか（yes/no）
   - yes の場合:
     - ドメイン名: `downloads.company.com`
     - Route53 hosted zone ID（Route53 で DNS 管理する場合）

ウィザードは次を行います。

- **Cognito**: Outputs から自動入力（コピー＆ペースト不要）
- **それ以外**: client secret を Secrets Manager に自動保存
- 設定を `~/.ccwb/profiles/<profile-name>.json` に保存
- `distribution_type = "landing-page"` を設定

#### 手順 2.2: VPC のデプロイ（必要な場合）

ランディングページには、2 つ以上の AZ に跨る public/private サブネットを持つ VPC が必要です。

**選択肢 A: 既存 VPC/サブネットを使う**

- ALB 用に 2+ AZ のパブリックサブネットがあること
- Lambda 用に 2+ AZ のプライベートサブネットがあること
- VPC ID とサブネット ID を控えておく

**選択肢 B: ccwb で新規作成**

```bash
poetry run ccwb deploy networking
```

作成されるもの:

- CIDR `10.0.0.0/16` の VPC
- 異なる AZ に 2 つのパブリックサブネット
- 異なる AZ に 2 つのプライベートサブネット
- Internet Gateway
- NAT Gateway（Lambda のインターネットアクセス用）
- ルートテーブル

**デプロイ時間**: 約 3〜5 分

#### 手順 2.3: ランディングページスタックのデプロイ

認証付きランディングページのインフラをデプロイします。

```bash
poetry run ccwb deploy distribution
```

作成されるもの:

- **S3 バケット**: パッケージ保管用
- **Lambda 関数**: ランディングページ HTML と事前署名 URL を生成
- **ALB**: インターネット向け HTTPS リスナー付きロードバランサ
- **セキュリティグループ**: ALB の ingress（443）および Lambda の egress
- **ターゲットグループ**: ALB トラフィックを Lambda にルーティング
- **ACM 証明書**: カスタムドメイン指定時（Route53 で自動検証）
- **Route53 レコード**: Route53 のカスタムドメイン指定時
- **OIDC 設定**: Lambda へ転送する前に ALB が IdP 認証を実施

**デプロイ時間**: 約 5〜10 分

#### 手順 2.4: スタック出力（Outputs）の取得

デプロイ完了後、スタック出力を取得します。

```bash
poetry run ccwb deploy distribution
```

デプロイ時に次のように表示されます。

```
✓ Landing page deployed successfully!

Distribution URL: https://<alb-dns-name>

⚠️  Configure your IdP web application:
   Redirect URI: https://<alb-dns-name>/oauth2/idpresponse

   Add this redirect URI to your IdP web application settings before users can authenticate.
```

もしくは CLI で直接取得:

```bash
aws cloudformation describe-stacks \
  --stack-name {identity-pool-name}-distribution \
  --query 'Stacks[0].Outputs'
```

主要な出力:

- **DistributionURL**: ランディングページ URL（ALB DNS またはカスタムドメイン）
- **IdPRedirectURI**: IdP に設定するコールバック URL
- **DistributionBucket**: パッケージ保管用 S3 バケット名

**`IdPRedirectURI` をコピー**してください。フェーズ 3 で必要です。

---

### フェーズ 3: デプロイ後の IdP 設定

**重要**: 認証を動作させるため、IdP の redirect URI を実際の ALB DNS に更新する必要があります。

#### Okta の redirect URI 更新

1. Okta Admin Console → Applications → Applications
2. 「Claude Code Distribution」アプリを選択
3. General タブ → General Settings を編集
4. **Sign-in redirect URIs**:
   - `https://placeholder.example.com/oauth2/idpresponse` を削除
   - `https://<actual-alb-dns>/oauth2/idpresponse` を追加（Outputs の値）
5. **Sign-out redirect URIs**:
   - `https://placeholder.example.com` を削除
   - `https://<actual-alb-dns>` を追加（Outputs の値）
6. Save

#### Azure AD の redirect URI 更新

1. Azure Portal → Azure Active Directory → App registrations
2. 「Claude Code Distribution」アプリを選択
3. Authentication（左メニュー）
4. Web → Redirect URIs:
   - `https://placeholder.example.com/oauth2/idpresponse` を削除
   - `https://<actual-alb-dns>/oauth2/idpresponse` を追加（Outputs の値）
5. Save

#### Auth0 の callback URL 更新

1. Auth0 Dashboard → Applications → Applications
2. 「Claude Code Distribution」アプリを選択
3. Settings タブ
4. **Allowed Callback URLs**:
   - `https://placeholder.example.com/oauth2/idpresponse` を削除
   - `https://<actual-alb-dns>/oauth2/idpresponse` を追加
5. **Allowed Logout URLs**:
   - `https://placeholder.example.com` を削除
   - `https://<actual-alb-dns>` を追加
6. Save Changes

#### Cognito の callback URL 更新

AWS CLI の例:

```bash
aws cognito-idp update-user-pool-client \
  --user-pool-id <user-pool-id> \
  --client-id <distribution-web-client-id> \
  --callback-urls "https://<actual-alb-dns>/oauth2/idpresponse" \
  --logout-urls "https://<actual-alb-dns>"
```

または AWS コンソール:

1. AWS Console → Cognito → User Pools
2. 対象 User Pool を選択
3. App integration → App clients → distribution-web-client を選択
4. Hosted UI → Edit:
   - Allowed callback URLs: `https://<actual-alb-dns>/oauth2/idpresponse` に更新
   - Allowed sign-out URLs: `https://<actual-alb-dns>` に更新
5. Save changes

---

### フェーズ 4: パッケージの公開と共有

#### 手順 4.1: パッケージのビルド

```bash
poetry run ccwb package --target-platform all
```

#### 手順 4.2: パッケージの配布

```bash
poetry run ccwb distribute
```

landing-page 方式の出力例:

```
✓ Packages published to landing page!

Users can download from: https://<alb-dns-or-custom-domain>
```

このコマンドはパッケージを S3 にアップロードしますが、事前署名 URL は生成しません。ユーザーがランディングページへアクセスし、認証後に動的に事前署名 URL が生成されます。

#### 手順 4.3: ランディングページ URL の共有

**恒久的なランディングページ URL を次の手段で共有します。**

- 社内 Wiki / ドキュメント
- Slack チャンネル
- メール配布リスト
- オンボーディング資料

**ユーザー側の流れ:**

1. ランディングページ URL にアクセス
2. IdP の認証画面へリダイレクトされる
3. 社内資格情報で認証
4. ダウンロードボタン付きのランディングページを表示
5. ダウンロードをクリック（その場で事前署名 URL を生成、有効期限 1 時間）

**URL の再生成は不要**です。ランディングページ URL は恒久的です。新バージョンを配布する際は `ccwb distribute` を実行してパッケージを更新してください。

---

### フェーズ 5: ランディングページのテスト

1. ブラウザで **ランディングページ URL** にアクセス

2. **期待される挙動**: IdP のログイン画面にリダイレクト

3. 社内資格情報で認証

4. **期待される表示内容**（例）:
   - "Welcome, [your-email]"
   - リリース日
   - プラットフォーム別のダウンロードボタン（Windows / Linux / macOS / All Platforms）
   - ファイルサイズ
   - インストール手順

5. 対象プラットフォームの **download** をクリック

6. **期待される挙動**: すぐにダウンロードが開始

7. （任意）チェックサム検証:
   ```bash
   sha256sum <downloaded-file>
   ```

#### 認証に失敗する場合

**400 Bad Request**:
- **原因**: IdP の redirect URI が未設定、または不一致
- **対処**: `IdPRedirectURI`（Outputs）と IdP 側の callback URL が **完全一致**しているか確認

**OIDC Error / Invalid State**:
- **原因**: client secret 不一致
- **対処**: Secrets Manager の値が IdP の client secret と一致しているか確認

**401 Unauthorized**:
- **原因**: ユーザーが IdP アプリに割り当てられていない
- **対処**: IdP 管理画面でユーザーをアプリに割り当てる

**リダイレクトループ**:
- **原因**: Cookie 問題またはセッション設定
- **対処**: ブラウザ Cookie を削除し、ALB のセッションタイムアウト設定を確認

---

## パッケージの公開（Publishing）

どちらの配布方式でも、公開（publish）ワークフローは同じです。

### パッケージのビルド

全プラットフォーム向けにビルド:

```bash
poetry run ccwb package --target-platform all
```

特定プラットフォームのみ:

```bash
# macOS のみ
poetry run ccwb package --target-platform macos

# Windows のみ（CodeBuild が必要）
poetry run ccwb package --target-platform windows

# Linux のみ
poetry run ccwb package --target-platform linux
```

`dist/` に生成されるもの:

- 各プラットフォーム向け credential process 実行ファイル
- （監視有効時）OTEL helper 実行ファイル
- インストールスクリプト（`install.sh`, `install.bat`）
- 設定ファイル（`config.json`）
- （設定されていれば）Claude Code の settings ディレクトリ

### パッケージの配布（Distribute）

```bash
poetry run ccwb distribute
```

**presigned-s3 の場合**:

- S3 にパッケージをアップロード
- 事前署名 URL を生成（有効期限 7 日）
- URL とダウンロード手順を表示
- 管理者がユーザーへ URL を共有

**landing-page の場合**:

- S3 にパッケージをアップロード
- ランディングページ URL を表示
- 管理者がランディングページ URL を共有
- ユーザーは認証してダウンロード

### 有効期限のカスタマイズ（presigned-s3 のみ）

有効期限を 1〜168 時間で指定:

```bash
# 48 時間（デフォルト）
poetry run ccwb distribute --expires-hours 48

# 1 時間（最小）
poetry run ccwb distribute --expires-hours 1

# 7 日（168 時間、最大）
poetry run ccwb distribute --expires-hours 168
```

**注記**: IAM ユーザーの事前署名 URL の最大有効期間は 7 日（168 時間）です。

### 最新 URL の取得（presigned-s3 のみ）

再生成せずに最新 URL を表示:

```bash
poetry run ccwb distribute --get-latest
```

表示内容:

- 現在の事前署名 URL
- 有効期限
- パッケージのファイル名とチェックサム
- ダウンロード手順

---

## 配布方式の切り替え

presigned-s3 と landing-page は、いつでも切り替え可能です。

### 手順

1. **プロファイルの再設定**:

   ```bash
   poetry run ccwb init
   ```

   - 別の配布方式を選択
   - landing-page へ切り替える場合は IdP 設定も完了させる

2. **配布スタックの再デプロイ**:

   ```bash
   poetry run ccwb deploy distribution
   ```

   - CloudFormation が既存スタックを **置き換え**、新方式で再作成
   - 旧スタックのリソース（S3 バケット、IAM ユーザー等）は **削除**
   - 新スタックのリソースを **作成**

3. **新しい配布先へパッケージを公開**:
   ```bash
   poetry run ccwb package
   poetry run ccwb distribute
   ```

### 重要な注意点

- **同時デプロイ不可**: どちらも同じスタック名（`{identity-pool-name}-distribution`）を使用
- **既存パッケージは削除される**: S3 バケットが削除・再作成される
- **必要ならバックアップ**: 切り替え前に S3 からダウンロードして保全
- **ユーザー手順の更新**: landing-page に切り替える場合、新 URL と IdP 認証が必要

---

## デプロイ後の運用

### パッケージの更新

新バージョンを公開するには:

1. **新しいパッケージをビルド**:

   ```bash
   poetry run ccwb package --target-platform all
   ```

2. **配布先へアップロード**:

   ```bash
   poetry run ccwb distribute
   ```

3. **ユーザーへ通知**:
   - **presigned-s3**: 新 URL を共有（旧 URL は失効まで有効）
   - **landing-page**: 原則不要（ユーザーはページ更新で新しいリリース日を確認）

パッケージ更新のために **スタックを再デプロイする必要はありません**。

---

### カスタムドメインの追加（landing-page）

#### 前提

- Route53 の hosted zone
- ドメイン名（例: `downloads.company.com`）
- hosted zone ID

#### 手順

1. **カスタムドメイン付きで再設定**:

   ```bash
   poetry run ccwb init
   ```

   - カスタムドメインの質問に **yes**
   - ドメイン名: `downloads.company.com`
   - hosted zone ID: `Z1234567890ABC`

2. **配布スタックを再デプロイ**:

   ```bash
   poetry run ccwb deploy distribution
   ```

   - ACM 証明書を作成
   - DNS で証明書検証（Route53 なら自動）
   - ALB を指す Route53 の A レコードを作成
   - ALB リスナーを ACM 証明書で更新

3. **IdP の redirect URI をカスタムドメインに更新**:

   - `https://<alb-dns>/oauth2/idpresponse` から  
     `https://downloads.company.com/oauth2/idpresponse` へ更新
   - IdP ごとのフェーズ 3 手順に従う

4. **テスト**:
   - `https://downloads.company.com` にアクセス
   - SSL 証明書が有効であることを確認
   - IdP 認証が動作することを確認

**DNS 反映**: Route53 の場合 2〜5 分

---

## セキュリティ上の考慮事項

### 配布方式の比較（要約）

**presigned-s3**: 有効期限付き URL（7 日）、認証なし。社内の信頼できるユーザー向けに限定。URL は共有・漏洩し得るが、失効前にアクセスを取り消す手段がない。

**landing-page**: IdP 認証必須、短命の事前署名 URL（1 時間）、監査用に ALB アクセスログを利用可能。エンタープライズのコンプライアンス要件に適する。

### ベストプラクティス

- すべての認証情報は AWS Secrets Manager に保存する
- SHA256 チェックサムでパッケージ整合性を検証する
- landing-page: MFA を有効化し、90 日ごとに secret をローテーションし、IdP アプリ割り当てを最小化する
- S3 / ALB のアクセスログでダウンロード状況を監視する

---

## 参考リンク

- **配布方式の比較**: [comparison.md](./comparison.md) — presigned-s3 と landing-page の詳細比較
- **IdP プロバイダ設定**: [../providers/](../providers/) — IdP 別の CLI 認証ガイド
- **メインのデプロイガイド**: [../../DEPLOYMENT.md](../../DEPLOYMENT.md) — 全体デプロイ手順
- **CLI リファレンス**: [../../CLI_REFERENCE.md](../../CLI_REFERENCE.md) — コマンド完全リファレンス
- **アーキテクチャ**: [../../ARCHITECTURE.md](../../ARCHITECTURE.md) — 技術アーキテクチャ資料

---

**最終更新日**: 2025-01-03  
**バージョン**: 1.0.0  
**互換性**: Bedrock 版 Claude Code v1.0+
