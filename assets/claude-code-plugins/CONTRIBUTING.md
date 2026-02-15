# Claude Code Advanced Patterns へのコントリビューション

Claude Code Advanced Patterns リポジトリへの貢献にご関心をお寄せいただき、ありがとうございます。本ガイドでは、本プロジェクトにコントリビュートするための始め方を説明します。

## 🚀 はじめに

### Fork と Clone

1. GitHub 上でリポジトリを Fork します: https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock  
2. Fork したリポジトリをローカルに clone します:
```bash
git clone https://github.com/YOUR-USERNAME/guidance-for-claude-code-with-amazon-bedrock.git
cd guidance-for-claude-code-with-amazon-bedrock
```
3. upstream リモートを追加します:
```bash
git remote add upstream https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock.git
```

### 開発環境のセットアップ

1. 機能追加または修正用に新しいブランチを作成します:
```bash
git checkout -b feature/your-feature-name
```

2. 以下のガイドラインに従って変更を加えます

3. 変更を十分にテストします

4. 分かりやすいメッセージでコミットします:
```bash
git commit -m "feat: Add new agent for database migrations"
```

## 📝 コントリビューション ガイドライン

### 求めている貢献内容

以下の領域での貢献を歓迎します。

#### 1. 新しいエージェント
- 特定の開発タスクに特化したエージェント
- 既存エージェントの改善
- エージェントのドキュメントおよび例

#### 2. フック設定
- 自動化のための新しいフックパターン
- 品質ゲートの改善
- 新しいツールとの統合

#### 3. ワークフローテンプレート
- 複雑なワークフローのオーケストレーション
- 業界特化ワークフロー
- パフォーマンス最適化

#### 4. コマンドテンプレート
- 新しいスラッシュコマンド
- 引数処理の強化
- コマンドのドキュメント

#### 5. ドキュメント
- 既存ガイドの改善
- 新しいチュートリアルや例
- 翻訳

#### 6. バグ修正
- 不具合解消
- パフォーマンス改善
- セキュリティ強化

### コード標準

#### エージェント（`/agents/` 配下の `.md` ファイル）
```markdown
---
name: agent-name
description: Clear, concise description
model: sonnet|opus  # Choose appropriate model
version: 1.0.0
tools: [List, Of, Tools]
---

# Agent documentation here
```

#### フック（`/hooks/` 配下の `.json` ファイル）
```json
{
  "name": "hook-name",
  "description": "What this hook does",
  "hooks": {
    "EventType": [
      {
        "type": "command|agent",
        "blocking": true|false,
        "description": "What this specific hook does"
      }
    ]
  }
}
```

#### コマンド（`/commands/` 配下の `.md` ファイル）
```markdown
---
name: command-name
description: Brief description
argument-hint: [optional-args] [--flags]
---

# Command implementation
```

### ドキュメント標準

- 明確で簡潔な言葉遣いにする
- 実用的な例を含める
- 既存のフォーマットパターンに従う
- すべてのコード例をテストする
- 変更に伴い関連ドキュメントも更新する

## 🔄 Pull Request（PR）手順

1. **upstream の最新変更を取り込み**、ブランチを更新します:
```bash
git fetch upstream
git rebase upstream/main
```

2. **Fork 側に push** します:
```bash
git push origin feature/your-feature-name
```

3. GitHub で **Pull Request を作成**します:
   - https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/tree/main/advanced-claude-code-patterns に移動
   - 「New Pull Request」をクリック
   - Fork とブランチを選択
   - PR テンプレートに以下を記入：
     - 変更内容の明確な説明
     - Issue 番号（該当する場合）
     - 実施したテスト
     - ドキュメント更新内容

4. **PR 要件**:
   - 明確で説明的なタイトル
   - 変更点の詳細説明
   - 関連 Issue へのリンク
   - （該当する場合）テストが成功していること
   - ドキュメントが更新されていること
   - マージ競合がないこと

### PR タイトル形式
Conventional Commits 形式を使用してください。
- `feat:` 新機能
- `fix:` バグ修正
- `docs:` ドキュメント変更
- `style:` コードスタイル変更
- `refactor:` リファクタリング
- `test:` テスト追加／変更
- `chore:` 保守作業

例:
- `feat: Add PostgreSQL migration agent`
- `fix: Correct model selection in security-reviewer agent`
- `docs: Improve TDD workflow guide examples`

## 🧪 テスト

PR 提出前に、以下を満たしていることを確認してください。

1. **構文検証**:
   - Markdown が適切に整形されている
   - YAML が妥当である
   - JSON が妥当である

2. **機能テスト**:
   - エージェントが期待どおりに動作する
   - フックが正しく発火する
   - ワークフローが正常に完了する
   - コマンドが引数を正しく受け付ける

3. **ドキュメント**:
   - 新機能がすべて文書化されている
   - 例が記載どおりに動作する
   - リンク切れがない

## 🎯 注力領域

### 優先度の高い貢献

1. **エンタープライズパターン**
   - 複数チームのワークフロー
   - コンプライアンス自動化
   - 監査証跡

2. **パフォーマンス最適化**
   - エージェント実行の高速化
   - トークン使用量の削減
   - キャッシュ戦略

3. **セキュリティ強化**
   - セキュリティスキャン用エージェント
   - 脆弱性検出フック
   - セキュアコーディング ワークフロー

4. **統合パターン**
   - 新しい MCP サーバー統合
   - サードパーティツール接続
   - API 統合

### コミュニティからの要望

次のラベルを目印に [GitHub Issues](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/issues) を確認してください。
- `help wanted` の機能要望
- `good first issue` のバグ報告
- `documentation` のドキュメント要望

## 💬 コミュニケーション

### 質問・議論

次の目的で [GitHub Discussion](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/discussions) を立ててください。
- 一般的な質問
- 機能アイデア
- ベストプラクティス
- コミュニティでの成果紹介

### Issue 報告

Issue を報告する際は、次を含めてください。
- 問題の明確な説明
- 再現手順
- 期待される挙動
- 実際の挙動
- Claude Code のバージョン
- OS

## 📜 ライセンス

このリポジトリに貢献することで、あなたの貢献物はプロジェクトと同一のライセンス（MIT License）でライセンスされることに同意したものとみなされます。

## 🙏 クレジット（謝辞）

コントリビューターは以下の形で紹介されます。
- プロジェクトの contributors セクションに掲載
- リリースノートでのクレジット表記
- 適切な場合、ドキュメント内での謝辞

## 📚 リソース

- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
- [Project README](README.md)
- [Quick Start Guide](docs/quick-start.md)
- [Best Practices](docs/best-practices.md)

## ✅ コントリビューター向けチェックリスト

PR を出す前に、以下を確認してください。

- [ ] リポジトリを Fork し、clone した
- [ ] 機能ブランチを作成した
- [ ] 標準に従って変更を行った
- [ ] 変更を十分にテストした
- [ ] 関連ドキュメントを更新した
- [ ] 分かりやすいコミットメッセージでコミットした
- [ ] Fork に push した
- [ ] 詳細説明付きで PR を作成した
- [ ] レビューでのフィードバックに対応した

Claude Code Advanced Patterns への貢献ありがとうございます。皆さまの貢献により、AI 支援開発はより良いものになります。

---

**質問がありますか？** Discussion を立てるか、GitHub Issues を通じてご連絡ください。
