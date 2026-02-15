> 📚 [ドキュメントハブに戻る](../README.md)

# Claude Code プラグインの設定と利用方法

> **目的**: Claude Code マーケットプレイスのプラグインを、正しくインストール／設定し、利用できる状態にする  
> **想定ユースケース**: 特化ツールで Claude Code を拡張したいチームおよび個人  
> **所要時間**: 基本セットアップ 15～30 分、エンタープライズ向け設定 1～2 時間

## 前提条件
開始前に、以下を満たしていることを確認してください。
- Claude Code がインストール済みで、認証が完了している
- Claude Code の基本コマンドに慣れている
- プロジェクトの開発ワークフロー上の要件を理解している
- （チーム設定のため）プロジェクトのリポジトリにアクセスできる
- 解決したい課題（ドキュメント、セキュリティ、テストなど）を把握している

## 課題の背景
Claude Code は強力な基本機能を提供しますが、専門的な開発タスクには追加ツールが必要です。Claude Code Plugins Marketplace（`aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock`）には、体系的な開発、ドキュメント、セキュリティ、テストなどに対応する **本番利用可能（production-ready）な 11 個のプラグイン**が用意されています。本ガイドでは、これらのプラグインを効果的にインストールし、設定し、利用する方法を説明します。

## 解決策の概要
以下の手順で解決します。
1. Claude Code にマーケットプレイスを追加する
2. 要件に応じて個別プラグインまたはバンドルをインストールする
3. チーム全体に適用するプラグイン要件を設定する
4. プラグインの構成要素（エージェント、コマンド、フック）を利用する
5. よくある設定問題をトラブルシューティングする

**この方法を選ぶ理由**: マーケットプレイスは、モジュール化され、実運用で鍛えられたプラグインを提供し、Claude Code とシームレスに統合できます。これにより、ゼロからカスタムツールを作る必要がなくなります。

## 手順 1: マーケットプレイスを追加

Claude Code をプラグインマーケットプレイスに接続します。

```bash
# マーケットプレイスを追加（初回のみ）
/plugin marketplace add aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock

# 追加されたことを確認
/plugin marketplace list
```

**期待される結果**: マーケットプレイス一覧に `aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock` が表示されます。

**CLI を使う代替方法**:
```bash
# ターミナルから Claude Code を使っている場合
claude "/plugin marketplace add aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"
```

## 手順 2: 利用可能なプラグインを確認

対話的にプラグインを探索して、必要なものを見つけます。

```bash
# 11 個のプラグインをすべて表示する対話ブラウザ
/plugin

# あるいは特定マーケットプレイスを参照
/plugin browse aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock
```

**表示される内容**:
- プラグイン名と説明
- カテゴリ（workflow、documentation、security、testing など）
- バージョン情報
- インストールコマンド

**成功基準**: 11 個のプラグイン（epcc-workflow、documentation、architecture、security、testing、performance、tdd-workflow、agile-tools、ux-design、deployment、code-analysis）が一覧で確認できること。

## 手順 3: 最初のプラグインをインストール

体系的な開発に推奨の EPCC workflow プラグインから始めます。

```bash
# EPCC workflow プラグインをインストール
/plugin install epcc-workflow
# インストール確認
/plugin list
```

**期待される結果**: インストール済みプラグイン一覧に表示され、新しいコマンドが利用可能になります。

**動作確認**: プラグインコマンドを試します。
```bash
# explore コマンドをテスト
/epcc-explore

# プラグインのエージェントを呼び出してテスト
@code-archaeologist
```

コマンドとエージェントが認識されれば、正しくインストールされています。

## 手順 4: プラグインバンドルをインストール

個別インストールの代わりに、一般的なシナリオ向けの事前構成済みバンドルを使用できます。

### チームレベルのプラグイン強制（必須化）の考え方

Claude Code は `.claude/settings.json` により **チームレベルの必須プラグイン**をサポートします。プロジェクトルートにこのファイルがある場合：

