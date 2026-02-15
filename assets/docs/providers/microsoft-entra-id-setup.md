# Amazon Bedrock 連携のための Microsoft Entra ID 完全セットアップガイド

このガイドでは、Microsoft Entra ID をゼロから設定し、Bedrock へのアクセスに使用する AWS Cognito Identity Pool と連携できるようにする手順を説明します。

## 目次

1. [Azure アカウントを作成する](#1-azure-アカウントを作成する)  
2. [Azure ポータルにアクセスする](#2-azure-ポータルにアクセスする)  
3. [アプリ登録を作成する](#3-アプリ登録を作成する)  
4. [認証を設定する](#4-認証を設定する)  
5. [テストユーザーを作成する](#5-テストユーザーを作成する)  
6. [ユーザーをアプリに割り当てる](#6-ユーザーをアプリに割り当てる)  
7. [必要な情報を収集する](#7-必要な情報を収集する)  
8. [セットアップをテストする](#8-セットアップをテストする)

---

## 1. Azure アカウントを作成する

Azure アカウントを持っていない場合:

1. https://azure.microsoft.com/free/ にアクセス
2. **Start free** をクリック
3. Microsoft アカウントでサインイン（または作成）
4. 登録を完了（本人確認のためクレジットカードが必要）
5. 200 ドル分のクレジットと Free Tier が付与されます

> **注**: テナント ID は設定に必要なので必ず控えてください。

---

## 2. Azure ポータルにアクセスする

1. https://portal.azure.com にアクセス
2. Azure アカウントでサインイン
3. 上部の検索バーで **Microsoft Entra ID** を検索
4. クリックして管理センターに移動

---

## 3. アプリ登録を作成する

### 手順 3.1: アプリ登録を開始する

1. Microsoft Entra ID で **Applications** → **App registrations** を開く
2. **+ New registration** をクリック

### 手順 3.2: アプリケーションを設定する

以下を入力します。

- **Name**: `Amazon Bedrock CLI Access`
- **Supported account types**: 要件に応じて選択
  - 企業内利用: **Accounts in this organizational directory only**
  - 広い利用: **Accounts in any organizational directory**
- **Redirect URI**: 空欄のまま（次の手順で追加します）

**Register** をクリックします。

### 手順 3.3: ID を控える

登録後、次の値を保存します。

- **Application (client) ID**: `12345678-1234-1234-1234-123456789012`
- **Directory (tenant) ID**: `87654321-4321-4321-4321-210987654321`

---

## 4. 認証を設定する

### 手順 4.1: プラットフォームを追加する

1. 対象のアプリ登録で **Authentication** をクリック
2. **+ Add a platform** をクリック
3. **Mobile and desktop applications** を選択
4. **Add a custom redirect URI** にチェック
5. 次を **完全に同一** で入力:
   ```
   http://localhost:8400/callback
   ```
6. **Configure** をクリック

### 手順 4.2: パブリッククライアントフローを有効化する

1. Authentication 画面で **Advanced settings** までスクロール
2. **Allow public client flows** を **Yes** に切り替え
3. **Save** をクリック

### 手順 4.3: API 権限を確認する

既定の `User.Read` 権限で十分です。変更は不要です。

---

## 5. テストユーザーを作成する

### 手順 5.1: Users へ移動する

1. **Identity** → **Users** → **All users**
2. **+ New user** → **Create new user** をクリック

### 手順 5.2: テストユーザーを作成する

次を入力します。

- **User principal name**: `testuser@yourdomain.onmicrosoft.com`
- **Display name**: `Test User`
- **Password**: Let me create the password（パスワードは控えておく）
- **Usage location**: 自国
- **Block sign in**: No

**Create** をクリックします。

### 手順 5.3: 追加ユーザー（任意）

必要に応じて、追加のテストユーザーも同様に作成します。

---

## 6. ユーザーをアプリに割り当てる

### 手順 6.1: Enterprise Applications から割り当てる

1. **Identity** → **Applications** → **Enterprise applications**
2. **Amazon Bedrock CLI Access** を検索
3. 対象アプリをクリック
4. **Users and groups** をクリック
5. **+ Add user/group** をクリック
6. テストユーザーを選択
7. **Assign** をクリック

---

## 7. 必要な情報を収集する

デプロイに必要な情報は揃いました。

| パラメータ | 値（あなたの環境） | 例 |
| --- | --- | --- |
| **Provider Domain** | テナント URL | `login.microsoftonline.com/{tenant-id}/v2.0` |
| **Client ID** | アプリケーション ID | `12345678-1234-1234-1234-123456789012` |

### サポートされる Provider Domain 形式

CLI は Azure の provider domain を複数形式で受け付けます。扱いやすい形式を選んでください。

| 形式 | 例 | 備考 |
| --- | --- | --- |
| **/v2.0 付きのフル URL** | `login.microsoftonline.com/c56f9106-1d27-456d-bd20-3de87e595a36/v2.0` | **推奨**（標準の Azure AD v2.0 エンドポイント） |
| **/v2.0 なしのフル URL** | `login.microsoftonline.com/c56f9106-1d27-456d-bd20-3de87e595a36` | こちらも対応 |
| **テナント ID のみ** | `c56f9106-1d27-456d-bd20-3de87e595a36` | 最も簡易 |
| **https:// 付き** | `https://login.microsoftonline.com/c56f9106-1d27-456d-bd20-3de87e595a36/v2.0` | プロトコルは自動で除去 |

> **注**: CLI は上記いずれの形式からでも tenant ID（GUID）を自動抽出するため、形式に神経質になる必要はありません。

### `ccwb init` で値を使用する

`poetry run ccwb init` 実行時に、次の値の入力を求められます。

```bash
poetry run ccwb init

# ウィザードの入力項目:
# - Provider Domain: login.microsoftonline.com/{your-tenant-id}/v2.0
# - Client ID: 12345678-1234-1234-1234-123456789012
# - インフラの AWS リージョン: us-east-1
# - Bedrock 利用リージョン: us-east-1,us-west-2
# - 監視を有効化: Yes/No
```

CLI ツールが CloudFormation の設定を自動で処理します。

---

## 8. セットアップをテストする

### 手順 8.1: アプリ設定の確認

1. アプリ登録に戻る
2. **Authentication** をクリック
3. 次を確認:
   - Platform: Mobile and desktop applications
   - Redirect URI: `http://localhost:8400/callback`
   - Public client flows: 有効

### 手順 8.2: OIDC Discovery のテスト

```bash
curl https://login.microsoftonline.com/{your-tenant-id}/v2.0/.well-known/openid-configuration
```

OIDC 設定を含む JSON が返ってくるはずです。

---

## トラブルシューティング

### 「Reply URL does not match」エラー

- redirect URI が次と完全一致していることを確認: `http://localhost:8400/callback`
- 末尾スラッシュやタイプミスがないか確認

### 「User not assigned」エラー

- Enterprise Applications でユーザー割り当てができているか確認
- ユーザーアカウントが有効か確認

### Client ID が見つからない

1. **Applications** → **App registrations**
2. 対象アプリをクリック
3. Overview ページに Client ID が表示されます

### 「Parameter AzureTenantId failed to satisfy constraint」エラー

テナント ID 形式が不正な場合、デプロイ中にこのエラーが発生します。対処は次のとおりです。

- **古い CLI を使用している場合**: 複数 URL 形式に対応した最新版へアップグレードしてください
- **手動回避策**: 「Provider Domain」の入力ではフル URL ではなく tenant ID（GUID）だけを入力します:
  - ✅ `c56f9106-1d27-456d-bd20-3de87e595a36`
  - ❌ `login.microsoftonline.com/c56f9106-1d27-456d-bd20-3de87e595a36/v2.0`
- **アップグレード後**: CLI はすべての形式を自動的に受け付けます（[Supported Provider Domain Formats](#supported-provider-domain-formats) 参照）

---

## 次のステップ

セットアップ完了後:

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
   - "common" ではなく、必ず特定の tenant ID を使用する
   - 全ユーザーに MFA を有効化
   - 適切なセッションタイムアウトを設定
   - サインインログを定期的に監視

2. **トークン設定**:
   - ネイティブアプリでは PKCE はデフォルトで有効
   - public client flows は有効化が必須

3. **ユーザー管理**:
   - グループで大規模なアクセス管理を行う
   - 定期的にアクセスレビューを実施
   - 未使用アカウントは迅速に無効化する
