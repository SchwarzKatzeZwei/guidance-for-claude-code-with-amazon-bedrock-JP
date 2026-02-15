# Claude Code モニタリング実装

本ガイドでは、Amazon Bedrock を通じた Claude Code の利用状況を追跡するための、任意（オプション）のモニタリングシステムをデプロイし利用する方法を説明します。

デプロイ時にモニタリングを有効にすると、Claude Code からの利用状況メトリクスを収集して可視化するためのインフラが作成されます。モニタリングスタックは、AWS ECS Fargate 上に OpenTelemetry（OTEL）Collector をデプロイし、Claude Code からメトリクスを受信して CloudWatch に転送し、可視化と分析を可能にします。

## アーキテクチャ

モニタリングシステムはいくつかのコンポーネントが連携して動作します。Claude Code は OpenTelemetry Protocol（OTLP）でメトリクスを Application Load Balancer（ALB）に送信します。ALB はこれらのメトリクスを ECS Fargate 上で稼働する OTEL Collector に転送します。collector はメトリクスを CloudWatch の Embedded Metric Format（EMF）に変換して CloudWatch Metrics と Logs に送信します。最後に CloudWatch ダッシュボードがこれらのメトリクスを可視化します。

## 実装詳細

モニタリング基盤は、メトリクス収集と可視化を担うために複数の AWS リソースをデプロイします。

中核コンポーネントは、AWS Distro for OpenTelemetry（ADOT）Collector イメージを使った ECS Fargate サービスとして動作します。このサービスは VPC 内のプライベートサブネットで、最小リソース（0.25 vCPU / 0.5 GB メモリ）で稼働します。CloudFormation テンプレートには CPU 使用率に基づく 1～3 タスクのオートスケーリング設定が含まれていますが、この機能はアカウント内に ECS のサービスリンクロールが作成されていることを前提とします。

ECS サービスの前段には Application Load Balancer が配置され、ポート 4318 で OTLP メトリクスを受信します。ALB は HTTP と HTTPS の両プロトコルをサポートします。デプロイ時にカスタムドメイン名を指定すると、システムは ACM 証明書を自動作成し、HTTPS を構成します。ヘルスチェックは root エンドポイントを通じて collector の可用性を監視します。

CloudWatch ダッシュボードは、Claude Code の利用状況を包括的に可視化します。ダッシュボードは Lambda 関数と DynamoDB を用いて効率的にメトリクスを収集・表示し、カスタムウィジェットでリアルタイムおよび履歴データを提示します。

### 設定

OTEL Collector の設定は、メトリクスがシステム内をどのように流れるかを定義します。collector はポート 4318 で OTLP トラフィックを待ち受け、CloudWatch に送信する前に 60 秒ごとにメトリクスをバッチ処理します。

設定には attributes processor が含まれており、OTEL helper バイナリが送信する HTTP ヘッダーからユーザー情報を抽出します。これらのヘッダーには JWT トークン由来のユーザー詳細（メールアドレス、ユーザー ID、部門、チーム、コストセンター、その他の組織属性）が含まれます。collector はこれらのヘッダーをリソース属性へマッピングし、CloudWatch のディメンションとして利用できるようにします。

Claude Code は、collector が処理する複数種のメトリクスを送信します。

- `claude_code.token.usage` - 入力／出力トークン消費を追跡
- `claude_code.session.count` - アクティブセッション数をカウント
- `claude_code.active_time.total` - Claude Code を能動的に使用した時間を測定
- `claude_code.cost.usage` - トークン使用量に基づくコスト推定
- `claude_code.code_edit_tool.decision` - コード編集の意思決定を記録

## 利用クォータ監視

モニタリングシステムは、ユーザーがトークン使用量の上限に近づいた／超過した際に管理者へ通知するための任意のクォータ追跡をサポートします。これによりコスト管理が容易になり、想定外の超過を防げます。

クォータ監視は、ダッシュボード基盤と統合する別の CloudFormation スタックとしてデプロイされます。有効化すると、ユーザーごとの月次トークン消費を追跡し、しきい値超過時に Amazon SNS で自動アラートを送信します。

> **詳細**: クォータ監視のセットアップ、設定、利用手順の全体は [Quota Monitoring Guide](QUOTA_MONITORING.md) を参照してください。

## 分析パイプライン（任意）

CloudWatch によるリアルタイム監視に加えて、高度なレポーティングと履歴分析のために分析パイプラインを有効化できます。分析スタックは、長期保存と分析のためのデータレイクを作成します。