**仕組み:**
1. チームメンバーが Claude Code でプロジェクトを開くと、必須プラグインが提示される
2. 未インストールのプラグインがあれば、Claude Code が自動的にインストールを促す
3. 全員が同じツール群と機能を利用できる
4. 設定はコードと一緒にバージョン管理される

**主なメリット:**
- ✅ **ツールの一貫性** — 同じエージェント／コマンド／フックを利用
- ✅ **ゼロ設定** — 新メンバーも自動で必要プラグインが揃う
- ✅ **チーム標準** — セキュリティ、テスト、品質のプラクティスを徹底
- ✅ **オンボーディングが容易** — git clone だけでセットアップが完了

**強制レベル:**
- `requiredPlugins`: 促し（プロンプト）は表示されますが、利用をブロックはしません  
- コードレビュー要件や CI/CD チェックと組み合わせるのが推奨です

### スターターバンドル（チーム導入に推奨）

プロジェクトルートに `.claude/settings.json` を作成します。

```json
{
  "requiredMarketplaces": [
    "aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"
  ],
  "requiredPlugins": [
    "epcc-workflow@aws-claude-code-plugins",
    "documentation@aws-claude-code-plugins",
    "security@aws-claude-code-plugins"
  ]
}
```

**この設定で行われること**:
- チーム全員に、必須の 3 プラグインを自動インストール
- 体系的な開発ワークフロー（EPCC）を適用
- 包括的なドキュメント化（Diataxis フレームワーク）を有効化
- セキュリティスキャンとコンプライアンスを提供

**利用場面**: AI 支援開発を導入し始めた小～中規模チーム。

### フルスタック バンドル（包括的な開発）

```json
{
  "requiredMarketplaces": [
    "aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"
  ],
  "requiredPlugins": [
    "epcc-workflow@aws-claude-code-plugins",
    "documentation@aws-claude-code-plugins",
    "architecture@aws-claude-code-plugins",
    "testing@aws-claude-code-plugins",
    "ux-design@aws-claude-code-plugins"
  ]
}
```

**利用場面**: フロントエンド／バックエンドを含む Web アプリを開発するフルスタックチーム。

### エンタープライズ バンドル（企業向けフルセット）

```json
{
  "requiredMarketplaces": [
    "aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"
  ],
  "requiredPlugins": [
    "epcc-workflow@aws-claude-code-plugins",
    "security@aws-claude-code-plugins",
    "testing@aws-claude-code-plugins",
    "performance@aws-claude-code-plugins",
    "architecture@aws-claude-code-plugins",
    "deployment@aws-claude-code-plugins",
    "agile-tools@aws-claude-code-plugins"
  ]
}
```

**利用場面**: セキュリティ、コンプライアンス、性能監視、デプロイ自動化が必要なエンタープライズチーム。

### TDD バンドル（テスト駆動開発）

```json
{
  "requiredMarketplaces": [
    "aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"
  ],
  "requiredPlugins": [
    "tdd-workflow@aws-claude-code-plugins",
    "testing@aws-claude-code-plugins",
    "epcc-workflow@aws-claude-code-plugins"
  ]
}
```

**利用場面**: red-green-refactor サイクルでテスト駆動開発を行うチーム。

**成功基準**: `.claude/settings.json` を作成後、`/plugin list` を実行し、必須プラグインが自動的にインストールされていることを確認できること。

## 手順 5: プラグインのエージェントを使う

プラグインは、特定タスク向けの専用エージェントを提供します。エージェントは `@` 接頭辞で呼び出します。

```bash
# 単一エージェントを呼び出す
@security-reviewer

# 複数エージェントを並列に呼び出す（重要パターン）
@docs-tutorial-agent @docs-howto-agent @docs-reference-agent @docs-explanation-agent

# 横断チームでのデプロイ
@architect @security-reviewer @qa-engineer @deployment-agent
```

**動作例** — セキュリティレビュー:
```bash
# セキュリティプラグインのエージェントにレビューを依頼
claude "@security-reviewer scan this codebase for vulnerabilities and generate a report"
```

