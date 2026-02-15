> **一部**: [Amazon Bedrock を用いた Claude Code 導入ガイダンス](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock)  
> **目的**: このサブディレクトリには、本番利用可能な Claude Code プラグインが含まれます（認証セットアップとは完全に独立しています）

# Claude Code プラグイン マーケットプレイス

Claude Code 向けの本番利用可能なエージェント、フック、ワークフローを提供します。体系的な開発、ドキュメント、アーキテクチャ、セキュリティなどに特化したツールをまとめた、包括的なプラグイン マーケットプレイスです。

## 🚀 クイックスタート

```bash
# マーケットプレイスを追加
/plugin marketplace add aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock

# 最初のプラグインをインストール（EPCC workflow 推奨）
/plugin install epcc-workflow@aws-claude-code-plugins

# 利用可能なプラグインを対話的に参照
/plugin
```

## 📖 ドキュメント

**プラグインが初めての方**は、まずハンズオンチュートリアルから：
- [EPCC ワークフローを始める](docs/tutorials/getting-started-epcc-workflow.md) - 初心者向け 25 分チュートリアル

**プラグイン設定が必要な方**は、実用ガイドを参照：
- [プラグイン設定 How-To](docs/how-to/configure-plugins.md) - インストール、チーム設定、トラブルシューティング

**すべてのリソースを確認したい方**は、ドキュメントハブへ：
- [ドキュメントハブ](docs/README.md) - 学習パス付きのガイド索引

## 📦 利用可能なプラグイン

### 🔄 epcc-workflow（最初におすすめ）
**EPCC（Explore-Plan-Code-Commit）による体系的な開発ワークフロー**

探索（Explore）と計画（Plan）フェーズを含む、体系的なソフトウェア開発手法を提供します。

**含まれるもの:**
- 探索／計画／実装／コミットの各フェーズ向けに特化した 12 のエージェント
- 4 つのワークフローコマンド（/epcc-explore, /epcc-plan, /epcc-code, /epcc-commit）
- 自動リカバリーフック

**インストール:** `/plugin install epcc-workflow@aws-claude-code-plugins`

**利用場面:** 体系的・手順的な開発アプローチが必要なチーム

---

### 📚 documentation
**Diataxis ドキュメントフレームワーク（完全版）**

チュートリアル、How-to、リファレンス、解説、分析のための 12 の特化エージェントを備え、Diataxis のドキュメント体系を完全に実装します。

**含まれるもの:**
- ドキュメント／分析向けの 12 エージェント
- 5 つのドキュメントコマンド
- Diataxis 準拠の構造

**インストール:** `/plugin install documentation@aws-claude-code-plugins`

**利用場面:** ユーザー志向の包括的ドキュメントが必要なプロジェクト

---

### 🏗️ architecture
**アーキテクチャ設計、レビュー、ドキュメント化**

システムアーキテクチャ設計、C4 図、ADR、アーキテクチャレビューのための包括的ツールキットです。

**含まれるもの:**
- アーキテクチャ／品質分析向けの 10 エージェント
- 3 コマンド（design / review / refactor）
- 3 つの自動化フック

**インストール:** `/plugin install architecture@aws-claude-code-plugins`

**利用場面:** システム設計に取り組むアーキテクトおよびチーム

---

### 🔒 security
**セキュリティスキャンとコンプライアンス自動化**

自動ゲート、脆弱性スキャン、コンプライアンス検証を備えた包括的セキュリティツール群です。

**含まれるもの:**
- セキュリティ／分析向けの 4 エージェント
- 2 コマンド（/security-scan, /permission-audit）
- 自動セキュリティゲートとスクリプト

**インストール:** `/plugin install security@aws-claude-code-plugins`

**利用場面:** セキュリティ重視のチーム、コンプライアンス要件がある場合

---

### ✅ testing
**テスト、QA、品質ゲート**

自動品質ゲート、lint、検証を備えた完全なテスト基盤です。

**含まれるもの:**
- テスト／設計向けの 3 エージェント
- テスト生成コマンド
- Python の lint を含む品質ゲート（Black / Ruff / mypy）

**インストール:** `/plugin install testing@aws-claude-code-plugins`

**利用場面:** QA チーム、TDD 実践者、品質重視の開発

---

### ⚡ performance
**性能プロファイリングと最適化**

性能分析、プロファイリング、最適化、継続的モニタリングのためのツールです。

**含まれるもの:**
- 性能分析向けの 5 エージェント
- 性能分析コマンド
- 性能監視フック

**インストール:** `/plugin install performance@aws-claude-code-plugins`

**利用場面:** 性能が重要なアプリケーション、最適化作業

---

### 🧪 tdd-workflow
**テスト駆動開発（TDD）ワークフロー**

red-green-refactor サイクルを支援する、TDD 向けの特化ワークフローです。

**含まれるもの:**
- TDD／品質分析向けの 6 エージェント
- 2 つの TDD コマンド（/tdd-feature, /tdd-bugfix）
- テストファースト開発パターン

**インストール:** `/plugin install tdd-workflow@aws-claude-code-plugins`

**利用場面:** TDD 実践者、テストファースト開発チーム

---

### 📋 agile-tools
**アジャイルの役割とプロセス**

