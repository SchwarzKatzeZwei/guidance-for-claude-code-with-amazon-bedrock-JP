# ドキュメント品質保証（QA）チェックリスト

**目的**: Claude Code Plugins Marketplace のドキュメント全体について、品質・一貫性・適切なナビゲーション構造を担保する。

## 1. 用語の一貫性

### 公式名称（表記を厳密に統一）
- ✅ **Claude Code Plugins Marketplace**（プロジェクト名）
- ✅ **Claude Code**（ツール名）
- ✅ **EPCC workflow**（プラグイン名。「workflow」は小文字）
- ✅ **Diataxis**（フレームワーク名。D は大文字）

### プラグイン名（完全一致必須）
すべてのプラグイン名は、以下と完全に一致する必要があります。

| プラグイン名 | インストールコマンド |
|-------------|------------------------|
| `epcc-workflow` | `/plugin install epcc-workflow@aws-claude-code-plugins` |
| `documentation` | `/plugin install documentation@aws-claude-code-plugins` |
| `architecture` | `/plugin install architecture@aws-claude-code-plugins` |
| `security` | `/plugin install security@aws-claude-code-plugins` |
| `testing` | `/plugin install testing@aws-claude-code-plugins` |
| `performance` | `/plugin install performance@aws-claude-code-plugins` |
| `tdd-workflow` | `/plugin install tdd-workflow@aws-claude-code-plugins` |
| `agile-tools` | `/plugin install agile-tools@aws-claude-code-plugins` |
| `ux-design` | `/plugin install ux-design@aws-claude-code-plugins` |
| `deployment` | `/plugin install deployment@aws-claude-code-plugins` |
| `code-analysis` | `/plugin install code-analysis@aws-claude-code-plugins` |

### コマンド構文の標準
- ✅ コマンドは必ず `/` から始める（例: `/plugin`、`/epcc-explore`）
- ✅ マーケットプレイス参照: `@aws-claude-code-plugins`
- ✅ 完全なインストール構文: `/plugin install <name>@aws-claude-code-plugins`
- ✅ スラッシュコマンド: `/epcc-explore`、`/epcc-plan`、`/epcc-code`、`/epcc-commit`

### よく使う用語（表記の統一）
| こちらを使う | こちらは使わない |
|----------|----------|
| plugin | plug-in, Plugin |
| agent | Agent（文頭を除く） |
| marketplace | Marketplace（文頭を除く） |
| workflow | Workflow（文頭を除く） |
| command | Command（文頭を除く） |

## 2. 相互参照（クロスリファレンス）の検証

### ドキュメントハブ（docs/README.md）
- [ ] チュートリアルへのリンク: `[Getting Started Tutorial](tutorials/getting-started-epcc-workflow.md)`
- [ ] How-To へのリンク: `[Configuration How-To](how-to/configure-plugins.md)`
- [ ] メイン README へのリンク: `[Main Repository README](../README.md)`
- [ ] CONTRIBUTING へのリンク: `[Contributing Guide](../CONTRIBUTING.md)`
- [ ] SECURITY へのリンク: `[Security Policy](../SECURITY.md)`
- [ ] すべてのプラグインリンクが、メイン README の該当セクションを参照している

### チュートリアル（docs/tutorials/getting-started-epcc-workflow.md）
- [ ] ドキュメントハブへのリンク: `[Documentation Hub](../README.md)`
- [ ] 高度なトピック用 How-To へのリンク: `[Configuration Guide](../how-to/configure-plugins.md)`
- [ ] アンカー付きで How-To の特定セクションへリンク（例: `#team-configuration`）
- [ ] プラグイン詳細はメイン README にリンク: `[Main README](../../README.md)`

### How-To（docs/how-to/configure-plugins.md）
- [ ] ドキュメントハブへのリンク: `[Documentation Hub](../README.md)`
- [ ] 初心者向けチュートリアルへのリンク: `[Getting Started](../tutorials/getting-started-epcc-workflow.md)`
- [ ] プラグインカタログ（メイン README）へのリンク: `[Plugin Catalog](../../README.md#available-plugins)`
- [ ] 適切なセクションアンカー（例: `#team-configuration`、`#troubleshooting`）

### メイン README（README.md）
- [ ] ドキュメントハブへのリンク: `[Documentation Hub](docs/README.md)`
- [ ] チュートリアルへのリンク: `[Getting Started Tutorial](docs/tutorials/getting-started-epcc-workflow.md)`
- [ ] How-To へのリンク: `[Configuration How-To](docs/how-to/configure-plugins.md)`
- [ ] リポジトリ構成で docs ディレクトリが正しく示されている
- [ ] すべてのプラグイン節に適切なアンカーがある

## 3. 内容の一貫性

### インストール例
全ドキュメントで、インストールコマンドが同一であることを確認します。

```bash
# マーケットプレイスを追加
/plugin marketplace add aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock

# プラグインをインストール
/plugin install epcc-workflow
# プラグインを参照
/plugin
```

