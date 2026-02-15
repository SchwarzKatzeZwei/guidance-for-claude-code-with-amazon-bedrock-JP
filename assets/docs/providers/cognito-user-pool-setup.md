# AWS Cognito User Pool セットアップガイド

このガイドでは、Claude Code の認証に使用する AWS Cognito User Pool のセットアップ方法を説明します。User Pool は単体で利用することも、Amazon Federate/Midway のような外部 ID プロバイダと統合して利用することもできます。

## 概要

CloudFormation テンプレートは、次を満たす Cognito User Pool を作成します。

- OAuth2 の Authorization Code フロー
- 適切なトークン有効期限設定
- 外部 OIDC プロバイダのサポート
- 属性マッピングの事前設定

## 前提条件

- 適切な認証情報で AWS CLI が設定済み
- Cognito User Pool と IAM ロールを作成できる権限
- Cognito ドメイン用の一意な domain prefix（重複しない接頭辞）

## クイックスタート

### 1. User Pool をデプロイする

```bash
# リポジトリをクローン
git clone <repository-url>
cd claude-code-auth-setup

# User Pool スタックをデプロイ
aws cloudformation deploy \
  --template-file deployment/infrastructure/cognito-user-pool-setup.yaml \
  --stack-name claude-code-user-pool \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    UserPoolName=claude-code-auth \
    DomainPrefix=my-unique-domain-prefix \
    CallbackURLs=http://localhost:8400/callback
```

### 2. 設定値を取得する

```bash
# User Pool ID を取得
aws cloudformation describe-stacks \
  --stack-name claude-code-user-pool \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text

# Client ID を取得
aws cloudformation describe-stacks \
  --stack-name claude-code-user-pool \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
  --output text

# ドメインを取得
aws cloudformation describe-stacks \
  --stack-name claude-code-user-pool \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolDomain`].OutputValue' \
  --output text
```

### 3. Claude Code を設定する

```bash
# User Pool を使って Claude Code を初期化
poetry run ccwb init

# プロンプトで入力する値:
# - Provider Domain: <your-domain-prefix>.auth.<region>.amazoncognito.com
# - User Pool ID: <手順2の値>
# - Client ID: <手順2の値>
```

### 4. Identity Pool をデプロイする

```bash
# 認証インフラをデプロイ
poetry run ccwb deploy --type auth
```

## 設定オプション

### 基本パラメータ

- `UserPoolName`: User Pool 名（既定: claude-code-auth）
- `DomainPrefix`: Cognito ドメインの一意なプレフィックス（必須）
- `CallbackURLs`: OAuth2 コールバック URL（既定: http://localhost:8400/callback）
- `LogoutURLs`: OAuth2 ログアウト URL（既定: http://localhost:8400/logout）

### Amazon Federate/Midway パラメータ（任意）

Amazon 社内で Federate/Midway を使う場合:

- `FederateEnvironment`: 'none' / 'integ' / 'prod'（既定: none）
- `FederateClientId`: Federate サービスプロファイルの Client ID
- `FederateClientSecret`: Federate サービスプロファイルの Client secret

## User Pool の構成

テンプレートは、以下の設定で User Pool を作成します。

### サインイン設定
- ユーザー名（email エイリアス可）
- email を必須属性に設定
- preferred_username を必須属性に設定

### セキュリティ設定
- セルフサインアップ（自己登録）は無効
- パスワードポリシー: 8 文字以上 + 大文字/小文字/数字/記号
- MFA は任意（ユーザー単位で設定可能）
- トークン失効（revocation）を有効化
- ユーザー存在有無のエラー抑止（Prevent user existence errors）を有効化

### トークン有効期限
- 認証フローのセッション: 3 分
- リフレッシュトークン: 600 分（10 時間）
- アクセストークン: 10 分
- ID トークン: 60 分

### OAuth2 設定
- Authorization Code フローのみ
- スコープ: openid, email, profile
- Implicit grant フローは無効

## ユーザー追加

自己登録が無効のため、ユーザーは手動で作成する必要があります。

### AWS コンソールから
1. Cognito → User pools → 対象プールへ移動
2. 「Create user」をクリック
3. ユーザー名と一時パスワードを入力
4. 初回ログイン時にユーザーがパスワード変更する必要があります

### AWS CLI から
```bash
aws cognito-idp admin-create-user \
  --user-pool-id <your-user-pool-id> \
  --username <username> \
  --user-attributes Name=email,Value=user@example.com \
  --temporary-password <temp-password>
```

## 外部 ID プロバイダとの統合

### Amazon Federate/Midway（Amazon 社内）

Federate パラメータを付けてデプロイした場合、統合は自動です。そうでない場合は次の手順になります。

1. Federate サービスプロファイルを作成:
   - テスト: https://integ.ep.federate.a2z.com/
   - 本番: https://prod.ep.federate.a2z.com/

2. サービスプロファイルを設定:
   - Protocol: OIDC
   - Redirect URI: `https://<domain-prefix>.auth.<region>.amazoncognito.com/oauth2/idpresponse`
   - Claims: EMAIL, GIVEN_NAME, FAMILY_NAME
   - Groups: LDAP/ANT/POSIX グループを要件に応じて設定

3. Cognito コンソールで IdP を追加:
   - Type: OpenID Connect
   - Provider name: midway
   - Client ID/Secret: Federate の値
   - Issuer URL: https://idp.federate.amazon.com
   - Attribute mappings: テンプレート出力に示される内容に従う

### その他の OIDC プロバイダ

Okta / Auth0 / Azure AD なども概ね同様です。

1. プロバイダ側に redirect URI を設定
2. Cognito に OIDC IdP として追加
3. 属性を適切にマッピング
4. アプリクライアントの「サポートする ID プロバイダ」を更新

## トラブルシューティング

### ドメインが既に存在する
ドメイン競合エラーが出た場合は、別の `DomainPrefix` を選んでください。Cognito のドメインはグローバルに一意である必要があります。

### Outputs が見つからない
スタックのデプロイが成功していることを確認します。

```bash
aws cloudformation describe-stacks \
  --stack-name claude-code-user-pool \
  --query 'Stacks[0].StackStatus'
```

### 認証の問題
次を確認してください。

1. User Pool にユーザーが存在する
2. callback URL が完全一致している
3. アプリクライアントに正しい ID プロバイダが設定されている

## クリーンアップ

User Pool を削除するには:

```bash
aws cloudformation delete-stack --stack-name claude-code-user-pool
```

注: これにより、すべてのユーザーと設定が削除されます。重要なデータがある場合は事前にバックアップしてください。