分析パイプラインは Kinesis Data Firehose を使って CloudWatch Logs を S3 にストリーミングし、効率的なクエリのためにメトリクスを Parquet 形式へ変換します。S3 データレイクは古いデータを自動的に Glacier にアーカイブし、長期保存コストを抑えます。AWS Athena はメトリクスデータに対する SQL クエリを提供し、Glue クローラーを不要にする自動パーティションプロジェクションを備えています。

このアーキテクチャにより、強力な機能が実現できます。ユーザー単位のトークン使用量推移の追跡、数か月分の履歴データの効率的クエリ、ユーザー／部門／プロジェクト別のコスト配賦、標準 SQL によるカスタムレポート作成などです。また、トークン消費上位ユーザーの特定、モデル別・種別別のトークン使用分析、時間帯別のユーザー活動パターン理解、使用傾向に基づくコスト予測など、一般的な分析タスク向けの事前作成クエリも含まれます。

## デプロイ手順

モニタリングのデプロイは、`poetry run ccwb init` を実行する初期セットアップ中に行います。対話型ウィザードがモニタリングの有効化と必要インフラの設定を促します。

```bash
poetry run ccwb init
```

モニタリングの質問で「yes」を選ぶと、追加の設定オプションが表示されます。新しい VPC を作成するか、既存 VPC を利用するかを選べます。既存 VPC を使う場合は、VPC ID と、Application Load Balancer 用に少なくとも 2 つのサブネットを選択します。

デプロイでは、モニタリング基盤一式が作成されます。（既存 VPC を使わない場合）パブリック／プライベートサブネットを持つ VPC、OTEL Collector の ECS クラスターとタスク定義、collector サービス本体、メトリクス受信用の Application Load Balancer、ログ／メトリクス保存用の CloudWatch Log Group です。

セットアップ時にカスタムドメイン名とホストゾーン ID を指定すると、ACM 証明書が自動的にプロビジョニングされ HTTPS が構成されます。これにより、Claude Code から collector へのメトリクス送信が暗号化されます。

ダッシュボードスタックは、クォータ監視を支えるメトリクス集約インフラを作成します。クォータ監視を別スタックとしてデプロイする場合も、ダッシュボードのメトリクステーブルと統合してユーザー消費量を追跡します。

## Claude Code の設定

package コマンドは、配布パッケージ内に `claude-settings/settings.json` ファイルを生成し、テレメトリ収集のための Claude Code 設定を行います。インストール時にこのファイルがユーザーのホームディレクトリ `~/.claude/settings.json` にコピーされ、モニタリングに必要な設定がすべて含まれます。

```json
{
  "env": {
    "CLAUDE_CODE_USE_BEDROCK": "1",
    "AWS_PROFILE": "ClaudeCode",
    "AWS_REGION": "us-east-1",
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp",
    "OTEL_LOGS_EXPORTER": "otlp",
    "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
    "OTEL_EXPORTER_OTLP_ENDPOINT": "http://otel-collector-alb-xxxxx.us-east-1.elb.amazonaws.com",
    "OTEL_RESOURCE_ATTRIBUTES": "department=engineering,team.id=default,cost_center=default,organization=default"
  },
  "otelHeadersHelper": "~/claude-code-with-bedrock/otel-helper"
}
```

この設定は Bedrock 利用を有効化し、認証用の AWS プロファイルを設定します。テレメトリ収集を有効化し、OTLP エクスポーターがデプロイ済み collector エンドポイントへメトリクスを送信するよう構成します。OTEL の resource attributes は、環境変数で上書き可能なデフォルトの組織タグを提供します。

`otelHeadersHelper` は、インストールされた OTEL helper バイナリを指します。このヘルパーは認証プロセスが保存した JWT トークンからユーザー情報を抽出し、各メトリクスとともに HTTP ヘッダーとして送信します。OTEL Collector はこれらのヘッダーを CloudWatch のディメンションに変換し、ユーザー単位の帰属（attribution）を可能にします。

## 収集されるメトリクス

モニタリングシステムは Claude Code の利用状況を包括的に追跡します。各メトリクスにはユーザー属性および組織属性が付与され、詳細な分析が可能です。

トークン使用量については、リクエストごとの入力トークンを示す `claude.tokens.input`、生成された出力トークンの `claude.tokens.output`、合算の `claude.tokens.total` を追跡します。これらは消費パターンとコストの理解に役立ちます。

リクエストメトリクスとしては、API 呼び出し回数の `claude.requests.count`、応答時間（ミリ秒）を測る `claude.requests.duration`、失敗リクエストを監視する `claude.requests.errors` を収集します。これにより性能問題やエラーパターンを特定できます。

