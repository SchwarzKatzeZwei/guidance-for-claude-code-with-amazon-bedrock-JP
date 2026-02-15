# Amazon Bedrock 連携のための Auth0 完全セットアップガイド

このガイドでは、Auth0 をゼロから設定し、Bedrock へのアクセスに使用する AWS Cognito Identity Pool と連携できるようにする手順を説明します。

## 目次

1. [Auth0 アカウントを作成する](#1-auth0-アカウントを作成する)  
2. [ダッシュボードにアクセスする](#2-ダッシュボードにアクセスする)  
3. [ネイティブアプリケーションを作成する](#3-ネイティブアプリケーションを作成する)  
4. [アプリケーションを設定する](#4-アプリケーションを設定する)  
5. [テストユーザーを作成する](#5-テストユーザーを作成する)  
6. [ユーザーをアプリケーションに割り当てる](#6-ユーザーをアプリケーションに割り当てる)  
7. [必要な情報を収集する](#7-必要な情報を収集する)  
8. [セットアップをテストする](#8-セットアップをテストする)

---

## 1. Auth0 アカウントを作成する

Auth0 アカウントを持っていない場合は次を行います。

1. https://auth0.com/signup にアクセス
2. 登録フォームを入力:
   - メールアドレス
   - パスワード
   - 会社名（任意）
3. **Sign Up** をクリック
4. リージョン（US / EU / AU / JP）を選択
5. テナントを作成:
   - Tenant Domain: `your-name`（`your-name.auth0.com` になります）
   - Region: 所在地に合わせて選択
6. **Create Account** をクリック

> **注**: テナントドメインは必ず控えてください。後の設定で必要になります。

---

## 2. ダッシュボードにアクセスする

1. `https://manage.auth0.com` で Auth0 ダッシュボードにログイン
2. 左側にナビゲーションがあるメインダッシュボードが表示されます
3. 左上にテナント名が表示されます

---

## 3. ネイティブアプリケーションを作成する

### 手順 3.1: アプリ作成を開始

1. ダッシュボードで **Applications** → **Applications** を開く
2. **+ Create Application** をクリック
3. 次を入力:
   - **Name**: `Amazon Bedrock CLI Access`
   - **Choose an application type**: **Native** を選択
4. **Create** をクリック

---

## 4. アプリケーションを設定する

### 手順 4.1: Client ID を控える

作成後に以下が表示されます。

- **Client ID**: 例 `aBcDeFgHiJkLmNoPqRsTuVwXyZ123456`
- **Domain**: 例 `your-name.auth0.com`

> **重要**: Client ID は設定に必要なのでコピーしておいてください。

### 手順 4.2: コールバック URL を設定する

1. アプリの設定画面で **Application URIs** を探す
2. **Allowed Callback URLs** を次のように設定:
   ```
   http://localhost:8400/callback
   ```
3. **Allowed Logout URLs**（任意）を次のように設定:
   ```
   http://localhost:8400/logout
   ```

### 手順 4.3: リフレッシュトークンを設定する

1. **Refresh Token Rotation** までスクロール
2. **Rotation** を有効化
3. **Rotation Reuse Interval** を有効化（推奨: 30 秒）

### 手順 4.4: グラントタイプを設定する

1. **Advanced Settings** → **Grant Types**
2. 次が有効になっていることを確認:
   - ✅ **Authorization Code**
   - ✅ **Refresh Token**

### 手順 4.5: 変更を保存する

ページ下部の **Save Changes** をクリックします。

---

## 5. テストユーザーを作成する

### 手順 5.1: ユーザー管理へ移動

1. ダッシュボードで **User Management** → **Users**
2. **+ Create User** をクリック

### 手順 5.2: テストユーザーを作成する

フォームに入力:

- **Email**: `testuser@example.com`
- **Password**: 強固なパスワードを入力
- **Repeat Password**: パスワードを再入力
- **Connection**: Username-Password-Authentication（既定）

**Create** をクリックします。

### 手順 5.3: 追加ユーザー（任意）

必要であれば、以下のテストユーザーも同様に作成します。

- `developer1@example.com`
- `developer2@example.com`

---

## 6. ユーザーをアプリケーションに割り当てる

Auth0 ではデフォルトで全ユーザーが全アプリにアクセスできます。アクセス制限したい場合は次を行います。

### 手順 6.1: Action を作成する（任意）

1. **Actions** → **Flows** → **Login**
2. **+** → **Build Custom**
3. 名前: `Restrict Bedrock Access`
4. ユーザーのメール/メタデータをチェックするコードを追加
5. Action を Deploy

### 手順 6.2: Organizations を有効化する（任意）

エンタープライズ運用向け:

1. **Organizations** を開く
2. 組織（organization）を作成
3. 組織にユーザーを追加
4. 対象アプリで organization を有効化

---

## 7. 必要な情報を収集する

デプロイに必要な情報は揃いました。

| パラメータ | 値（あなたの環境） | 例 |
| --- | --- | --- |
| **Auth0Domain** | Auth0 ドメイン | `your-name.auth0.com` |
| **Auth0ClientId** | Client ID | `aBcDeFgHiJkLmNoPqRsTuVwXyZ123456` |

### サポートされる Provider Domain の形式

CLI は Auth0 の provider domain を複数形式で受け付けます。

| 形式 | 例 | 備考 |
| --- | --- | --- |
| **標準ドメイン** | `company.auth0.com` | **推奨**（標準の Auth0 ドメイン） |
| **リージョナル（US）** | `company.us.auth0.com` | US テナント |
| **リージョナル（EU）** | `company.eu.auth0.com` | EU テナント |
| **リージョナル（AU）** | `company.au.auth0.com` | AU テナント |
| **リージョナル（JP）** | `company.jp.auth0.com` | JP テナント |

**重要**:
- `https://` は付けないでください（システム側で自動付与されます）
- 末尾の `/` は付けないでください（OIDC の provider URL は自動生成されます）
- ドメイン名のみを指定してください（例: `company.auth0.com`）

### `ccwb init` で値を使用する

`poetry run ccwb init` 実行時に、次の値の入力を求められます。

```bash
poetry run ccwb init

# ウィザードの入力項目:
# - Auth0 Domain: your-name.auth0.com            （上で控えたドメイン）
# - Client ID: aBcDeFgHiJkLmNoPqRsTuVwXyZ123456  （上で控えた Client ID）
# - インフラの AWS リージョン: us-east-1
# - Bedrock 利用リージョン: us-east-1,us-west-2
# - 監視を有効化: Yes/No
```

CLI ツールが CloudFormation の設定を自動で処理します。

---

## 8. セットアップをテストする

### 手順 8.1: アプリ設定の確認

1. Auth0 で対象アプリを開く
2. **Settings** タブを確認
3. 次を検証:
   - Application Type: Native
   - Allowed Callback URLs: `http://localhost:8400/callback`
   - Token Endpoint Authentication Method: None

### 手順 8.2: OIDC Discovery のテスト

```bash
curl https://your-name.auth0.com/.well-known/openid-configuration
```

OIDC エンドポイント情報を含む JSON が返ってくるはずです。

### 手順 8.3: ログの確認

1. **Monitoring** → **Logs**
2. 次を確認:
   - Successful Login
   - Failed Login（トラブルシュート用）

---

## トラブルシューティング

### 「Invalid redirect URI」エラー

- callback URL が次と完全一致しているか確認: `http://localhost:8400/callback`
- 末尾のスラッシュや HTTPS を付けない

### 「Unauthorized」エラー

- ユーザーが存在し、パスワードが正しいか確認
- アプリが有効化されているか確認
- アクセスをブロックする Rules / Actions がないか確認

### Client ID が見つからない

1. **Applications** → **Applications**
2. 対象アプリをクリック
3. Settings タブ上部に Client ID が表示されます

### トークン関連の問題

- Authorization Code グラントが有効か確認
- PKCE が明示的に無効化されていないか確認
- refresh token の設定を確認

### 「AssumeRoleWithWebIdentity」バリデーションエラー

次のようなエラーが出る場合:

```
Member must satisfy regular expression pattern: [\w+=,.@-]*
```

これは credential provider 側で自動的に処理されます。Auth0 の user ID は `auth0|12345` のようにパイプ区切り（`|`）形式を使うことが多い一方、AWS はセッション名にその文字を許可しません。そのため credential provider が該当文字をハイフンへ置換してサニタイズします。

**つまり:**
- Auth0 固有の既知の挙動であり、自動的に吸収されます
- 設定変更は不要です
- セッション名は AWS 要件を満たすよう自動整形されます
- ユーザー認証は問題なく動作します

### 「Parameter Auth0Domain failed to satisfy constraint」エラー

Auth0Domain パラメータに関連するデプロイエラーが出る場合:

**原因**: Auth0 ドメイン形式が期待するパターンに一致していません。

**解決策**:
1. ドメイン名のみ（例: `company.auth0.com`）になっているか確認
2. `https://` や末尾 `/` を含めない
3. リージョナルテナントならサフィックス（`.us` `.eu` `.au` `.jp`）が正しいか確認
4. Auth0 として正しいドメインであることを確認

**有効な例:**
- ✅ `company.auth0.com`
- ✅ `company.us.auth0.com`
- ❌ `https://company.auth0.com`
- ❌ `company.auth0.com/`

---

## 次のステップ

Auth0 のセットアップが完了したら:

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
   - 全ユーザーに MFA を有効化
   - エンタープライズ運用では Auth0 Organizations を利用
   - セッション/トークンの有効期限を適切に設定
   - ログを定期的に監視

2. **トークン設定**:
   - refresh token rotation を有効化
   - トークン有効期限は 8 時間以下に設定
   - ネイティブアプリでは PKCE は自動で有効化されます

3. **ユーザー管理**:
   - Auth0 のパスワードポリシーを利用
   - ブルートフォース保護を有効化
   - 異常検知（anomaly detection）を設定
   - 定期的なアクセスレビューを実施

---

## 高度な設定（任意）

### カスタムドメイン

本番環境向け:

1. **Settings** → **Custom Domains**
2. ドメイン（例: `auth.company.com`）を追加
3. DNS 設定を検証
4. アプリ設定を更新

### カスタムクレームの追加

トークンにユーザーメタデータを含めるには:

1. **Actions** → **Flows** → **Login**
2. カスタム Action を作成
3. ID トークンへクレームを追加:
   ```javascript
   exports.onExecutePostLogin = async (event, api) => {
     api.idToken.setCustomClaim('email', event.user.email);
     api.idToken.setCustomClaim(
       'department',
       event.user.user_metadata.department,
     );
   };
   ```

### エンタープライズ接続の有効化

企業 IdP と SSO 連携する場合:

1. **Authentication** → **Enterprise**
2. 接続タイプ（SAML / OIDC など）を選択
3. IdP 要件に従って設定
4. 対象アプリで有効化

---

## Auth0 ダッシュボードの便利な URL

- ダッシュボード: `https://manage.auth0.com/dashboard`
- アプリ一覧: `https://manage.auth0.com/dashboard/applications`
- ユーザー: `https://manage.auth0.com/dashboard/users`
- ログ: `https://manage.auth0.com/dashboard/logs`

テナントを複数持っている場合は、正しいテナントに切り替えて操作してください。
