# Amazon Bedrock 連携のための Okta 完全セットアップガイド

このガイドでは、Okta をゼロから設定し、Bedrock へのアクセスに使用する AWS Cognito Identity Pool と連携できるようにする手順を説明します。

## 目次

1. [Okta Developer アカウントを作成する](#1-okta-developer-アカウントを作成する)  
2. [管理コンソール（Admin Console）にアクセスする](#2-管理コンソールadmin-consoleにアクセスする)  
3. [OIDC アプリケーションを作成する](#3-oidc-アプリケーションを作成する)  
4. [テストユーザーを作成する](#4-テストユーザーを作成する)  
5. [ユーザーをアプリケーションに割り当てる](#5-ユーザーをアプリケーションに割り当てる)  
6. [必要な情報を収集する](#6-必要な情報を収集する)  
7. [セットアップをテストする](#7-セットアップをテストする)  
8. [クォータ監視の設定（任意）](#8-クォータ監視の設定任意)

---

## 1. Okta Developer アカウントを作成する

Okta アカウントがない場合:

1. https://developer.okta.com/signup/ にアクセス
2. 登録フォームを入力:
   - First Name
   - Last Name
   - Email（管理者ユーザー名になります）
   - Country
3. **Sign Up** をクリック
4. メールに届くアクティベーションリンクを確認
5. リンクをクリックしてパスワードを設定
6. Okta ドメインが発行されます（例: `dev-12345678.okta.com`）

> **注**: Okta ドメインは CloudFormation パラメータに必要なので必ず控えてください。

---

## 2. 管理コンソール（Admin Console）にアクセスする

1. `https://your-domain.okta.com` で Okta 組織にログイン
2. 右上の **Admin** をクリックして Admin Console を開く
3. 左側に各種メニューがあるダッシュボードが表示されます

---

## 3. OIDC アプリケーションを作成する

### 手順 3.1: アプリ作成を開始する

1. Admin Console で **Applications** → **Applications** に移動
2. **Create App Integration** をクリック
3. 次を選択:
   - **Sign-in method**: OIDC - OpenID Connect
   - **Application type**: Native Application
4. **Next** をクリック

### 手順 3.2: アプリ設定を行う

以下の設定を入力します。

#### General Settings（一般設定）

- **App integration name**: `Amazon Bedrock CLI Access`（任意の名前でも可）
- **Logo**: 任意（スキップ可）

#### Grant Type（グラントタイプ）

次にチェックが入っていることを確認:

- ✅ **Authorization Code**
- ✅ **Refresh Token**
- ✅ **Resource Owner Password**（任意、テスト用途）

#### Sign-in Redirect URIs（サインイン時リダイレクト URI）

次を **完全に同一** で追加:

```
http://localhost:8400/callback
```

#### Sign-out Redirect URIs（任意）

```
http://localhost:8400/logout
```

#### Controlled Access（アクセス制御）

- **Allow everyone in your organization to access** を選択  
  または
- アクセス制限したい場合は **Limit access to selected groups** を選択

### 手順 3.3: アプリケーションを保存する

1. **Save** をクリック
2. アプリケーションの設定画面に遷移します

### 手順 3.4: Client ID を控える

保存後、次が表示されます。

- **Client ID**: 例 `0oa1234567890abcde`
- **Okta domain**: 例 `dev-12345678.okta.com`

> **重要**: Client ID は CloudFormation パラメータに必要なのでコピーしておいてください。

---

## 4. テストユーザーを作成する

### 手順 4.1: ユーザー管理へ移動する

1. Admin Console で **Directory** → **People**
2. **Add Person** をクリック

### 手順 4.2: テストユーザーを作成する

フォームに入力:

- **First name**: Test
- **Last name**: User
- **Username**: testuser@example.com（メール形式である必要あり）
- **Primary email**: testuser@example.com
- **Password**: **Set by admin** を選択し、パスワードを設定
- ✅ **User must change password on first login**（任意）
- ❌ **Send user activation email now**（テスト用途ならチェックを外す）

**Save** をクリックします。

### 手順 4.3: 追加ユーザー（任意）

必要に応じて、次のようなユーザーを同様に追加します。

- `developer1@example.com`
- `developer2@example.com`
- など

---

## 5. ユーザーをアプリケーションに割り当てる

### 方法 1: アプリ側から割り当てる（推奨）

1. **Applications** → **Applications**
2. **Amazon Bedrock CLI Access** アプリをクリック
3. **Assignments** タブをクリック
4. **Assign** → **Assign to People**
5. 一覧からテストユーザーを探す
6. 各ユーザーの横の **Assign** をクリック
7. **Save and Go Back** をクリック
8. **Done** をクリック

### 方法 2: ユーザープロファイル側から割り当てる

1. **Directory** → **People**
2. ユーザー（例: `testuser@example.com`）をクリック
3. **Applications** タブをクリック
4. **Assign Applications** をクリック
5. **Amazon Bedrock CLI Access** を探して選択
6. **Assign** をクリック
7. **Save and Go Back** をクリック

---

## 6. 必要な情報を収集する

CloudFormation デプロイに必要な情報は揃いました。

| パラメータ | 値（あなたの環境） | 例 |
| --- | --- | --- |
| **OktaDomain** | Okta ドメイン | `dev-12345678.okta.com` |
| **OktaClientId** | Client ID | `0oa1234567890abcde` |

### `ccwb init` で値を使用する

`poetry run ccwb init` 実行時に、次の値の入力を求められます。

```bash
poetry run ccwb init

# ウィザードの入力項目:
# - Okta Domain: dev-12345678.okta.com   （上で控えたドメイン）
# - Client ID: 0oa1234567890abcde        （上で控えた Client ID）
# - インフラの AWS リージョン: us-east-1
# - Bedrock 利用リージョン: us-east-1,us-west-2
# - 監視を有効化: Yes/No
```

CLI ツールが CloudFormation の設定を自動で処理します。

---

## 7. セットアップをテストする

### 手順 7.1: アプリ設定の確認

1. Okta の対象アプリに戻る
2. **General** タブを開く
3. 次を確認:
   - Client authentication: **Use PKCE**
   - Redirect URIs に `http://localhost:8400/callback` が含まれる
   - Grant types に Authorization Code と Refresh Token が含まれる

### 手順 7.2: ユーザー割り当てのテスト

1. **Reports** → **System Log**
2. 次のようなログを探します:
   - "User single sign on to app"
   - "Add user to application membership"
3. いずれも **Success** であることを確認します

---

## 高度な設定（任意）

### Refresh Token Rotation を有効化する

1. 対象アプリの **General** タブを開く
2. General Settings セクションの **Edit** をクリック
3. **Refresh Token** で次を選択:
   - **Rotate token after every use**
   - Grace period: **30 seconds**（または任意）
4. **Save** をクリック

### カスタムクレームを追加する（任意）

部署やグループ情報を追加したい場合:

1. **Security** → **API**
2. Authorization Server（通常 "default"）をクリック
3. **Claims** タブをクリック
4. **Add Claim**
5. 次のように設定:
   - **Name**: `department`
   - **Include in**: ID Token, Access Token
   - **Value type**: Expression
   - **Value**: `user.department`
6. **Create** をクリック

### グループを用意する（任意）

1. **Directory** → **Groups**
2. **Add Group**
3. Name: `bedrock-users`
4. Description: `Users with Amazon Bedrock access`
5. ユーザーをこのグループに追加
6. グループを Bedrock CLI アプリに割り当て

---

## 8. クォータ監視の設定（任意）

クォータ監視機能でユーザーのトークン利用量を追跡・制限する場合、Okta 側で追加設定が必要です。

### 必要な JWT スコープ

クォータ監視 API は JWT トークン内に以下のスコープを要求します。

| スコープ | 必須 | 目的 |
| --- | --- | --- |
| `openid` | **必須** | OIDC の基本スコープ |
| `email` | **必須** | クォータ追跡に使用するユーザー email |
| `profile` | 推奨 | ユーザープロファイル情報 |
| `groups` | 任意 | グループ単位クォータに使用 |

> **注**: `groups` スコープは、`engineering` と `data-science` で上限を変えるなど「グループ単位のクォータポリシー」を使う場合にのみ必要です。

### `groups` スコープを追加する

1. **Security** → **API** → **Authorization Servers**
2. Authorization Server（通常 "default"）をクリック
3. **Scopes** タブ
4. **Add Scope**
5. 設定:
   - **Name**: `groups`
   - **Display phrase**: `Access your group memberships`
   - **Description**: `Allows the app to see your group memberships`
   - **User consent**: `Implicit`
6. **Create**

### `groups` クレームを設定する

JWT トークンにグループ情報を含めるには:

1. **Security** → **API** → **Authorization Servers**
2. Authorization Server（通常 "default"）をクリック
3. **Claims** タブ
4. **Add Claim**
5. 設定:
   - **Name**: `groups`
   - **Include in token type**: `ID Token` → `Always`
   - **Value type**: `Groups`
   - **Filter**: `Matches regex` → `.*`（全グループを含める）
   - **Include in**: `Any scope`（または特定スコープ）
6. **Create**

### トークン有効期限の設定

トークンの有効期限は、クォータチェックの頻度に影響します。

1. **Security** → **API** → **Authorization Servers**
2. Authorization Server をクリック
3. **Access Policies** タブ
4. ポリシーを開き、ルールを編集
5. トークン有効期限を設定:
   - **Access token lifetime**: `1 hour`（既定。多くのケースで十分）
   - **ID token lifetime**: `1 hour`（既定）
   - **Refresh token lifetime**: 要件に合わせて設定

> **ヒント**: トークン期限を短くするとクォータチェック頻度は上がりますが、再認証も増えます。多くの場合は既定値で問題ありません。

### クォータポリシー用のグループ作成

グループベースのクォータを使う場合:

1. **Directory** → **Groups**
2. **Add Group**
3. クォータポリシーに合わせてグループを作成:
   - `engineering` — エンジニアリング
   - `data-science` — データサイエンス
   - `power-users` — 上限が高いユーザー
4. ユーザーを適切なグループに追加
5. グループを Bedrock CLI アプリに割り当て

### クォータ監視のデプロイと設定

Okta 設定後:

```bash
# クォータ監視スタックをデプロイ
poetry run ccwb deploy quota

# 全ユーザーの既定クォータを設定（必須）
poetry run ccwb quota set-default --monthly-limit 225M

# 任意: グループ別クォータ（groups claim が必要）
poetry run ccwb quota set-group engineering --monthly-limit 500M
poetry run ccwb quota set-group data-science --monthly-limit 1B

# 任意: ユーザー個別クォータ
poetry run ccwb quota set-user power.user@company.com --monthly-limit 500M

# クォータ API のテスト
poetry run ccwb test quota-api
```

### 設定の確認方法

JWT に期待するクレームが入っているかを確認します。

1. 対象アプリで認証フローを完了
2. [jwt.io](https://jwt.io) で ID トークンをデコード
3. 次のクレームが存在することを確認:
   - `email` — ユーザーのメールアドレス
   - `groups` — グループ名配列（設定した場合）

クォータ監視の詳細は [Quota Monitoring Guide](../QUOTA_MONITORING.md) を参照してください。

---

## トラブルシューティング

### 「Invalid redirect URI」エラー

- redirect URI が `http://localhost:8400/callback` と完全一致しているか確認
- 末尾スラッシュやタイプミスがないか確認

### ユーザーがサインインできない

- ユーザーがアプリに割り当てられているか確認
- ユーザーアカウントがアクティブか確認
- パスワードが Okta のポリシー要件を満たしているか確認

### Client ID が見つからない

1. **Applications** → **Applications**
2. 対象アプリをクリック
3. **General** タブの「Client Credentials」に Client ID があります

---

## 次のステップ

Okta のセットアップが完了したら:

1. リポジトリをクローン:
   ```bash
   git clone https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock.git
   cd claude-code-setup
   poetry install
   ```
2. セットアップウィザードを実行: `poetry run ccwb init`
3. 配布パッケージを作成: `poetry run ccwb package`
4. デプロイをテスト: `poetry run ccwb test --api`
5. `dist/` フォルダをユーザーに配布

---

## セキュリティのベストプラクティス

1. **本番運用の考慮事項**:
   - グループを使ってスケールするアクセス管理を行う
   - 全ユーザーに MFA を有効化
   - 適切なセッションタイムアウトを設定
   - System Log を定期的に監視

2. **トークン設定**:
   - refresh token rotation を有効化
   - 適切なトークン有効期限を設定
   - PKCE を使用（ネイティブアプリではデフォルトで有効）

3. **ユーザー管理**:
   - Okta のパスワードポリシーを使用
   - アカウントロックアウトポリシーを実装
   - 定期的なアクセスレビュー

---

## 便利な Okta 管理 URL

- Dashboard: `https://your-domain.okta.com/admin/dashboard`
- Applications: `https://your-domain.okta.com/admin/apps/active`
- Users: `https://your-domain.okta.com/admin/users`
- System Log: `https://your-domain.okta.com/admin/reports/system_log`

`your-domain` は実際の Okta ドメインに置き換えてください。
