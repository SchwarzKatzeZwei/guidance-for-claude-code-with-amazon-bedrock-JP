# Claude Code クォータ監視

クォータ監視はユーザーのトークン消費量を追跡し、使用量のしきい値を超えた場合に自動アラートを送信します。これにより管理者はコスト管理を行いやすくなり、想定外の超過を防止できます。

## 概要

クォータ監視システムは、ダッシュボードスタックと統合して、ユーザーごとの月次トークン消費を追跡し、設定可能なしきい値で SNS アラートを送る **任意の CloudFormation スタック**です。

### 主な機能

- **ユーザー別トークン追跡**: 認証済みユーザーごとに、月次／日次の消費量を監視
- **細粒度のクォータポリシー**: user / group / default の各レベルで上限を設定し、優先規則で解決
- **複数の上限タイプ**: 月次トークンと日次トークン
- **しきい値の設定**: 上限の 80%／90%／100% でアラート
- **JWT グループ統合**: IdP クレームからグループ所属を自動抽出
- **アラート重複排除**: ユーザー×期間×上限タイプ×しきい値ごとに 1 回のみ送信
- **DynamoDB で保存**: TTL による自動クリーンアップで効率的に追跡

### アーキテクチャ構成要素

- **UserQuotaMetrics テーブル**: DynamoDB。月次／日次の使用合計（トークン種別内訳も）を保存
- **QuotaPolicies テーブル**: DynamoDB。細粒度ポリシー（user/group/default）を保存
- **Quota Monitor Lambda**: 15 分ごとにしきい値をチェックするスケジュール関数
- **SNS トピック**: 管理者向けアラート配信
- **EventBridge ルール**: Lambda のスケジューリング
- **Metrics Aggregator 連携**: メトリクス処理中にクォータテーブルを更新

## 設定