### ディレクトリ構成例
すべてのドキュメントで同じ構成を示していること。

```
claude-code-plugins/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   ├── epcc-workflow/
│   ├── documentation/
│   ├── architecture/
│   └── ...
├── docs/
│   ├── README.md
│   ├── tutorials/
│   └── how-to/
└── README.md
```

### プラグイン説明
各プラグインの説明は、メイン README と完全に一致している必要があります。

#### EPCC Workflow
- "EPCC (Explore-Plan-Code-Commit) systematic development workflow"
- "Systematic, methodical development approach"

#### Documentation
- "Complete Diataxis documentation framework"
- "Comprehensive, user-focused documentation"

#### Architecture
- "Architecture design, review, and documentation"
- "System design and architecture reviews"

## 4. 例の一貫性

### 動作するコード例
すべてのコード例は次を満たす必要があります。
- [ ] 実在して動作するコマンドを使用している
- [ ] 期待される出力を得られる
- [ ] 公開前にテストされている
- [ ] 期待結果または説明が含まれている
- [ ] 複数ドキュメントで同じ例を使う場合、コードが完全に同一である（同じ例＝同じコード）

### 検証すべき代表例

**例 1: 基本的なプラグインインストール**
```bash
/plugin install epcc-workflow
```

**例 2: チーム設定**
```json
{
  "requiredMarketplaces": ["aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"],
  "requiredPlugins": [
    "epcc-workflow@aws-claude-code-plugins",
    "security@aws-claude-code-plugins"
  ]
}
```

**例 3: EPCC workflow コマンド**
```bash
/epcc-explore "authentication system"
/epcc-plan
/epcc-code
/epcc-commit
```

## 5. 矛盾がないこと

### 競合のチェック

- [ ] インストール手順が全ドキュメントで同一
- [ ] コマンド構文が全箇所で一貫
- [ ] プラグインの機能説明が参照先間で一致
- [ ] 前提条件が一貫
- [ ] （存在する場合）バージョン番号が一致
- [ ] ファイルパスが一貫
- [ ] ディレクトリ構成が一致

### 矛盾が起きやすいポイント
1. **インストール手順**: チュートリアルと How-To が一致している必要がある
2. **プラグイン名**: すべての箇所で完全一致が必要
3. **コマンド構文**: 例を含めて完全一致が必要
4. **ディレクトリパス**: 同じ構造を使用する
5. **前提条件**: 同一の要件を列挙する

## 6. リンク検証

### 内部リンク（相対パス）

`docs/README.md` から:
- [ ] `tutorials/getting-started-epcc-workflow.md` ✓
- [ ] `how-to/configure-plugins.md` ✓
- [ ] `../README.md` ✓
- [ ] `../CONTRIBUTING.md` ✓
- [ ] `../SECURITY.md` ✓

`docs/tutorials/getting-started-epcc-workflow.md` から:
- [ ] `../README.md` ✓
- [ ] `../how-to/configure-plugins.md` ✓
- [ ] `../../README.md` ✓

`docs/how-to/configure-plugins.md` から:
- [ ] `../README.md` ✓
- [ ] `../tutorials/getting-started-epcc-workflow.md` ✓
- [ ] `../../README.md` ✓

`README.md` から:
- [ ] `docs/README.md` ✓
- [ ] `docs/tutorials/getting-started-epcc-workflow.md` ✓
- [ ] `docs/how-to/configure-plugins.md` ✓
- [ ] `CONTRIBUTING.md` ✓
- [ ] `SECURITY.md` ✓

### 外部リンク

- [ ] `https://docs.claude.com/claude-code` ✓
- [ ] `https://docs.claude.com/claude-code/plugins-reference` ✓
- [ ] `https://docs.claude.com/claude-code/plugin-marketplaces` ✓
- [ ] `https://diataxis.fr/` ✓
- [ ] （該当する場合）GitHub リポジトリリンク ✓

### アンカーリンク

- [ ] How-To ガイドに `#team-configuration` が存在する
- [ ] How-To ガイドに `#troubleshooting` が存在する
- [ ] How-To ガイドに `#installation` が存在する
- [ ] メイン README に `#available-plugins` が存在する
- [ ] 参照しているアンカーがすべて有効

## 7. Diataxis フレームワーク準拠

### チュートリアル文書
- [ ] 学習指向（学習成果に焦点）
- [ ] ハンズオンで、手順が段階的
- [ ] 事前知識がない前提
- [ ] 試行錯誤を促す
- [ ] 動作する例がある
- [ ] 明確な完了基準がある
- [ ] 所要時間の目安がある（25 分）

### How-To 文書
- [ ] タスク指向（問題解決に焦点）
- [ ] 目的に直結した手順
- [ ] 基礎知識がある前提
- [ ] 実用的な解決策を提示
- [ ] 複数のユースケースを扱う
- [ ] トラブルシューティング節がある
- [ ] タスク説明が明確