**期待される出力**: 次を含むセキュリティ分析レポート
- 潜在的な脆弱性
- コンプライアンス上の問題
- セキュリティ改善提案
- リスク評価

**エージェント編成（オーケストレーション）パターン** — ドキュメント一式:
```bash
# 並列エージェントで包括的ドキュメントを生成
claude "@docs-tutorial-agent @docs-howto-agent @docs-reference-agent @docs-explanation-agent create comprehensive documentation for the authentication system"
```

**並列が良い理由**: 逐次実行より効率的で、Claude Code の同時処理能力を活かせます。

## 手順 6: プラグインコマンドを使う

プラグインは、引数を取れるスラッシュコマンドを提供します。

```bash
# EPCC ワークフロー コマンド
/epcc-explore "authentication module"
/epcc-plan
/epcc-code
/epcc-commit

# ドキュメントコマンド（スマートルーティング）
/docs-create "API endpoints" --complete
/docs-create "user guide" --learning
/docs-howto "configure SSL"

# TDD ワークフロー コマンド
/tdd-feature "user login"
/tdd-bugfix "authentication timeout"

# セキュリティコマンド
/security-scan --strict
/permission-audit

# アーキテクチャ コマンド
/design-architecture "microservices system"
/code-review --comprehensive
```

**動作例** — EPCC の探索（深さ制御）:
```bash
# 簡易探索（デフォルトの深さ）
/epcc-explore "database layer"

# 深掘り探索（より徹底した分析）
/epcc-explore "payment processing" --deep
```

**期待される結果**: 指定領域の包括的分析を含む `EPCC_EXPLORE.md` が作成されます。

## 手順 7: セキュリティフックを設定

security プラグインは、危険な操作をブロックする pre-commit フックを提供します。

プロジェクトに `hooks/security_check.py` を作成します。

```python
#!/usr/bin/env python3
"""Claude Code 用セキュリティ検証フック。"""

import sys
import re

def check_secrets(file_path, content):
    """コード内の潜在的なシークレットを検出する。"""
    secret_patterns = [
        r'api[_-]?key\s*=\s*["\'][\w\-]+["\']',
        r'secret[_-]?key\s*=\s*["\'][\w\-]+["\']',
        r'password\s*=\s*["\'][\w\-]+["\']',
        r'token\s*=\s*["\'][\w\-]+["\']',
    ]

    for pattern in secret_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            print(f"ERROR: Potential secret detected in {file_path}")
            return False

    return True

def main():
    file_path = sys.argv[1] if len(sys.argv) > 1 else None
    content = sys.stdin.read()

    if not check_secrets(file_path, content):
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
```

`.claude/settings.json` にフック設定を追加します。

```json
{
  "requiredPlugins": [
    "security@aws-claude-code-plugins"
  ],
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python hooks/security_check.py",
            "blocking": true,
            "description": "Check for secrets before writing files"
          }
        ]
      }
    ]
  }
}
```

**スクリプトに実行権限を付与**:
```bash
chmod +x hooks/security_check.py
```

**セキュリティフックをテスト**:
```bash
# この操作はフックによりブロックされる想定
echo 'API_KEY="sk-1234567890"' > test.py
claude "edit test.py to add a function"
```

**期待される結果**: フックが操作をブロックし、潜在的なシークレットに関するエラーが表示されます。

**確認方法**: 書き込みが防止され、セキュリティ警告が表示されること。

## 手順 8: 品質ゲートを設定

testing プラグインは、コミット前に自動品質チェックを実行できます。

`.claude/settings.json` に追加します。

```json
{
  "requiredPlugins": [
    "testing@aws-claude-code-plugins"
  ],
  "hooks": {
    "PreCommit": [
      {
        "type": "command",
        "command": "black --check .",
        "blocking": true,
        "description": "Check Python code formatting"
      },
      {
        "type": "command",
        "command": "ruff check .",
        "blocking": true,
        "description": "Run linting checks"
      },
      {
        "type": "command",
        "command": "mypy . --ignore-missing-imports",
        "blocking": false,
        "description": "Type checking (warning only)"
      },
      {
        "type": "command",
        "command": "pytest tests/ --quiet",
        "blocking": true,
        "description": "Run test suite"
      }
    ]
  }
}
```