チーム連携／プロジェクト管理向けに、役割ベースのエージェント一式を提供します。

**含まれるもの:**
- 4 つのアジャイル役割エージェント（スクラムマスター、プロダクトオーナー、ビジネスアナリスト、プロジェクトマネージャー）
- 通知フック

**インストール:** `/plugin install agile-tools@aws-claude-code-plugins`

**利用場面:** アジャイルチーム、プロダクト管理、業務分析

---

### 🎨 ux-design
**UX 最適化と UI デザイン**

アクセシビリティ検証を含む、ユーザー体験／UI 設計ツールです。

**含まれるもの:**
- 2 つのデザインエージェント（UI デザイナー、UX オプティマイザー）
- WCAG アクセシビリティ対応

**インストール:** `/plugin install ux-design@aws-claude-code-plugins`

**利用場面:** フロントエンドチーム、デザイン重視の開発

---

### 🚀 deployment
**デプロイのオーケストレーションと自動化**

デプロイ自動化、段階的ロールアウト、コンプライアンスのための DevOps ツールです。

**含まれるもの:**
- デプロイ用エージェント
- コンプライアンスフック
- 段階的デプロイ戦略

**インストール:** `/plugin install deployment@aws-claude-code-plugins`

**利用場面:** DevOps チーム、CI/CD パイプライン

---

### 🔍 code-analysis
**コード考古学と技術評価**

レガシーシステム分析、技術評価、技術的負債の評価のためのツールです。

**含まれるもの:**
- 2 つの分析エージェント（code archaeologist、tech evaluator）
- レガシーシステム分析

**インストール:** `/plugin install code-analysis@aws-claude-code-plugins`

**利用場面:** レガシー刷新、技術選定・評価

---

## 🎯 推奨プラグインバンドル

### Starter Bundle
Claude Code を導入し始めるチームに最適：
```json
{
  "requiredMarketplaces": ["aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"],
  "requiredPlugins": [
    "epcc-workflow",
    "documentation",
    "security"
  ]
}
```

### Full-Stack Bundle
フルスタック開発向けの包括的ツール：
```json
{
  "requiredPlugins": [
    "epcc-workflow",
    "documentation",
    "architecture",
    "testing",
    "ux-design"
  ]
}
```

### Enterprise Bundle
エンタープライズ向けの完全な開発ツールキット：
```json
{
  "requiredPlugins": [
    "epcc-workflow",
    "security",
    "testing",
    "performance",
    "architecture",
    "deployment",
    "agile-tools"
  ]
}
```

### TDD Bundle
テスト駆動開発に必要な一式：
```json
{
  "requiredPlugins": [
    "tdd-workflow",
    "testing",
    "epcc-workflow"
  ]
}
```

## 🔧 チーム設定

プロジェクトの `.claude/settings.json` に追加します。

```json
{
  "requiredMarketplaces": [
    "aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"
  ],
  "requiredPlugins": [
    "epcc-workflow",
    "security",
    "testing"
  ]
}
```

これにより、チームメンバー全員が自動的にこれらのプラグインを利用できるようになります。

## 📂 リポジトリ構成

```
claude-code-plugins/
├── .claude-plugin/
│   └── marketplace.json       # マーケットプレイスのマニフェスト
├── plugins/
│   ├── epcc-workflow/         # 11 個の特化プラグイン
│   ├── documentation/
│   ├── architecture/
│   ├── security/
│   ├── testing/
│   ├── performance/
│   ├── tdd-workflow/
│   ├── agile-tools/
│   ├── ux-design/
│   ├── deployment/
│   └── code-analysis/
├── docs/                      # 包括的ガイド
└── README.md                  # このファイル
```

## 🎓 学習リソース

### 個人向け
1. 体系的な開発のために `epcc-workflow` から始める
2. 良いドキュメントを書くために `documentation` を追加する
3. 自動セキュリティチェックのために `security` を含める

### チーム向け
1. `.claude/settings.json` に必須プラグインを設定する
2. ワークフローに合うバンドルを選ぶ
3. 必要に応じてプロジェクト単位でカスタマイズする

### エンタープライズ向け
1. 組織全体で security と testing プラグインを展開する
2. 一貫性のために EPCC ワークフローを活用する
3. プロジェクト管理に agile-tools を活用する

## 🤝 コントリビューション

貢献を歓迎します。詳細は [Contributing Guide](CONTRIBUTING.md) をお読みください。

## 📄 ライセンス

本プロジェクトは MIT-0 で提供されます。詳細は [LICENSE](LICENSE) を参照してください。

## 🔗 リンク

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [Plugin Reference](https://docs.claude.com/claude-code/plugins-reference)
- [Marketplace Guide](https://docs.claude.com/claude-code/plugin-marketplaces)
- [Issue Tracker](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/issues)

## ⭐ ハイライト

- **本番利用可能な 11 プラグイン** — 現代的な開発のための包括的ツール群
- **高度なメタデータ** — キーワード、タグ、カテゴリによる高い発見性
- **モジュール設計** — 必要なものだけをインストール可能
- **チームフレンドリー** — 必須プラグインで標準を徹底
- **充実したドキュメント** — 完全なガイドと例
- **実戦で検証済み** — 実証済みパターンとワークフローに基づく

---

**はじめる:** `/plugin marketplace add aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock`
