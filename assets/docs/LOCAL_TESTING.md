# ローカルテストガイド

Claude Code 認証を組織に配布する前に、ローカルで十分にテストしておくことで、すべてが期待どおりに動作することを確認できます。`ccwb test` コマンドが検証の大部分を自動で行いますが、本ガイドでは、追加のシナリオや性能テストも含め、デプロイに対する確信を得るための手順を説明します。

## 自動テストの強み

CLI は、ユーザーが実際に体験する流れをそのまま再現する包括的な自動テストを提供します。

```bash
poetry run ccwb test         # 基本の認証テスト
poetry run ccwb test --api   # Bedrock API 呼び出しを含むフルテスト
```

この単一コマンドで、インストール、認証、Bedrock アクセスまで、ユーザージャーニー全体を実行します。多くのデプロイでは、この自動テストで十分な検証になります。ただし、裏側の挙動を理解し、エッジケースもテストしておくと、ユーザーサポートをより効果的に行えます。

## デプロイ済みインフラの把握

認証フローをテストする前に、AWS インフラが正しくデプロイされていることを確認したい場合があります。`ccwb deploy` が作成する CloudFormation スタックには、認証に必要なすべてのコンポーネントが含まれます。

認証スタックの状態を確認するには次を実行します。

```bash
# auth スタックの状態を確認（デプロイ時の設定に基づく）
poetry run ccwb status --detailed
```

これにより、デプロイ済みの全スタック状態が表示されます。

健全なデプロイでは "CREATE_COMPLETE" または "UPDATE_COMPLETE" が表示されます。スタック出力には Identity Pool ID や IAM ロール ARN など、認証フローに必要な重要値が含まれます。通常それらを直接操作する必要はありませんが、トラブルシューティング時には、それらが存在することを理解していると役立ちます。

## 配布パッケージの確認

`ccwb package` で作られたパッケージには、エンドユーザーがインストールするために必要なものがすべて含まれます。中身を理解しておくと、ユーザーサポートや障害切り分けに役立ちます。

配布ディレクトリを確認します。

```bash
ls -la dist/
```

プラットフォーム別実行ファイル（credential-process-macos、credential-process-linux）、組織設定を含む設定ファイル、そしてインテリジェントなインストーラスクリプトが見つかるはずです。モニタリングを有効化している場合は、OTEL helper 実行ファイルや Claude Code 設定も含まれます。

設定ファイルには、OIDC プロバイダー情報と Cognito Identity Pool ID が含まれます。

```bash
cat dist/config.json | jq .
```

この設定はインストール時にユーザーのホームディレクトリへコピーされ、credential process が実行時に読み取ります。

## 手動インストールのテスト

`ccwb test` が大部分を検証しますが、ユーザー体験をより理解するために、インストール手順を手動でなぞってみたい場合があります。

新規ユーザーのインストールを模したテスト環境を作成します。

```bash
mkdir -p ~/test-user
cp -r dist ~/test-user/
cd ~/test-user/dist
./install.sh
```

インストーラはプラットフォームを判別し、適切なバイナリを `~/claude-code-with-bedrock/` にコピーして、AWS CLI プロファイルを設定します。これはユーザーの体験と同じです。

認証をテストします。

```bash
aws sts get-caller-identity --profile ClaudeCode
```

初回実行では認証のためブラウザが開きます。ログインが成功すると、フェデレートされた AWS ID が表示され、フロー全体が正しく動作していることを確認できます。

## 認証フローのテスト

認証の仕組みを理解しておくと、ユーザーサポートがやりやすくなります。credential process は、安全性を維持しつつ認証プロンプトを最小化するため、洗練されたキャッシュ機構を実装しています。

キャッシュをクリアして、フロー全体を観察したい場合は次を実行します。

```bash
# キャッシュ済み認証情報をクリア（キーチェーン権限を維持するため、期限切れダミーに置換）
~/claude-code-with-bedrock/credential-process --clear-cache

# 認証をトリガー
aws sts get-caller-identity --profile ClaudeCode
```

ブラウザで組織のログインページが開き、認証後にターミナルへフェデレート ID が表示されます。

初回認証後は認証情報がキャッシュされます。連続呼び出しで確認できます。

```bash
# 1 回目: 認証を含む
time aws sts get-caller-identity --profile ClaudeCode

# 2 回目: キャッシュ済み認証情報を利用
time aws sts get-caller-identity --profile ClaudeCode
```

1 回目は認証を含めて 3～10 秒程度、キャッシュ利用時は 1 秒未満で完了します。認証情報は最大 8 時間まで有効です。

## Bedrock アクセスの検証

認証が動作したら、意図どおり Amazon Bedrock のモデルにアクセスできることを確認します。まず、利用可能な Claude モデル一覧を取得します。

```bash
aws bedrock list-foundation-models \
  --profile ClaudeCode \
  --region us-east-1 \
  --query 'modelSummaries[?contains(modelId, `claude`)].[modelId,modelName]' \
  --output table
```

これにより、IAM 権限が Bedrock モデルへのアクセスを許可していることを確認できます。エンドツーエンドの確認として、Claude モデルを実際に呼び出します。

```bash
# 簡単なテストプロンプトを作成
echo '{
  "anthropic_version": "bedrock-2023-05-31",
  "messages": [{"role": "user", "content": "Say hello!"}],
  "max_tokens": 50
}' > test-prompt.json

# Claude を呼び出し
aws bedrock-runtime invoke-model \
  --profile ClaudeCode \
  --region us-east-1 \
  --model-id anthropic.claude-3-haiku-20240307-v1:0 \
  --body fileb://test-prompt.json \
  response.json

# 応答を表示
jq -r '.content[0].text' response.json
```

複数の Bedrock リージョンを含む構成の場合は、各リージョンでアクセスをテストして、期待どおりに動作することを確認してください。

```bash
for region in us-east-1 us-west-2 eu-west-1; do
  echo "Testing $region..."
  aws bedrock list-foundation-models \
    --profile ClaudeCode \
    --region $region \
    --query 'length(modelSummaries)' \
    --output text
done
```

## Claude Code との統合

最終的なテストは、認証システムと一緒に Claude Code を実際に使うことです。AWS プロファイルの環境変数を設定します。

```bash
export AWS_PROFILE=ClaudeCode
```

モニタリングを有効化している場合は、Claude Code 設定が正しくインストールされていることを確認します。

```bash
cat ~/.claude/settings.json | jq '.env.OTEL_EXPORTER_OTLP_ENDPOINT'
```

次に Claude Code を起動します。

```bash
claude
```

Claude Code は AWS プロファイルを用いて自動的に認証を行います。内部では、Bedrock へのアクセスが必要になるたびに credential process を呼び出し、認証は透過的に処理されます。

### 重要: AWS 認証情報の優先順位

テスト時には、AWS CLI の認証情報優先順位に注意してください。AWS CLI は次の順序で認証情報を解決します。

1. **環境変数**（`AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY`、`AWS_SESSION_TOKEN`）— 最優先
2. コマンドラインオプション
3. 環境変数 `AWS_PROFILE`
4. AWS 設定の credential process
5. 設定ファイル内の静的認証情報
6. インスタンスメタデータ

他ツール（例: Isengard）などが設定した AWS 認証情報が環境変数に残っていると、それが ClaudeCode プロファイルより優先されてしまいます。Claude Code 認証を確実に使うには、環境変数の認証情報をクリアしてください。

```bash
# 環境変数の AWS 認証情報をクリア
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN

# そのうえで ClaudeCode プロファイルを使用
export AWS_PROFILE=ClaudeCode
aws sts get-caller-identity
```