**各ゲートの内容**:
- **black**: コードフォーマットの一貫性を保証（ブロッキング）
- **ruff**: コード品質の問題を検出（ブロッキング）
- **mypy**: 型ヒントを検証（非ブロッキングの警告）
- **pytest**: テストスイートを実行（ブロッキング）

**必要ツールのインストール**:
```bash
# uv を使う場合（推奨）
uvx black --version
uvx ruff --version
uvx mypy --version
uvx pytest --version

# 従来どおりインストールする場合
pip install black ruff mypy pytest
```

**品質ゲートをテスト**:
```bash
# コミットを発行してゲートを実行
git add .
git commit -m "test quality gates"
```

**期待される結果**: 品質チェックが自動で実行され、ブロッキングチェックがすべて成功した場合のみコミットが進行します。

## 手順 9: プラグインの有効化／無効化

アンインストールせずにプラグインを管理できます。

```bash
# 一時的に無効化
/plugin disable security
# 再度有効化
/plugin enable security
# 有効／無効の状態も含めて一覧表示
/plugin list
```

**無効化する場面**:
- 一時的に制約を外してテストしたい
- パフォーマンス最適化
- プラグイン競合の切り分け

**注**: 無効化してもプラグインはインストールされたままですが、エージェント／コマンド／フックは無効になります。

## 手順 10: プラグインの更新とアンインストール

プラグインを最新化する、または不要なものを削除します。

```bash
# 更新の有無を確認
/plugin update --check

# 特定プラグインを更新
/plugin update epcc-workflow
# すべて更新
/plugin update --all

# アンインストール
/plugin uninstall performance
# 確認なしでアンインストール
/plugin uninstall --force performance
```

**ベストプラクティス**: バグ修正や新機能を取り込むため、定期的に更新してください。

**更新確認**:
```bash
# バージョン番号を確認
/plugin list --verbose
```

## 検証

プラグイン設定が正しく動作していることを確認します。

```bash
# マーケットプレイスへのアクセスを確認
/plugin marketplace list
# 期待: aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock が表示される

# プラグインのインストール確認
/plugin list
# 期待: インストール済みプラグインがバージョン番号付きで表示される

# エージェントの利用可否確認
@code-archaeologist
# 期待: エージェントが応答する、またはヘルプが表示される

# コマンドの利用可否確認
/epcc-explore
# 期待: コマンドが実行される、または入力を促される

# フック（設定している場合）の確認
git commit -m "test hooks"
# 期待: 品質ゲートが自動実行される
```

**成功の指標**:
- マーケットプレイスにアクセスできる
- プラグインが一覧に表示される
- `@` メンションでエージェントが応答する
- スラッシュコマンドが認識される
- 適切なトリガーでフックが実行される

## トラブルシューティング

### 問題: マーケットプレイスが見つからない
**症状**: `/plugin marketplace list` に aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock が表示されない  
**原因**: マーケットプレイス未追加、またはネットワーク問題  
**対処**:
```bash
# 再追加
/plugin marketplace add aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock

# インターネット接続を確認
curl -I https://github.com/aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock

# マーケットプレイス設定ファイルを確認
cat ~/.claude/marketplaces.json
```

### 問題: プラグインがインストールできない
**症状**: `/plugin install` が失敗する／一覧に出てこない  
**原因**: バージョン不整合、権限問題、またはキャッシュ破損  
**対処**:
```bash
# プラグインキャッシュを削除
rm -rf ~/.claude/plugins/cache

# バージョンを明示して試す
/plugin install epcc-workflow@1.0.0
# 権限を確認
ls -la ~/.claude/plugins/

# 必要なら再インストール
/plugin uninstall epcc-workflow
/plugin install epcc-workflow
```