> **前提条件**: モニタリングが有効で、dashboard スタックがデプロイ済みである必要があります。デプロイ詳細は [CLI Reference](CLI_REFERENCE.md#deploy---deploy-infrastructure) を参照してください。

`ccwb init` 実行時、モニタリングが有効であればクォータ監視は **既定で有効**です。次を設定するよう促されます。
- ユーザーごとの月次トークン上限（既定: 2 億 2,500 万トークン）
- しきい値の自動算出（例: 80% 警告は 180M、90% クリティカルは 202.5M）
- バーストバッファ付き日次トークン上限（月次から自動算出）
- 日次／月次の上限に対する強制モード

デプロイは `poetry run ccwb deploy`（有効スタックを一括デプロイ）または `poetry run ccwb deploy quota`（クォータスタックのみ）で行います。OIDC 設定はプロファイル設定から自動的に引き渡されます。完全な手順は [CLI Reference](CLI_REFERENCE.md#deploy---deploy-infrastructure) を参照してください。

## 設定パラメータ

| パラメータ | 既定値 | 説明 |
| --- | --- | --- |
| MonthlyTokenLimit | 225M tokens | ユーザー 1 人あたりの月次上限（既定） |
| DailyTokenLimit | ~8.25M tokens | 日次上限（バーストバッファ付きで自動算出） |
| BurstBufferPercent | 10% | 日次上限のバッファ率（5～25%） |
| MonthlyEnforcementMode | block | 月次上限超過時にアクセスをブロック |
| DailyEnforcementMode | alert | 日次上限超過時はアラートのみ |
| Warning Threshold | 80% (180M) | 第 1 段階のアラート |
| Critical Threshold | 90% (202.5M) | 第 2 段階のアラート |
| Check Frequency | 15 minutes | Lambda 実行間隔 |
| Alert Retention | 60 days | 重複排除のための DynamoDB TTL |
| EnableFinegrainedQuotas | true | 細粒度ポリシー対応を有効化 |

上限を更新するには、`ccwb init` を再実行し、`ccwb deploy quota` で再デプロイしてください。

## 日次上限と請求ショック（bill shock）対策

暴走的な利用による想定外コストを防ぐため、本システムは月次クォータから日次上限を自動算出し、バーストバッファを設定できます。

### なぜ日次上限が必要か

日次上限がないと、ヘビーユースにより月次クォータを 2～3 日で使い切り、想定外コストや月途中のブロックにつながる可能性があります。日次上限は 24 時間以内に異常を検知しつつ、正当な作業パターンも許容します。

### 算出式

```
daily_limit = monthly_limit ÷ 30 × (1 + burst_buffer%)
```

月次 225M、バースト 10% の例：
- 基本日次: 225,000,000 ÷ 30 = 7,500,000 tokens/day
- 10% バースト込み: 7,500,000 × 1.10 = **8,250,000 tokens/day**

### バーストバッファの目安

バーストバッファは、平均を上回る正当な日次の変動を許容します。

| バッファ | 日次（225M/月） | 利用場面 |
|---|---:|---|
| 5%（厳格） | 7,875,000 tokens | コスト制御を強め、重い日を早く検知したい |
| 10%（既定） | 8,250,000 tokens | 一般的利用のバランス重視 |
| 25%（柔軟） | 9,375,000 tokens | 平均の 1.25 倍程度を許容し、極端なスパイクのみ検知 |

### 強制モード

上限タイプごとに強制を切り替えられます。

| モード | 挙動 | 利用場面 |
|---|---|---|
| **alert** | 通知のみ。利用は継続可 | 監視・ソフト上限 |
| **block** | 超過時に認証情報発行を拒否 | 厳格なコスト制御 |

**推奨既定:**
- **日次**: `alert` — 逸脱を警告しつつ作業は止めない
- **月次**: `block` — 予算上限で確実に停止

### 設定例

```
月次上限: 225,000,000 tokens（block）
日次上限:   8,250,000 tokens（alert）
バースト:  10%

挙動:
- 1 日目: 9M tokens → 日次アラート
- 2 日目: 8.5M tokens → 日次アラート
- 3～5 日目: 通常（約 7M/日）→ アラートなし
- 15 日目: 月次 180M 到達 → 80% 警告
- 20 日目: 月次 225M 到達 → アクセスブロック
```

## 細粒度クォータポリシー

細粒度クォータにより、ユーザーやグループごとに異なる上限を設定でき、明確な優先順位で解決されます。

### ポリシー種別

1. **ユーザーポリシー**: メールアドレスで特定ユーザーに適用
2. **グループポリシー**: グループ所属ユーザー全員に適用（JWT クレーム由来）
3. **デフォルトポリシー**: より具体的なポリシーがないユーザーに適用

### 優先順位（precedence）

ユーザーの有効クォータを決める際は次の順序です。

1. **ユーザー固有ポリシー**（最優先）: ユーザーのメールにポリシーがあればそれを適用
2. **グループポリシー**（最も厳しいもの）: 複数グループに所属し各グループにポリシーがある場合、**最も低い上限**（最も厳格）を適用
3. **デフォルトポリシー**: user / group がなければデフォルトを適用
4. **ポリシーなし**: どのポリシーも定義されていない場合、利用は **無制限**（そのユーザーに対するクォータ監視は無効）

### 上限タイプ

各ポリシーは 2 種類の上限を設定できます。

| 上限タイプ | 説明 | リセット周期 |
| --- | --- | --- |
| 月次トークン上限 | 暦月あたりの最大トークン | 毎月 1 日 |
| 日次トークン上限 | 1 日あたりの最大トークン | UTC 0:00 |

### CLI によるポリシー管理

ポリシー管理には `ccwb quota` コマンドを使用します。

```bash
# ユーザー固有ポリシーを設定
ccwb quota set-user john.doe@company.com --monthly-limit 500M --daily-limit 20M

# グループポリシーを設定
ccwb quota set-group engineering --monthly-limit 400M

# 全ユーザーのデフォルトポリシーを設定
ccwb quota set-default --monthly-limit 225M --daily-limit 8M

# すべてのポリシーを一覧表示
ccwb quota list
ccwb quota list --type group

# 特定ユーザーの有効ポリシーを表示
ccwb quota show john.doe@company.com --groups "engineering,ml-team"

# 上限に対する現在使用量を表示
ccwb quota usage john.doe@company.com

# ポリシーを削除
ccwb quota delete group engineering

# クォータ超過ユーザーを一時的にブロック解除（Phase 2）
ccwb quota unblock john.doe@company.com --duration 24h
```

### トークン値のショートカット

CLI は読みやすいトークン表記をサポートします。

- `225M` = 225,000,000（2 億 2,500 万）— 既定上限
- `500K` = 500,000（50 万）
- `1B` = 1,000,000,000（10 億）

### JWT クレームからのグループ所属

本システムは JWT トークンのクレームからグループ所属を自動抽出します。

- `groups`: 標準の groups クレーム
- `cognito:groups`: Amazon Cognito の groups
- `custom:department`: カスタム部門クレーム（グループとして扱う）

IdP が発行する JWT にグループクレームを含めるよう、IdP 側設定を行ってください。

## アラート管理

デプロイ後、通知を受け取るために SNS トピックを購読（subscribe）します。

```bash
# スタック出力からトピック ARN を取得
aws cloudformation describe-stacks --stack-name <quota-stack-name> \
  --query 'Stacks[0].Outputs[?OutputKey==`QuotaAlertTopicArn`].OutputValue' \
  --output text

# 購読（email / SMS / HTTPS webhook など）
aws sns subscribe --topic-arn <arn> --protocol email --notification-endpoint admin@company.com
```

### アラート種別

本システムは 2 種類の上限タイプについて、各 3 段階のしきい値でアラートを送ります。

#### 月次トークンアラート

月次トークン使用量が月次上限の 80%／90%／100% を超えた時に送信されます。

#### 日次トークンアラート

日次トークン使用量が日次上限の 80%／90%／100% を超えた時に送信されます。日次アラートは日付を重複排除キーに含むため、日ごとに送信され得ます。

### アラート内容の例

```
Subject: Claude Code CRITICAL - Monthly Token Quota - 92%

Claude Code Usage Alert - Monthly Token Quota

User: john.doe@company.com
Alert Level: CRITICAL
Month: November 2025
Policy: group:engineering

Current Usage: 207,000,000 tokens
Monthly Limit: 225,000,000 tokens
Percentage Used: 92.0%

Days Remaining in Month: 8
Daily Average: 9,409,091 tokens
Projected Monthly Total: 282,272,727 tokens

---
This alert is sent once per threshold level per month.
```

アラートは重複排除され、しきい値ごとに「ユーザー×期間」あたり 1 回だけ送信されます。履歴は DynamoDB に保存され（TTL 60 日）、自動的にクリーンアップされます。

## ユーザー通知

ユーザーが上限に近づく／超過すると、ターミナルとブラウザの両方で視覚的通知が表示されます。

### ブラウザ通知

credential provider は次の場合に、クォータ状態を示すブラウザページを開きます。

| 条件 | ブラウザが開くか | アクセス許可 |
|---|---|---|
| 上限内（<80%） | いいえ | はい |
| 警告（80～99%） | はい（黄色） | はい |
| ブロック（100%+） | はい（赤） | いいえ |

ブラウザページの表示内容：
- **ステータス見出し**: Warning（⚠️）または Blocked（🚫）
- **月次使用量**: 進捗バー（% 表示）
- **日次使用量**: 進捗バー（% 表示、日次上限設定時）
- **メッセージ**: 説明とガイダンス

### ターミナル出力

ブラウザ通知に加えて、ターミナルにも表示されます。

**警告（使用率 80%+）:**
```
============================================================
QUOTA WARNING
============================================================
  Monthly: 180,000,000 / 225,000,000 tokens (80.0%)
  Daily: 6,600,000 / 8,250,000 tokens (80.0%)
============================================================
```

**ブロック（使用率 100%+）:**
```
============================================================
ACCESS BLOCKED - QUOTA EXCEEDED
============================================================

Monthly quota exceeded: 225,000,000 / 225,000,000 tokens (100.0%).
Contact your administrator for assistance.

Current Usage:
  Monthly: 225,000,000 / 225,000,000 tokens (100.0%)

Policy: user:john.doe@company.com

To request an unblock, contact your administrator.
============================================================
```

### 定期的なクォータ再チェック

既定では、認証情報がキャッシュされている場合でも 30 分ごとにクォータを再チェックします。これにより、ユーザーがブロックされた後も最大 12 時間（認証情報キャッシュ期間）作業を続けられてしまうギャップを縮小します。

`ccwb init` で設定します。

| 間隔 | チェック頻度 | 最大の強制遅延 | UX への影響 |
|---|---|---|---|
| 0 | 毎リクエスト | 即時 | リクエストあたり約 200ms |
| 15 | 15 分ごと | 15 分 | 最小 |
| 30（既定） | 30 分ごと | 30 分 | ほぼ無視できる |
| 60 | 1 時間ごと | 1 時間 | なし |

**動作:**

1. ユーザーが認証情報を要求（キャッシュ／新規）
2. 前回のクォータチェックから `interval` 分を超えていれば:
   - クォータ API を呼び出し（約 200ms）
   - タイムスタンプ更新
3. ブロックなら: ブラウザ通知を表示し、認証情報を拒否
4. 警告（80%+）なら: ブラウザ通知を表示し、認証情報を発行
5. OK なら: 何も表示せず認証情報を発行

**トレードオフ:**

- **Interval = 0**（最も厳格）: 毎回クォータをチェック。credential 要求ごとに約 200ms の遅延。即時強制が必須な場合に。
- **Interval = 30**（推奨）: 強制の厳しさと UX のバランス。上限超過から 30 分以内にブロック。
- **Interval = 60+**（緩め）: 影響は最小だが、超過後 1 時間程度作業できる可能性。

キャッシュ返却時にもバックグラウンドでチェックし、ステータスが変わった場合のみブラウザ通知が表示されます。

## ポリシーの一括管理

ユーザー数が多い組織向けに、CLI は import/export でポリシーを一括管理できます。

### ポリシーのエクスポート

バックアップ、監査、移行のため、既存ポリシーを JSON または CSV にエクスポートします。

```bash
# 全ポリシーを JSON でエクスポート
ccwb quota export policies.json

# スプレッドシート編集用に CSV でエクスポート
ccwb quota export policies.csv

# user ポリシーのみエクスポート
ccwb quota export users.json --type user
```

### ポリシーのインポート

ファイルからポリシーをインポートします。

```bash
# CSV からインポート（新規作成＋既存更新）
ccwb quota import users.csv --update

# 適用せずにプレビュー
ccwb quota import users.csv --dry-run

# 日次上限を自動算出（月次/30 + バーストバッファ）
ccwb quota import users.csv --auto-daily --burst 15
```

### CSV テンプレート

次の列を持つ CSV を作成します。

```csv
type,identifier,monthly_token_limit,daily_token_limit,enforcement_mode,enabled
user,alice@example.com,300M,15M,alert,true
user,bob@example.com,200M,,block,true
group,engineering,500M,25M,alert,true
default,default,225M,8M,alert,true
```

**必須列:** `type`, `identifier`, `monthly_token_limit`

**トークン形式:** `K`（千）、`M`（百万）、`B`（十億）をサポート。例: `300M` = 300,000,000 tokens

### 典型的な運用フロー

1. **人事システムから初期投入:**
   ```bash
   # HR からユーザー一覧を出し、CSV を作る
   ccwb quota import users.csv --auto-daily --update
   ```

2. **変更前のバックアップ:**
   ```bash
   ccwb quota export backup-$(date +%Y%m%d).json
   ```

3. **環境間同期:**
   ```bash
   # staging からエクスポート
   ccwb quota export policies.json --profile staging

   # production にインポート
   ccwb quota import policies.json --profile production --update
   ```

詳細は [CLI Reference](CLI_REFERENCE.md#quota-export---export-policies) を参照してください。

## トラブルシューティング

### クイックチェック

```bash
# Lambda ログを確認
aws logs tail /aws/lambda/claude-code-quota-monitor --follow

# ユーザークォータを照会
aws dynamodb scan --table-name UserQuotaMetrics \
  --projection-expression "email, total_tokens, daily_tokens"

# クォータポリシー一覧
aws dynamodb scan --table-name QuotaPolicies \
  --filter-expression "sk = :current" \
  --expression-attribute-values '{":current": {"S": "CURRENT"}}'
```

### よくある問題

- **アラートが来ない**: SNS 購読が承認済みであること、EventBridge ルールが有効であることを確認
- **ユーザーが欠ける**: JWT トークンに email クレームが含まれているか確認
- **誤ったポリシーが適用される**: JWT にグループクレームが入っているか確認
- **グループが検出されない**: `ENABLE_FINEGRAINED_QUOTAS` が `true` か確認

モニタリング全体の詳細は [Monitoring Guide](MONITORING.md) を参照してください。

## コスト面の考慮

**1000 ユーザー未満の月額想定: $2～$10**
- Lambda: 約 2,880 回 × $0.0000002 = $0.58
- DynamoDB: ユーザー数 × 2,880 操作の従量課金
- SNS: 通知 100 万件あたり $0.50
- CloudWatch Logs: 標準保持の料金
- QuotaPolicies テーブル: ほぼ無視できる（ポリシーは頻繁に変わらない）

## データスキーマ

### UserQuotaMetrics テーブル

**ユーザー合計**: `PK: USER#{email}`, `SK: MONTH#{YYYY-MM}`
- 属性: `total_tokens`, `daily_tokens`, `daily_date`, `input_tokens`, `output_tokens`, `cache_tokens`, `groups`, `last_updated`, `email`
- TTL: 翌月末

**アラート履歴**: `PK: ALERTS`, `SK: {YYYY-MM}#ALERT#{email}#{type}#{level}[#{date}]`
- 属性: `sent_at`, `alert_type`, `alert_level`, `usage_at_alert`, `policy_info`
- TTL: 60 日

### QuotaPolicies テーブル

**ポリシーレコード**: `PK: POLICY#{type}#{identifier}`, `SK: CURRENT`
- 属性: `policy_type`, `identifier`, `monthly_token_limit`, `daily_token_limit`, `warning_threshold_80`, `warning_threshold_90`, `enforcement_mode`, `enabled`, `created_at`, `updated_at`, `created_by`

**GSI: PolicyTypeIndex**
- PK: `policy_type`（user / group / default）
- SK: `identifier`
- 「全 group ポリシー一覧」などの効率的クエリに使用

## 基本クォータからの移行

基本クォータ（単一のグローバル上限）からアップグレードする場合:

1. 更新された CloudFormation スタックをデプロイ（QuotaPolicies テーブルが追加されます）
2. 既存の UserQuotaMetrics データは引き続き動作（新フィールドは nullable）
3. スタックパラメータで `EnableFinegrainedQuotas: true` を設定
4. 必要なら、従来挙動を維持するためデフォルトポリシーを作成:
   ```bash
   ccwb quota set-default --monthly-limit 225M
   ```
5. 必要に応じて group/user ポリシーを段階的に追加

**破壊的変更なし** — これはポリシー作成により opt-in できる拡張です。

## アクセスブロック（Phase 2）

ポリシーの `enforcement_mode` が `"block"` の場合、ユーザーが上限を超えると認証情報の発行を拒否します。

### ブロックの仕組み

1. **Quota Check API**: 認証情報発行前に、ユーザークォータをリアルタイムに検査する API エンドポイント
2. **強制ポイント**: credential provider が OIDC 認証後に Quota Check API を呼び出す
3. **ブロック条件**: 次を満たすとブロック
   - 月次使用量 ≥ `monthly_token_limit`
   - 日次使用量 ≥ `daily_token_limit`（設定されている場合）

### ブロッキングの設定

ポリシーに block を設定します。

```bash
# user ポリシーを block で設定
ccwb quota set-user john.doe@company.com --monthly-limit 10M --enforcement block

# group ポリシーを block で設定
ccwb quota set-group engineering --monthly-limit 50M --enforcement block

# default を block で設定
ccwb quota set-default --monthly-limit 225M --enforcement block
```

### 管理者による上書き（unblock）

クォータ超過ユーザーを一時的に解除できます。

```bash
# 24 時間（既定）
ccwb quota unblock john.doe@company.com

# 7 日
ccwb quota unblock john.doe@company.com --duration 7d

# 月末（リセット）まで
ccwb quota unblock john.doe@company.com --duration until-reset

# 理由付き
ccwb quota unblock john.doe@company.com --duration 24h --reason "Urgent project deadline"
```

unblock レコードは期限切れ後、DynamoDB TTL により自動削除されます。

### エラーハンドリング: フェイルオープン vs フェイルクローズ

既定では **fail-open**（クォータチェック API が落ちている場合は許可）です。ネットワーク問題で業務が止まることを防ぎます。

プロファイル設定で変更できます。

```json
{
  "quota_fail_mode": "open"   // エラー時に許可（既定）
  // または
  "quota_fail_mode": "closed" // エラー時に拒否（より厳格）
}
```

15 分ごとの Lambda 監視ジョブは独立して動作するため、リアルタイムチェックが失敗してもアラート送信は継続されます。

### Quota Check API

Quota Check API は、認証情報発行前にユーザーのクォータを検査する保護された HTTP エンドポイントです。

#### API のセキュリティ

API は OIDC プロバイダーのトークンを使った JWT 認証を必須とします。

- **認証**: `Authorization: Bearer <token>` ヘッダーの JWT
- **検証**: API Gateway の JWT Authorizer が OIDC プロバイダーに対してトークンを検証
- **ユーザー識別**: 検証済み JWT クレームから email と group を抽出（クエリパラメータは使わない）

これにより以下が保証されます。
- 認証済みユーザーのみがクォータチェック可能
- ユーザー ID を偽装できない（検証済みクレーム由来）
- 追加の認証情報が不要（認証フローの同一 OIDC トークンを利用）

#### デプロイ設定

`ccwb deploy quota` を使う場合、OIDC 設定は `ccwb init` で設定したプロファイルから **自動的に引き渡される**ため、手動のパラメータ指定は不要です。

CloudFormation を手動デプロイする場合は、OIDC 設定を渡します。

```bash
aws cloudformation deploy \
  --stack-name claude-code-quota \
  --template-file quota-monitoring.yaml \
  --parameter-overrides \
    OidcIssuerUrl="https://company.okta.com" \
    OidcClientId="your-client-id" \
    # ... other parameters
```

OIDC パラメータは credential provider の設定と一致している必要があります。
- `OidcIssuerUrl`: IdP の issuer URL（Okta 例: `https://company.okta.com`）
- `OidcClientId`: IdP で設定した Client ID

デプロイ後、スタック出力から API エンドポイントを取得します。

```bash
# Quota Check API エンドポイントを取得
aws cloudformation describe-stacks --stack-name <quota-stack-name> \
  --query 'Stacks[0].Outputs[?OutputKey==`QuotaCheckApiEndpoint`].OutputValue' \
  --output text
```

credential provider の config.json にエンドポイントを設定します。

```json
{
  "profiles": {
    "ClaudeCode": {
      "quota_api_endpoint": "https://xxx.execute-api.us-east-1.amazonaws.com"
    }
  }
}
```

#### API 応答

| シナリオ | HTTP ステータス | 応答 |
|---|---:|---|
| JWT なし／不正 | 401 | Unauthorized（API Gateway が拒否） |
| JWT 有効、クォータ OK | 200 | `{"allowed": true, ...}` |
| JWT 有効、クォータ超過 | 200 | `{"allowed": false, "reason": "monthly_exceeded", ...}` |
| JWT 有効、email クレームなし | 200 | `{"allowed": true, "reason": "missing_email_claim"}`（fail-open） |

### 強制のタイミング

**重要**: クォータ強制は「認証情報の発行時」にのみ行われ、アクティブセッション中には行われません。

ユーザーがセッション中にクォータを超過した場合でも、認証情報が期限切れになって再認証が必要になるまで、Claude Code を使い続けられます。その時点でクォータチェックによりアクセスがブロックされます。

#### タイムライン例（12 時間セッション）

```
09:00 - ユーザーが認証、クォータチェック通過（上限の 50%）
09:00 - AWS 認証情報発行（12 時間有効）
15:00 - 月次クォータ 100% 超過
15:01 - それでも作業は継続（認証情報がまだ有効）
21:00 - 認証情報期限切れ、再認証が必要
21:00 - クォータチェックでアクセスをブロック（ここで初めて強制）
```

この例では、超過（15:00）から強制（21:00）まで 6 時間のギャップがあります。

#### 厳密な強制の推奨

ブロックを有効にする場合、`max_session_duration` を短くすることを推奨します。

| セッション期間 | 強制ギャップ | 利用場面 |
|---|---|---|
| 12h（既定） | 最大 12 時間 | alert-only モード |
| 4h | 最大 4 時間 | 中程度の強制 |
| 1h（推奨） | 最大 1 時間 | 厳格なコスト制御 |

プロファイルで設定します。

```json
{
  "profiles": {
    "ClaudeCode": {
      "max_session_duration": 3600,
      "quota_api_endpoint": "https://xxx.execute-api.us-east-1.amazonaws.com"
    }
  }
}
```

**トレードオフ**: セッションを短くすると再認証が増え、ユーザーのプロンプト表示回数が増えますが、クォータ強制はより厳密になります。

## 現在の制約

- クォータは暦月／日（UTC）でリセットされます
- JWT に email クレームが必要です
- グループ所属には IdP からの JWT グループクレームが必要です
- 強制は認証情報発行時のみ（緩和策は [強制のタイミング](#強制のタイミング) 参照）

## 今後の拡張

- **一括 import/export**: JSON ファイルでポリシー管理
- **クォータレポート**: 全ユーザーの使用レポート生成

## 統合ポイント

- **Dashboard**: DynamoDB のメトリクステーブルと OTEL パイプラインを共有
- **Analytics**: クォータデータは Athena クエリで利用可能（[Analytics Guide](ANALYTICS.md) 参照）
- **外部システム**: SNS トピックは webhook、Lambda トリガー、サードパーティ統合をサポート
- **ID プロバイダー**: グループ所属は JWT クレームから抽出

モニタリングの全体セットアップと一般的なテレメトリ情報は [Monitoring Guide](MONITORING.md) を参照してください。
