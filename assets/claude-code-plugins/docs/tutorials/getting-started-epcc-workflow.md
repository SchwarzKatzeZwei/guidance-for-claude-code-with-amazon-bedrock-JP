> 📚 [ドキュメントハブに戻る](../README.md)

# Claude Code 入門: EPCC workflow で最初の機能を作る

**学べること**: このチュートリアルを終えるころには、Claude Code Plugins Marketplace をインストールし、EPCC workflow プラグインをセットアップし、探索からコミットまでの開発サイクルを一通り完了できます。体系的な開発プラクティスを自分のプロジェクトに適用できる状態になります。

**所要時間**: 25 分  
**前提条件**:
- Claude Code がインストール済み（未インストールの場合は [https://claude.ai/code](https://claude.ai/code) を参照）
- ターミナル／コマンドラインの基本操作に慣れている
- 作業対象のコードプロジェクトがある（なければ作成を支援します）

## 作るもの

EPCC（Explore-Plan-Code-Commit）ワークフローを使って、プロジェクトに簡単なユーザー向け挨拶（greeting）機能を追加します。これは、次のような現実的な開発サイクルを表しています。

- 既存のパターンを理解するためにコードベースを探索する
- 実装を体系的に計画する
- 専門の AI エージェントに支援してもらいながら実装する
- プロフェッショナルなドキュメント付きでコミットする

### このチュートリアルが重要な理由

EPCC は、よくある開発ミス（文脈理解前にコーディングを始める、エッジケースを見落とす、実装が一貫しない）を防ぐための、手順化されたアプローチです。このワークフローを学ぶことで、「行動する前に考える」習慣が身につきます。これは世界中のプロの開発チームで使われている実践です。

## 開始前に

### セットアップの確認

まず Claude Code が正しく動作していることを確認します。

```bash
# Claude Code がインストールされているか確認
claude --version
```

**期待される出力**: `claude-code v1.x.x` のようなバージョン番号が表示されます。

**チェックポイント**: バージョン番号が表示されれば続行できます。表示されない場合は、先に [https://claude.ai/code](https://claude.ai/code) から Claude Code をインストールしてください。

## 手順 1: プラグインマーケットプレイスを追加

Claude Code をプラグインマーケットプレイスに接続します。開発環境に「アプリストア」を追加するようなものです。

```bash
# AWS Samples のマーケットプレイスを追加
/plugin marketplace add aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock
```

**いま起きたこと**: Claude Code が、本番利用可能な 11 個のプラグインをまとめたキュレーション済みコレクションに接続しました。専門の開発アシスタント一式を解放した、と考えると分かりやすいでしょう。

**期待される結果**: 次のような確認メッセージが表示されます。
```
✓ Marketplace added: aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock
  11 plugins available
```

**チェックポイント**: マーケットプレイスが追加された旨の確認が表示されること。これで利用可能なプラグインへアクセスできる状態になりました。

### マーケットプレイスへのアクセス確認

マーケットプレイスが機能していることを確認します。

```bash
# 利用可能なプラグインを参照
/plugin
```

**期待される結果**: 11 個すべてのプラグインが対話的リストで表示されます。例：
- epcc-workflow（Explore-Plan-Code-Commit）
- documentation（Diataxis フレームワーク）
- security（セキュリティスキャン）
- testing（QA と品質ゲート）
- その他 7 個…

**意味するところ**: マーケットプレイス接続は完了しており、このコレクションから任意のプラグインをインストールできます。

## 手順 2: EPCC workflow プラグインをインストール

最初のプラグインとして、EPCC workflow システムをインストールします。

```bash
# EPCC workflow プラグインをインストール
/plugin install epcc-workflow
```

**いま起きたこと**: 次を含む体系的開発ワークフロー一式をインストールしました。
- 探索／計画／実装／コミットの各フェーズ向けに特化した 12 の AI エージェント
- 4 つのワークフローコマンド（/epcc-explore, /epcc-plan, /epcc-code, /epcc-commit）
- エラーハンドリングのための自動リカバリーフック

**期待される結果**: 次のように表示されます。
```
✓ Plugin installed: epcc-workflow  12 agents added
  4 commands added
  Ready to use!
```

**チェックポイント**: `/epcc` と入力して Tab を押し、コマンド補完が出ることを確認します。4 つの EPCC コマンドが表示されるはずです。

### インストールの確認

すべて準備できていることを確認します。

```bash
# スラッシュコマンド一覧（/epcc-* コマンドが見えるはず）
/

# タブ補完で表示される想定:
# /epcc-explore
# /epcc-plan
# /epcc-code
# /epcc-commit
```

**いま見えているもの**: これら 4 コマンドが EPCC の開発サイクル全体です。プロフェッショナルなワークフロー一式が使える状態になりました。

## 手順 3: はじめての EPCC ワークフロー

いよいよ EPCC を使って実際に何かを作ります。ワークフロー全体を体験できるよう、簡単なユーザー挨拶機能を追加します。

### フェーズ 1: Explore（まず理解する）

コードを書く前に、プロジェクトを理解する必要があります。家を建てる前に土地を測るのと同じです。

```bash
# 探索フェーズを開始
/epcc-explore "user interface and existing greeting patterns"
```

**いま起きたこと**: Claude Code が複数の AI エージェントを並列に起動しました。
- @code-archaeologist がコード構造を分析
- @system-designer がアーキテクチャパターンを特定
- @business-analyst がプロセスフローを整理
- @test-generator がテストカバレッジを評価
- @documentation-agent が既存ドキュメントを確認

**いま試す**: 上記コマンドをプロジェクトディレクトリで実行してください。

**期待される結果**: 30～60 秒程度の分析後、プロジェクトルートに `EPCC_EXPLORE.md` が作成されます。

**チェックポイント**: `EPCC_EXPLORE.md` を開き、次のようなセクションがあることを確認します。
- Executive Summary
- Project Structure
- Key Components
- Patterns & Conventions
- Dependencies
- Constraints & Limitations

**意味するところ**: コードベースの「地図」が手に入りました。これにより、既存のパターンと衝突する変更や、隠れた依存関係を壊す変更を避けられます。

### フェーズ 2: Plan（戦略的に設計する）

プロジェクト理解ができたので、詳細な実装計画を作ります。

```bash
# 計画フェーズを開始
/epcc-plan "Add a simple user greeting feature that displays personalized welcome message"
```

**いま起きたこと**: Claude Code は次を行います。
- `EPCC_EXPLORE.md` の探索結果を読み取る
- 詳細な実装計画を作成する
- 作業を具体的タスクへ分解する
- リスクとエッジケースを評価する
- 成功基準を定義する

**期待される結果**: プロジェクトルートに `EPCC_PLAN.md` が作成されます。

**チェックポイント**: `EPCC_PLAN.md` を開き、次が含まれていることを確認します。
- 機能目的の明確化
- 技術方針の定義
- 所要時間見積もり付きのタスク分解
- リスク評価マトリクス
- テスト戦略
- 成功指標

**いま見えているもの**: これはロードマップです。プロのチームは開発時間の 20～30% を計画に使います。後からの手戻りや高コストなミスを防ぐためです。

### フェーズ 3: Code（自信を持って実装する）

さあ実装です。ただし、やみくもに書き始めません。探索結果と計画に従って進めます。

```bash
# 実装フェーズを開始
/epcc-code "Implement user greeting feature from plan"
```

**いま起きたこと**: Claude Code は次を行います。
- `EPCC_EXPLORE.md` を見て、従うべきパターンを確認
- `EPCC_PLAN.md` を参照して、実装戦略を適用
- 専門の実装エージェントを起動：
  - @test-generator がテストを先に作成（TDD アプローチ）
  - @security-reviewer がセキュリティ実践を検証
  - @documentation-agent がインラインドキュメントを生成
  - @optimization-engineer が性能面を考慮
- 動作し、テスト済みのコードを作成

**期待される結果**:
1. 計画に沿った新規／変更コードが作成される
2. テストファイルが作成され、テストが通る
3. 作った内容を記録する `EPCC_CODE.md` が作成される

**チェックポイント**: 次を確認してください。
- [ ] 挨拶機能のコードが存在し、期待どおり動く
- [ ] テストがあり、成功している
- [ ] `EPCC_CODE.md` に実装詳細が記録されている
- [ ] 探索フェーズで特定されたパターンに沿っている

**試す**: 新しい挨拶機能をテストします。
```bash
# テストを実行
npm test
# または
pytest
```

**いま見えているもの**: テストはグリーン（成功）になるはずです。Claude が探索フェーズで見つけたテスト規約に従って実装したためです。

### フェーズ 4: Commit（プロとして仕上げる）

最後は、完全なドキュメントを備えたプロフェッショナルなコミットを作ります。

```bash
# コミットフェーズを開始
/epcc-commit "Add personalized user greeting feature"
```

**いま起きたこと**: Claude Code は次を行います。
- 最終品質チェック（テスト、lint、セキュリティスキャン）を実行
- プロフェッショナルなコミットメッセージを生成
- そのまま使える PR ドキュメントを作成
- 変更全体を `EPCC_COMMIT.md` に記録
- コードレビューに向けた準備を整える

**期待される結果**:
1. Conventional Commits 形式に沿ったコミットメッセージ案
2. コピーして使える PR 説明文
3. 完全な記録が入った `EPCC_COMMIT.md`
4. 品質チェックがすべて成功

**チェックポイント**: `EPCC_COMMIT.md` を開き、次があることを確認します。
- 変更概要（what/why/how）
- 変更ファイル一覧
- カバレッジを含むテスト概要
- セキュリティ観点
- 性能影響
- PR 説明テンプレート

**意味するところ**: 変更がプロフェッショナルに文書化され、チームレビューに出せる状態になりました。判断と実装の根拠が残ります。

### 実際にコミットする

作業をコミットします。

```bash
# 変更内容を確認
git status
git diff

# ステージング
git add .

# EPCC_COMMIT.md のメッセージを使ってコミット
git commit -m "feat: Add personalized user greeting feature

- Implement greeting display component
- Add user name personalization
- Include comprehensive test coverage
- Follow existing UI patterns

Based on:
- Exploration: EPCC_EXPLORE.md
- Plan: EPCC_PLAN.md
- Implementation: EPCC_CODE.md
- Finalization: EPCC_COMMIT.md"
```

**期待される結果**: Git がコミット作成を確認します。

**やったこと**: 変更の「全ストーリー」が分かる、プロフェッショナルなコミットを作成しました。将来の自分を含む誰が見ても、何をなぜどう行ったかが追えます。

## 達成したこと

おめでとうございます。EPCC ワークフローを 1 周完走しました。達成したことは次のとおりです。

✓ Claude Code Plugins Marketplace をインストールした  
✓ EPCC workflow プラグインをセットアップした  
✓ AI エージェントを用いてコードベースを体系的に探索した  
✓ 詳細な実装計画を作成した  
✓ 自動テスト／ドキュメント化を伴って機能を実装した  
✓ 完全なドキュメント付きでプロとしてコミットした  
✓ プロの開発チームが使うワークフローを学んだ  

**さらに重要なこと**: 各フェーズがなぜ必要かを理解しました。
- **Explore**: 破壊的変更や不整合な実装を防ぐ
- **Plan**: コーディング前に考え、手戻りを減らす
- **Code**: 体系的実装で品質を担保する
- **Commit**: チームが理解できる保守可能な履歴を作る

## 次のステップ

EPCC の基本が分かったら、次に進みましょう。

### 自分の作業に適用する
プロジェクトの実タスクで EPCC を試してください。
```bash
# まずは探索から
/epcc-explore "the authentication system"

# あるいは追加したい機能を探索
/epcc-explore "API endpoints for user management"
```

### 他のプラグインを試す
マーケットプレイスには、まだ 10 個のプラグインがあります。
```bash
# プラグイン一覧
/plugin

# よく使われる組み合わせ:
/plugin install documentation@aws-claude-code-plugins  # ドキュメント強化
/plugin install security@aws-claude-code-plugins       # セキュリティチェック
/plugin install testing@aws-claude-code-plugins        # QA 自動化
```

### チーム向けに設定する
チーム全体で必須プラグインを設定します。
- **[チーム設定ガイド](../how-to/configure-plugins.md#step-4-install-plugin-bundles)** - `.claude/settings.json` でチーム全体に強制
- **[バンドル例](../how-to/configure-plugins.md#starter-bundle-recommended-for-teams-getting-started)** - 規模に応じた事前構成
- **[ベストプラクティス](../how-to/configure-plugins.md#team-configuration)** - チームのプラグイン管理の DO / DON'T

**重要性**: チームレベル設定により全員のツールが揃い、コラボレーションが滑らかになり、オンボーディングも即時化します。

### EPCC 応用テクニック
- **深掘り探索**: `/epcc-explore --deep "complex legacy code"`
- **高速イテレーション**: `/epcc-explore --quick "small bug fix"`
- **TDD アプローチ**: `/epcc-code --tdd "feature with tests first"`

### さらに学ぶ
- **設定ガイド**: チーム設定を含む高度な設定は [Plugin Configuration](../how-to/configure-plugins.md) を参照
- **プラグインカタログ**: 全プラグイン詳細は [Main README](../../README.md#available-plugins) を参照
- **ドキュメントハブ**: リソース一覧は [Documentation Home](../README.md) を参照

## トラブルシューティング

### 問題: マーケットプレイスを追加できない
```
Error: Cannot connect to marketplace
```

**対処**: インターネット接続を確認し、再試行します。
```bash
# Claude Code が最新か確認
claude --version

# マーケットプレイス追加を再試行
/plugin marketplace add aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock
```

### 問題: プラグインのインストールに失敗する
```
Error: Plugin not found
```

**対処**: 先にマーケットプレイスが追加されていることを確認します。
```bash
# マーケットプレイス一覧
/plugin marketplace list

# 表示されるべきもの:
# aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock
# なければ再追加
/plugin marketplace add aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock
```

### 問題: EPCC コマンドが見つからない
```
Command not recognized: /epcc-explore
```

**対処**: プラグインのインストールを確認します。
```bash
# インストール済みプラグイン確認
/plugin list

# 表示されるべきもの: epcc-workflow
# なければ再インストール
/plugin install epcc-workflow
```

### 問題: 探索フェーズに時間がかかりすぎる

**対処**: 小さい探索では quick モードを使います。
```bash
# 小範囲の探索向け
/epcc-explore --quick "specific component"
```

### 問題: EPCC_*.md ファイルが増えすぎる

**対処**: 完了したワークフローをアーカイブします。
```bash
# アーカイブディレクトリ作成
mkdir -p .epcc-archive/feature-name

# 完了済み EPCC ファイルを移動
mv EPCC_*.md .epcc-archive/feature-name/

# あるいは機能と一緒にコミット
git add EPCC_*.md
git commit -m "docs: Add EPCC workflow documentation"
```

### 問題: 生成されたコードがプロジェクトのスタイルに合わない

**対処**: プロジェクトルートに、規約を記した CLAUDE.md を作成します。
```markdown
# CLAUDE.md

## Code Style
- Use spaces, not tabs
- Functions should be under 50 lines
- Always use TypeScript strict mode

## Testing
- Write tests first (TDD)
- Use Jest for testing
- Minimum 80% coverage
```

EPCC は探索中にこのファイルを自動的に読み取り、規約に従います。

## 成功のためのヒント

1. **必ず探索から始める** — 分かっているつもりでも、忘れていた制約やパターンが見つかります。

2. **計画を省略しない** — 15 分の計画が、後のリファクタリング数時間を節約します。

3. **EPCC ファイルを確認する** — コーディング前に `EPCC_EXPLORE.md` と `EPCC_PLAN.md` を開いてください。

4. **EPCC ファイルを残す** — コードレビューや将来の保守で強力なドキュメントになります。

5. **状況に応じてフラグを使い分ける**:
   - 迅速な修正: `/epcc-explore --quick`
   - 複雑な作業: `/epcc-explore --deep`
   - テスト駆動: `/epcc-code --tdd`

6. **他プラグインと組み合わせる** — EPCC は security/testing/documentation と相性が良いです。

## EPCC の旅はここから

AI 支援による体系的開発の第一歩を踏み出しました。練習すれば EPCC は自然に身につきます。

**1 週目**: 小さな機能で EPCC を使い、習慣化する  
**2 週目**: バグ修正やリファクタリングで試す  
**3 週目**: 依存関係の多い複雑機能に適用する  
**4 週目**: 作業開始前に自然と「探索→計画→実装→コミット」と考えるようになる  

**体系的に考え、自信を持って実装し、プロとしてコミットする。**

EPCC コミュニティへようこそ。

---

**困ったときは**
- [Issue を報告する](https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock/issues)
- [全ドキュメントを読む](../../README.md)
- [ドキュメントハブに戻る](../README.md)