### 問題: エージェントが応答しない
**症状**: `@agent-name` が認識されない／動かない  
**原因**: プラグイン未インストール、エージェント名の誤り、プラグイン無効化  
**対処**:
```bash
# インストール済みで有効か確認
/plugin list

# プラグイン内の正確なエージェント名を確認
cat ~/.claude/plugins/epcc-workflow/agents/code-archaeologist.md

# 無効なら有効化
/plugin enable epcc-workflow
# Claude Code セッションを再起動（クリア）
/clear
```

### 問題: コマンドが使えない
**症状**: スラッシュコマンドで "command not found" が出る  
**原因**: プラグイン未インストール、またはコマンド接頭辞が違う  
**対処**:
```bash
# コマンドを提供するプラグインが入っているか確認
/plugin list

# タブ補完で正しいコマンドを探す
/epcc[TAB]

# コマンドファイルが存在するか確認
ls ~/.claude/plugins/epcc-workflow/commands/

# プラグインの再読み込み
/plugin reload
```

### 問題: フックが発火しない
**症状**: PreCommit や PreToolUse フックが実行されない  
**原因**: settings.json の JSON が不正、matcher が不適切、スクリプトに実行権限がない  
**対処**:
```bash
# JSON 構文チェック
python -m json.tool .claude/settings.json

# フックスクリプト権限を確認
ls -la hooks/security_check.py

# 実行権限付与
chmod +x hooks/security_check.py

# フックを直接テスト
python hooks/security_check.py test_file.py < test_file.py

# Claude Code のフックログを確認
cat ~/.claude/logs/hooks.log
```

### 問題: チーム設定が適用されない
**症状**: チームメンバーに必須プラグインが自動導入されない  
**原因**: settings.json がコミットされていない、配置場所が違う、キャッシュ問題  
**対処**:
```bash
# settings.json の場所を確認
ls -la .claude/settings.json

# git にコミットされているか確認
git ls-files .claude/settings.json

# 最新を取得してもらう
git pull origin main

# ローカルプラグインキャッシュ削除
rm -rf ~/.claude/plugins/cache

# インストールを促す
claude /plugin list
```

### 問題: プラグインの競合
**症状**: 複数プラグインで同名のエージェント／コマンドがある  
**原因**: 複数プラグインの機能が重複  
**対処**:
```bash
# 全エージェントを列挙して競合を確認
grep -r "name:" ~/.claude/plugins/*/agents/*.md

# 競合するプラグインを無効化
/plugin disable conflicting-plugin@marketplace

# または完全修飾名で呼び出す
@epcc-workflow/code-archaeologist
```

### 問題: フックの性能問題
**症状**: コミットやファイル操作が極端に遅い  
**原因**: ブロッキングフックの実行時間が長い  
**対処（例）**:
```json
{
  "hooks": {
    "PreCommit": [
      {
        "type": "command",
        "command": "mypy . --ignore-missing-imports",
        "blocking": false,
        "description": "Type checking (non-blocking)"
      }
    ]
  }
}
```

**方針**: 遅いフックは非ブロッキング（警告のみ）にする、またはスクリプトを高速化します。

## 代替アプローチ

### 個人コントリビューター向け
ソロで作業し、チーム強制が不要な場合：

**アプローチ**: 個人用途としてグローバルにプラグインをインストール  
**長所**:
- すべてのプロジェクトで利用できる
- プロジェクトごとの設定が不要
- 試行錯誤が容易

**短所**:
- チームメンバーは同じ設定にならない
- 更新が手動になる

**利用場面**: 個人プロジェクト、探索、学習

**実装方法**:
```bash
# Claude Code のグローバル設定にインストール
/plugin install epcc-workflow
# すべてのプロジェクトで利用可能
cd ~/any-project
@code-archaeologist  # どこでも動作
```

### 大規模組織向け
数百人規模の開発者がいるエンタープライズ導入の場合：

**アプローチ**: 組織デフォルトとして中央集約のプラグイン設定  
**長所**:
- 組織全体でツールの一貫性を確保
- 更新とセキュリティを中央で管理
- 監査／コンプライアンス追跡に寄与