各メトリクスには、フィルタや集計に使える複数のディメンションが含まれます。`UserEmail` ディメンションは OIDC トークン由来で、ユーザー単位の消費量を追跡できます。`Model` ディメンションは使用された Claude モデル（例: claude-3-sonnet、claude-3-opus）を示します。`Region` ディメンションは Bedrock にアクセスした AWS リージョンを示します。

組織ディメンションは、追加の文脈を提供します。`department` は部門単位のグルーピング、`team.id` は部門内のチーム識別、`cost_center` は請求目的のコスト配賦に使えます。さらに `organization`、`location`、`role` などのディメンションにより、より細かな分類も可能です。

## CloudWatch ダッシュボード

`ClaudeCodeMonitoring` という名前の CloudWatch ダッシュボードは、Claude Code メトリクスを包括的に可視化します。

![Claude Code Monitoring Dashboard](/assets/images/ClaudeCodeDashboard.png)  
_全メトリクスを表示するダッシュボード全体像_

## エンドユーザー体験

エンドユーザー視点では、モニタリングは追加設定なしで自動的に動作します。

インストール中に `install.sh` が Claude Code 設定および OTEL helper バイナリを含む必要ファイル一式をコピーします。ユーザーが何か設定する必要はありません。モニタリング設定は、組織の collector エンドポイントが事前設定された状態で配布されます。

ユーザーが Claude Code を利用している間、メトリクスはバックグラウンドで送信され、性能や体験に影響を与えません。OTEL helper バイナリが認証トークンからユーザー情報を自動抽出し、メトリクスに付与して帰属情報を提供します。

モニタリング実装ではプライバシーも重視しています。収集するのはトークン数や応答時間などの利用状況メトリクスのみで、会話内容は送信も保存もしません。組織レポートでの帰属のためメトリクスにユーザーのメールアドレスが含まれますが、メールベースの識別が不適切なケース向けに、ハッシュ化されたユーザー ID も生成します。

## Bedrock API のモニタリング

認証スタックは、AWS CloudTrail により Bedrock API 呼び出しを追跡し、監査証跡と追加のコスト監視機能を提供することもできます（任意）。

CloudTrail の追跡では、すべての Bedrock モデル呼び出しを記録し、90 日保持で S3 に詳細ログを保存します。これらのイベントは `/aws/bedrock/cognito-access` として CloudWatch Logs にもストリーミングされ、リアルタイム分析が可能になります。これにより、誰がいつどのモデルにアクセスしたかの完全な監査証跡が得られます。

モニタリングダッシュボードにはコスト関連機能もあります。別途、Bedrock サービスの AWS Billing 課金を追跡する Bedrock コストダッシュボードがあります。メインダッシュボードは、トークン使用量に基づき（既定は 100 万トークンあたり $15 の価格設定で）コストを推定します。リアルタイムのコストウィジェットにより、本日・今週・今月の支出を表示できます。

### データプライバシー

本システムは利用状況メトリクスのみを収集し、ユーザーと Claude の会話内容を取得・送信することはありません。ユーザー帰属は OIDC トークン由来のメールアドレスで行われ、過剰なデータ収集なしに明確な説明責任を確保します。CloudWatch は既定で 15 か月メトリクスを保持しますが、保持期間は組織ポリシーに応じて調整できます。帰属に使用するメールアドレス以外の個人識別情報（PII）は送信も保存もしません。

### ネットワークセキュリティ

モニタリング基盤は HTTP と HTTPS の両方をサポートします。本番デプロイでは、セットアップ時にカスタムドメイン名を指定し、ACM 証明書による HTTPS を自動的に有効化することを推奨します。暗号化が不要な開発環境や内部向けデプロイでは HTTP も利用できます。

Application Load Balancer は Claude Code のインストール先からのメトリクスを受信するためインターネット向け（internet-facing）ですが、ECS タスクはセキュリティ強化のためプライベートサブネットで稼働します。セキュリティグループは必要なポートとプロトコルのみにアクセスを制限し、最小権限の原則に従います。

## まとめ

モニタリングシステムは、組織全体における Claude Code の利用状況を包括的に可視化します。デプロイは `ccwb` CLI ツールにより自動化され、最小限の設定で必要なインフラがすべて作成されます。ECS Fargate 上の OTEL Collector がメトリクス収集と変換を担い、CloudWatch が保存と可視化を提供します。

ユーザー帰属は、認証トークンから情報を抽出する OTEL helper バイナリにより自動で行われます。これにより、手動設定なしでユーザー／部門／チームなど組織ディメンション別の詳細な利用追跡が可能になります。

クォータ監視は、ユーザーがトークン使用量上限に近づく／超過する前にプロアクティブにアラートを送信します。SNS による詳細通知により、組織はコストと利用傾向を効果的に管理できます。
