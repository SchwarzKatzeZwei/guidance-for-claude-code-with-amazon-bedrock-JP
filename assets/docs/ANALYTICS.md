# Claude Code 分析パイプライン

このディレクトリには、Claude Code の利用メトリクスを追跡するための分析パイプラインをセットアップする CloudFormation テンプレートが含まれています。

## 概要

分析パイプラインは、次のコンポーネントで構成されます。

- **Kinesis Data Firehose**: CloudWatch Logs を Parquet 形式で S3 にストリーミング
- **S3 データレイク**: 履歴メトリクスデータを保存し、自動アーカイブを実施
- **AWS Athena**: メトリクスデータに対する SQL クエリを可能にする
- **パーティションプロジェクション（Partition Projection）**: Glue クローラーを不要にする

![概要](../images/otel-monitoring-flow.png)

## デプロイ

### 前提条件

1. 適切な認証情報で設定済みの AWS CLI
2. Claude Code の OTEL コレクターがすでにデプロイされ、メトリクスを CloudWatch Logs に送信していること

### 分析パイプラインをデプロイ

```bash
# 分析パイプラインをデプロイ
aws cloudformation deploy \
  --template-file analytics-pipeline.yaml \
  --stack-name claude-code-analytics \
  --capabilities CAPABILITY_IAM

# Athena コンソール URL を取得
aws cloudformation describe-stacks \
  --stack-name claude-code-analytics \
  --query 'Stacks[0].Outputs[?OutputKey==`AthenaConsoleUrl`].OutputValue' \
  --output text
```

### モニタリングダッシュボードを更新

```bash
# ダッシュボードを更新し、ハードコードされたユーザーを削除
aws cloudformation deploy \
  --template-file monitoring-dashboard.yaml \
  --stack-name claude-code-auth-dashboard \
  --parameter-overrides TokenCostPerMillion=15.0
```

## Athena を使ったユーザー分析

### Athena コンソールへのアクセス

1. スタック出力で提供される Athena コンソール URL に移動します
2. スタックが作成したワークグループ（例: `claude-code-analytics-workgroup`）を選択します
3. データベース（例: `claude_code_analytics_analytics`）を選択します
4. Athena コンソールの「Saved queries」タブから保存済みクエリにアクセスします

### 事前作成済みの名前付きクエリ

このスタックは、ワークグループに紐づく **10 個の名前付きクエリ**を自動作成します。これらのクエリにより、包括的な分析が可能になります。

#### 1. トークン使用量に基づく上位ユーザー
直近 7 日間におけるトークン消費量上位 10 ユーザーを特定し、ユーザーのメールアドレス、組織、セッション数、推定コストを含めて表示します。

**利用場面:** パワーユーザーの把握と利用パターンの追跡。

#### 2. モデル別・種別別のトークン使用量
モデル（Opus / Sonnet / Haiku）およびトークン種別（入力／出力）ごとにトークン使用状況を分析し、推定コストも算出します。

**利用場面:** モデル選択の最適化、コスト分布の把握。

#### 3. ユーザー活動パターン
ユーザー活動を「時刻（時間帯）」別に示し、ピーク利用時間を特定します。

**利用場面:** キャパシティ計画、ユーザーが最も活動的な時間帯の把握。

#### 4. 組織別のトークン使用量
組織ごとのトークン使用量を、ユーザー数およびコスト配賦とともに追跡します。

**利用場面:** 組織単位の請求／チャージバック。

#### 5. メールドメイン別のトークン使用量
メールドメイン別に利用状況を分析し、ユーザー属性（所属傾向）を把握します。

**利用場面:** どのチーム／部門が利用しているかの把握。

#### 6. 詳細 TPM / RPM 分析
レートリミット監視のために、Tokens Per Minute（TPM）および Requests Per Minute（RPM）を算出します。

**利用場面:** API 利用パターンの監視、レート制限問題の予防。

#### 7. ユーザーセッション分析
セッション継続時間、強度、使用モデル、セッション単位のコストを含めてユーザーセッションを分析します。

**利用場面:** ユーザー行動とセッション特性の理解。

#### 8. 詳細コスト配賦
ユーザー／組織／モデル別の正確なコスト計算を提供し、累積追跡を行います。

**利用場面:** 正確な課金とコスト管理。

#### 9. ピーク利用とレートリミット分析
ピーク利用期間を特定し、レートリミットに近づいているタイミングを可視化します。

**利用場面:** サービス中断を防ぐための予防的監視。

#### 10. ID プロバイダー別の利用分析
異なる ID プロバイダー（Okta / Auth0 / Cognito）間で利用パターンを比較します。

**利用場面:** 認証方式別の利用状況把握。

### クエリの使い方

Athena コンソールでワークグループとデータベースを選択したら、次の手順で実行します。

1. **保存済みクエリにアクセス**: 「Saved queries」タブをクリック
2. **クエリを読み込み**: 10 個の事前作成済みクエリのいずれかを選択し、クエリエディタに読み込む
3. **クエリを実行**: 「Run」をクリックして、現在のデータに対して実行
4. **結果をエクスポート**: 追加分析のために CSV としてダウンロード

### クエリのカスタマイズ

#### 期間（タイムレンジ）の調整

任意のクエリの WHERE 句を修正して、対象期間を変更します。

```sql
-- 直近 24 時間
WHERE from_unixtime(timestamp/1000) >= CURRENT_TIMESTAMP - INTERVAL '24' HOUR

-- 直近 7 日
WHERE year >= YEAR(CURRENT_DATE - INTERVAL '7' DAY)
    AND from_unixtime(timestamp/1000) >= CURRENT_TIMESTAMP - INTERVAL '7' DAY

-- 直近 30 日
WHERE year >= YEAR(CURRENT_DATE - INTERVAL '30' DAY)
    AND from_unixtime(timestamp/1000) >= CURRENT_TIMESTAMP - INTERVAL '30' DAY

-- 特定期間
WHERE from_unixtime(timestamp/1000) BETWEEN TIMESTAMP '2024-01-01' AND TIMESTAMP '2024-01-31'
```

#### 特定ユーザー／組織でフィルタする

追加の WHERE 条件で対象を絞り込みます。

```sql
-- メールドメインでフィルタ
AND user_email LIKE '%@example.com'

-- 組織でフィルタ
AND organization_id = 'your-org-id'

-- 特定モデルでフィルタ
AND model LIKE '%opus%'
```

## データ保持（リテンション）

- **S3 Standard**: 90 日（`DataRetentionDays` パラメータで変更可能）
- **S3 Glacier**: 90 日後（自動移行）
- **Athena クエリ結果**: 7 日（自動削除）

## コスト最適化

1. **パーティションプロジェクション**: Glue クローラー実行が不要
2. **Parquet 形式**: 列指向ストレージによりクエリコストを削減
3. **S3 ライフサイクル**: Glacier への自動アーカイブ
4. **クエリ結果キャッシュ**: Athena が結果を 7 日間キャッシュ

### クエリ性能

- WHERE 句でパーティション列（year, month, day, hour）を使用する
- 対象期間を絞ってスキャン量を減らす
- 探索的クエリでは LIMIT を使用する