**短所**:
- インフラ整備が必要
- チーム個別の柔軟性は低下

**利用場面**: セキュリティ／コンプライアンス要件があるエンタープライズ環境

**実装方法（例）**:
```bash
# 組織の設定テンプレートを作成
# .claude/org-defaults.json
{
  "requiredMarketplaces": [
    "aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"
  ],
  "requiredPlugins": [
    "security@aws-claude-code-plugins",
    "testing@aws-claude-code-plugins",
    "deployment@aws-claude-code-plugins"
  ],
  "hooks": {
    "PreCommit": [
      {
        "type": "agent",
        "agent": "security-reviewer",
        "blocking": true,
        "args": "--strict --compliance"
      }
    ]
  }
}

# git テンプレートや CI/CD でチームに配布
git clone git@github.com:company/project-template.git
cd project-template
cp .claude/org-defaults.json my-new-project/.claude/settings.json
```

### プラグイン開発向け
マーケットプレイスにない機能が必要な場合：

**アプローチ**: マーケットプレイスプラグインと並行してカスタムプラグインを作成  
**長所**: 独自要件に合わせて拡張できる  
**短所**: 保守負担が増え、プラグイン開発スキルが必要

**利用場面**: 固有のワークフローや社内専用ツールが必要な場合

**実装方法（例）**:
```bash
# マーケットプレイスとローカルプラグインを併用
# .claude/settings.json
{
  "requiredMarketplaces": [
    "aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"
  ],
  "requiredPlugins": [
    "epcc-workflow@aws-claude-code-plugins",
    "security@aws-claude-code-plugins"
  ],
  "localPlugins": [
    ".claude/plugins/custom-workflow",
    ".claude/plugins/company-standards"
  ]
}
```

## ベストプラクティス

**プラグイン選定**:
- Starter Bundle から始め、必要に応じて拡張する
- 実際に使うプラグインだけを導入する
- 導入前にプラグインドキュメントを確認する

**設定管理**:
- `.claude/settings.json` をバージョン管理にコミットする
- プラグイン選定理由をプロジェクト README に記載する
- チームの複数プロジェクトで一貫した設定を使う

**セキュリティ**:
- 本番プロジェクトでは常に security プラグインを有効化する
- フックスクリプトは使用前にレビューする
- セキュリティパッチのためにプラグインを最新化する

**パフォーマンス**:
- 警告用途には非ブロッキングフックを使う
- フックスクリプトを高速化する
- 未使用プラグインはアンインストールではなく無効化する

**チーム設定**:
- 一貫性のため、**`.claude/settings.json` を必ずコミットする**
- プラグインの入手元を明示するため、**`requiredMarketplaces` を使用する**
- **なぜプラグインが必須なのかを記録する**（チーム標準を説明する `description` フィールドを追加）
- **リストは絞る** — 最初は 3～7 個の必須プラグインから始め、必要に応じて拡張
- **必須プラグインを増やしすぎない** — オンボーディング体験と性能を考慮
- **個人の好みをチーム要件に混ぜない** — `requiredPlugins` はチーム標準のみに使う

**説明付きの例:**
```json
{
  "description": "Team standards: EPCC for consistency, security for compliance",
  "requiredMarketplaces": ["aws-solutions-library-samples/guidance-for-claude-code-with-amazon-bedrock"],
  "requiredPlugins": [
    "epcc-workflow@aws-claude-code-plugins",
    "security@aws-claude-code-plugins"
  ]
}
```

## 関連タスク

- [EPCC ワークフローを始める](../tutorials/getting-started-epcc-workflow.md) - 体系的な開発を学ぶ
- [ドキュメントハブ](../README.md) - ドキュメント索引

## さらに読む

- **Claude Code が初めての方**: [Getting Started Guide](https://docs.claude.com/claude-code) →
- **プラグイン仕様が必要な方**: [Plugin Reference](https://docs.claude.com/claude-code/plugins-reference) →
- **プラグインの全詳細**: [Main README](../../README.md#available-plugins) →
- **追加ドキュメント**: [Documentation Hub](../README.md) →
