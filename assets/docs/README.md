# ユーザー向けドキュメント

このフォルダには、AWS インフラ上で Claude Code を実装・運用するユーザー向けのドキュメントが含まれています。特に、エンタープライズ認証のデプロイパターンに重点を置いています。

## はじめに

### CLI リファレンス

- **ファイル**: [CLI_REFERENCE.md](./CLI_REFERENCE.md)
- **目的**: ccwb の完全なコマンドリファレンス
- **対象読者**: ソリューションをデプロイする IT 管理者

### デプロイガイド

- **ファイル**: [DEPLOYMENT.md](./DEPLOYMENT.md)
- **目的**: ステップバイステップのデプロイ手順
- **対象読者**: IT 管理者

### アーキテクチャ概要

- **ファイル**: [ARCHITECTURE.md](./ARCHITECTURE.md)
- **目的**: 技術アーキテクチャの詳細
- **対象読者**: 技術チームおよびアーキテクト

### ローカルテスト

- **ファイル**: [LOCAL_TESTING.md](./LOCAL_TESTING.md)
- **目的**: 本番展開前にソリューションをテストする方法
- **対象読者**: IT 管理者

## 運用

### モニタリング設定

- **ファイル**: [MONITORING.md](./MONITORING.md)
- **目的**: CloudWatch モニタリング設定および OpenTelemetry セットアップ
- **対象読者**: モニタリングを管理する IT 管理者

### 分析パイプライン

- **ファイル**: [ANALYTICS.md](./ANALYTICS.md)
- **目的**: Claude Code メトリクス追跡のための分析パイプラインのセットアップと利用方法
- **対象読者**: 利用状況分析を管理する IT 管理者

## プロバイダー設定

### OIDC プロバイダー設定ガイド

- **フォルダ**: [providers/](./providers/)
- **Okta**: [okta-setup.md](./providers/okta-setup.md)
- **Microsoft Entra ID（Azure AD）**: [microsoft-entra-id-setup.md](./providers/microsoft-entra-id-setup.md)
- **Auth0**: [auth0-setup.md](./providers/auth0-setup.md)
- **AWS Cognito User Pool**: [cognito-user-pool-setup.md](./providers/cognito-user-pool-setup.md)