### リファレンス（メイン README）
- [ ] 情報指向
- [ ] 網羅的
- [ ] 機能（プラグイン）別に整理
- [ ] 技術仕様がある
- [ ] すばやく参照できる構造

## 8. プロフェッショナル品質基準

### 体裁（フォーマット）
- [ ] 見出しレベルが一貫している
- [ ] 言語タグ付きのコードブロックが適切
- [ ] 表が整形され、揃っている
- [ ] リストの箇条書きスタイルが一貫
- [ ] リンク形式が正しい

### 文法とスタイル
- [ ] 全体を通してプロフェッショナルなトーン
- [ ] 可能な限り能動態
- [ ] 手順は命令形を優先
- [ ] 時制が一貫
- [ ] スペルミスがない

### 構成
- [ ] 情報の流れが論理的
- [ ] 段階的開示（簡単 → 複雑）
- [ ] セクションの境界が明確
- [ ] 必要に応じて目次がある
- [ ] まとめ／結論がある（必要に応じて）

### アクセシビリティ
- [ ] リンクテキストが説明的（"click here" を避ける）
- [ ] 画像（ある場合）に代替テキストがある
- [ ] 見出し階層が明確
- [ ] コード例が読みやすい
- [ ] 色だけに情報を依存していない

## 9. ユーザーナビゲーション

### 「ここから辿れるか？」テスト

メイン README から開始:
- [ ] 1 クリックでドキュメントハブに到達できる
- [ ] 2 クリックでチュートリアルに到達できる
- [ ] 2 クリックで How-To に到達できる
- [ ] 1 クリックで Contributing ガイドに到達できる

ドキュメントハブから開始:
- [ ] 1 クリックでチュートリアルに到達できる
- [ ] 1 クリックで How-To に到達できる
- [ ] 1 クリックでメイン README に戻れる
- [ ] 1 クリックで Contributing ガイドに到達できる

チュートリアルから開始:
- [ ] 1 クリックでドキュメントハブに到達できる
- [ ] 1 クリックで How-To に到達できる
- [ ] 1 クリックでメイン README に到達できる

How-To から開始:
- [ ] 1 クリックでドキュメントハブに到達できる
- [ ] 1 クリックでチュートリアルに到達できる
- [ ] 1 クリックでメイン README に到達できる

### ユーザージャーニーの完結性

**初心者ジャーニー:**
1. [ ] メイン README に到達する
2. [ ] ドキュメントハブへのリンクを見つける
3. [ ] 自分が初心者であると判断できる
4. [ ] 2 クリックでチュートリアルへ到達できる
5. [ ] チュートリアルを完了できる
6. [ ] 次のステップとして How-To へのリンクを見つけられる

**実務者ジャーニー:**
1. [ ] メイン README に到達する
2. [ ] ドキュメントハブへのリンクを見つける
3. [ ] 自分が実務者であると判断できる
4. [ ] 2 クリックで How-To へ到達できる
5. [ ] 特定の問題を解決できる
6. [ ] プラグイン詳細のため、メイン README へのリンクを見つけられる

**チームリード ジャーニー:**
1. [ ] メイン README に到達する
2. [ ] ドキュメントハブへのリンクを見つける
3. [ ] 自分がチームリードであると判断できる
4. [ ] 3 クリックでチーム設定に到達できる
5. [ ] チーム向けにプラグインを設定できる
6. [ ] チーム教育のためのチュートリアルリンクを見つけられる

## 10. 最終チェックリスト

### 公開前
- [ ] すべての agent が担当ドキュメントを完了している
- [ ] ドキュメントハブが完成している
- [ ] メイン README がリンク付きで更新されている
- [ ] 内部リンクをすべてテストした
- [ ] 外部リンクをすべてテストした
- [ ] 用語が一貫している
- [ ] 例が動作確認済み
- [ ] 矛盾がない
- [ ] 相互参照が完備されている

### 品質ゲート
- [ ] スペルと文法をチェックした
- [ ] コード例をテストした
- [ ] リンクの妥当性を確認した
- [ ] ユーザージャーニーを検証した
- [ ] Diataxis 原則に従っている
- [ ] プロフェッショナルなトーンを維持している
- [ ] アクセシビリティ基準を満たしている
- [ ] ナビゲーション構造を検証した

### サインオフ
- [ ] ドキュメント統括がレビューした
- [ ] Tutorial Agent が完了を確認した
- [ ] How-To Agent が完了を確認した
- [ ] すべてのリンクを手動でテストした
- [ ] ユーザーテストの準備ができている

---

**テストメモ**: チェックリスト完了後、次の対象者でユーザーテストを実施してください。
1. 完全な初心者（Claude Code 未使用）
2. 経験豊富な開発者（CLI ツールに慣れている）
3. チームリード（チーム設定の責任者）

ナビゲーション上の問題、不明瞭な手順、リンク切れなどがあれば記録し、速やかに修正してください。
