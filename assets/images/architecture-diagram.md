# アーキテクチャ図

## 1. 認証およびクレデンシャル取得フロー

この図は、一時的な AWS 認証情報を取得し、それを使って Amazon Bedrock にアクセスするまでの全プロセスを示します。

```mermaid
sequenceDiagram
    participant Dev as 開発者
    participant CLI as Claude Code CLI
    participant Cache as ローカル認証情報キャッシュ
    participant Browser as Web ブラウザ
    participant OIDC as OIDC プロバイダ<br/>(Okta/Azure AD/Google)
    participant Cognito as AWS Cognito<br/>Identity Pool
    participant STS as AWS STS
    participant Bedrock as Amazon Bedrock

    Dev->>CLI: aws bedrock-runtime invoke-model
    CLI->>Cache: 有効な認証情報があるか確認
    
    alt 認証情報が未キャッシュ、または期限切れ
        Cache-->>CLI: 有効な認証情報なし
        CLI->>Browser: 認証 URL を開く（localhost:8400）
        Browser->>OIDC: OIDC ログインへリダイレクト
        Dev->>OIDC: 資格情報 + MFA を入力
        OIDC->>Browser: OIDC トークンを返す
        Browser->>CLI: 認可コードを返す
        CLI->>OIDC: 認可コードを ID トークンに交換
        OIDC->>CLI: ID トークンを返す
        CLI->>Cognito: OIDC トークンを交換
        Cognito->>Cognito: OIDC トークンを検証
        Cognito->>STS: AssumeRoleWithWebIdentity
        STS->>Cognito: 一時的な認証情報を返す
        Cognito->>CLI: AWS 認証情報を返す<br/>(AccessKey, SecretKey, SessionToken)
        CLI->>Cache: 認証情報を保存（8 時間）
    else 認証情報がキャッシュ済みで有効
        Cache-->>CLI: キャッシュ済み認証情報を返す
    end
    
    CLI->>Bedrock: 認証情報を用いてモデルを呼び出す
    Bedrock->>Bedrock: IAM 権限を検証
    Bedrock->>CLI: AI 応答を返す
    CLI->>Dev: 応答を表示

    Note over Dev,Bedrock: すべての認証情報は一時的（最大 8 時間）<br/>長期的な API キーは保存しない
```

## 2. OpenTelemetry 監視アーキテクチャ

この図は、ECS Fargate 上の OpenTelemetry Collector を用いた（任意の）監視構成を示します。

```mermaid
flowchart TB
    subgraph "開発者端末"
        CLI1[Claude Code CLI 1]
        CLI2[Claude Code CLI 2]
        CLI3[Claude Code CLI N]
    end

    subgraph "AWS アカウント"
        subgraph "ECS Fargate"
            Collector[OpenTelemetry Collector<br/>コンテナ]
        end
        
        subgraph "CloudWatch"
            Metrics[CloudWatch メトリクス]
            Logs[CloudWatch ログ]
            Dashboard[CloudWatch ダッシュボード]
            Alarms[CloudWatch アラーム]
        end
        
        subgraph "ストレージ"
            S3[S3 バケット<br/>ログアーカイブ]
        end
    end

    CLI1 -->|OTLP/gRPC<br/>ポート 4317| Collector
    CLI2 -->|OTLP/gRPC<br/>ポート 4317| Collector
    CLI3 -->|OTLP/gRPC<br/>ポート 4317| Collector

    Collector -->|メトリクスをエクスポート| Metrics
    Collector -->|ログをエクスポート| Logs
    Collector -->|トレースをエクスポート| Logs

    Metrics --> Dashboard
    Metrics --> Alarms
    Logs --> Dashboard
    Logs -->|アーカイブ| S3

    Alarms -->|通知| SNS[SNS トピック<br/>任意のアラート]

    Note1[認証メトリクス:<br/>- 認証総数<br/>- 認証失敗数<br/>- 認証レイテンシ<br/>- アクティブユーザー数]
    
    Note2[Bedrock 利用メトリクス:<br/>- モデル別 API コール数<br/>- トークン使用量<br/>- エラー率<br/>- 応答時間]

    style Collector fill:#f9f,stroke:#333,stroke-width:2px
    style Dashboard fill:#9f9,stroke:#333,stroke-width:2px
    style Note1 fill:#ffd,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5
    style Note2 fill:#ffd,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5
```

## AWS アーキテクチャアイコン要件

公式の AWS アーキテクチャ図（PNG 形式）を作成する場合:

- AWS Architecture Icons Toolkit の最新版（明るい背景、2023-04-28 リリース）を使用
- サービスアイコンは 0.4"×0.4" 以上、グルーピング用アイコンは 0.3"×0.3" 以上
- すべてのアイコンに下部ラベルを付ける（Arial 9〜12pt、黒）
- サービス名の先頭語と同じ行に "AWS" または "Amazon" を含める
- 矢印は黒の実線（線幅 1.25pt）、斜め線は使用しない
- トリミング、反転、形状変更は禁止

## 主要アーキテクチャ要素

1. **開発者ワークステーション**: Claude Code CLI を実行し、ローカルで認証情報をキャッシュ
2. **OIDC プロバイダ**: エンタープライズ向け IdP（Okta、Azure AD、Google Workspace）
3. **Amazon Cognito Identity Pool**: OIDC トークンを検証し、ID フェデレーションを管理
4. **AWS STS**: AssumeRoleWithWebIdentity により一時的な認証情報を発行
5. **Amazon Bedrock**: 一時的な認証情報でアクセスする対象 AI サービス
6. **AWS CloudTrail**: 認証および API アクセスイベントをすべて記録
7. **Amazon CloudWatch**: （任意）監視ダッシュボードとアラート
8. **Amazon ECS Fargate**: 集約テレメトリのための OpenTelemetry Collector をホスト
