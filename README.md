# レシピ管理システム

株式会社エブリー 技術課題「レシピ管理システム」の実装です。

## 概要

レシピデータを管理し、ソート機能とナップサック問題（2制約0-1）を解くシステムです。

- **Part1**: データ構造とJSON読み込み
- **Part2**: 自前ソート（標準ソートAPI禁止）、2制約0-1ナップサック問題
- **Part3**: CLIインターフェース

詳細な実行方法とテスト結果については、[実行方法とテスト結果](#実行方法とテスト結果)セクションを参照してください。

## 要件

- Python 3.11+
- 標準ライブラリのみ使用（JSONパース、argparse等）

## プロジェクト構成

```
エブリー_課題/
├── data/                    # テストデータ
│   ├── sample_data.json
│   └── recipes_tiebreak_sort.json
├── src/                     # ソースコード
│   ├── models.py           # データモデル定義
│   ├── loader.py           # JSON読み込み・バリデーション
│   ├── sort.py             # 自前ソート実装（マージソート）
│   ├── knapsack.py         # 2制約0-1ナップサック実装
│   └── main.py             # CLI実装
├── recipe/                  # CLIエントリーポイント
│   └── __main__.py
├── 仕様書.md                # 仕様書
└── TEST_PLAN.md            # テスト計画
```

## インストール

特別なインストールは不要です。Python 3.11以上がインストールされていることを確認してください。

## 実行方法とテスト結果

### プログラムの起動方法

#### 基本コマンド形式

```bash
# Windows PowerShell / macOS/Linux
python -m recipe <command> [options]
```

#### 利用可能なコマンド

1. **レシピ一覧表示**
   ```bash
   python -m recipe list --data <JSONファイルパス>
   ```

2. **レシピソート**
   ```bash
   python -m recipe sort --data <JSONファイルパス> --orderBy <id|name|calories|cookingTime> --order <asc|desc>
   ```

3. **ナップサック問題を解く**
   ```bash
   python -m recipe knapsack --data <JSONファイルパス> --maxCalories <数値> --maxCookingTime <数値>
   ```

### 主要機能のテスト実行例

以下、TEST_PLAN.mdに基づく主要テストケースの実行例と結果を示します。

#### Part1: データ読み込み・バリデーション

**TC-P1-01: 正常JSON読込**

```bash
python -m recipe list --data data/sample_data.json
```

**実行ログ**:
```
Exit Code: 0
```

**出力（stdout）**:
```json
[
  {
    "id": "R001",
    "name": "トマトパスタ",
    "description": "シンプルなトマトパスタ",
    "servings": 2,
    "cookingTime": 15.5,
    "category": "main",
    "nutrition": {
      "calories": 450.5,
      "nutrients": {
        "protein": 18.2
      }
    }
  },
  {
    "id": "R002",
    "name": "チキンサラダ",
    "description": "ヘルシーなチキンサラダ",
    "servings": 1,
    "cookingTime": 10.0,
    "category": "main",
    "nutrition": {
      "calories": 250.0,
      "nutrients": {
        "protein": 30.0
      }
    }
  },
  {
    "id": "R003",
    "name": "味噌汁",
    "description": "定番の味噌汁",
    "servings": 4,
    "cookingTime": 5.0,
    "category": "soup",
    "nutrition": {
      "calories": 50.0,
      "nutrients": {
        "protein": 5.0
      }
    }
  },
  {
    "id": "R004",
    "name": "ハンバーグ",
    "description": "ジューシーなハンバーグ",
    "servings": 2,
    "cookingTime": 30.0,
    "category": "main",
    "nutrition": {
      "calories": 600.0,
      "nutrients": {
        "protein": 40.0
      }
    }
  },
  {
    "id": "R005",
    "name": "サラダ",
    "description": "シンプルなサラダ",
    "servings": 2,
    "cookingTime": 3.0,
    "category": "side",
    "nutrition": {
      "calories": 30.0,
      "nutrients": {
        "protein": 2.0
      }
    }
  },
  {
    "id": "R006",
    "name": "オムライス",
    "description": "ふわふわオムライス",
    "servings": 1,
    "cookingTime": 20.0,
    "category": "main",
    "nutrition": {
      "calories": 550.0,
      "nutrients": {
        "protein": 20.0
      }
    }
  }
]
```

**検証ポイント**:
- ✅ exit code 0（成功）
- ✅ stdoutがJSON形式
- ✅ Raw値（小数）が保持される（例：`cookingTime: 15.5`, `calories: 450.5`）

#### Part2-1: ソート機能

**TC-SORT-01: orderBy=id asc**

```bash
python -m recipe sort --data data/sample_data.json --orderBy id --order asc
```

**実行ログ**:
```
Exit Code: 0
```

**出力（stdout）**:
```json
[
  {
    "id": "R001",
    "name": "トマトパスタ",
    ...
  },
  {
    "id": "R002",
    "name": "チキンサラダ",
    ...
  },
  {
    "id": "R003",
    "name": "味噌汁",
    ...
  },
  {
    "id": "R004",
    "name": "ハンバーグ",
    ...
  },
  {
    "id": "R005",
    "name": "サラダ",
    ...
  },
  {
    "id": "R006",
    "name": "オムライス",
    ...
  }
]
```

**検証ポイント**:
- ✅ IDsが辞書順昇順でソートされる（R001 < R002 < R003 < R004 < R005 < R006）

**TC-SORT-03: orderBy=calories asc（Raw小数比較）**

```bash
python -m recipe sort --data data/sample_data.json --orderBy calories --order asc
```

**実行ログ**:
```
Exit Code: 0
```

**出力（stdout）**:
```json
[
  {
    "id": "R005",
    "name": "サラダ",
    "nutrition": {
      "calories": 30.0,
      ...
    }
  },
  {
    "id": "R003",
    "name": "味噌汁",
    "nutrition": {
      "calories": 50.0,
      ...
    }
  },
  {
    "id": "R002",
    "name": "チキンサラダ",
    "nutrition": {
      "calories": 250.0,
      ...
    }
  },
  {
    "id": "R001",
    "name": "トマトパスタ",
    "nutrition": {
      "calories": 450.5,
      ...
    }
  },
  {
    "id": "R006",
    "name": "オムライス",
    "nutrition": {
      "calories": 550.0,
      ...
    }
  },
  {
    "id": "R004",
    "name": "ハンバーグ",
    "nutrition": {
      "calories": 600.0,
      ...
    }
  }
]
```

**検証ポイント**:
- ✅ Raw値（小数含む）で比較される（450.5が250.0と550.0の間にある）
- ✅ 同値の場合、idが昇順（tie-break）

**TC-SORT-06: desc時のtie-break（Must）**

```bash
python -m recipe sort --data data/recipes_tiebreak_sort.json --orderBy calories --order desc
```

**実行ログ**:
```
Exit Code: 0
```

**出力（stdout）**:
```json
[
  {
    "id": "R020",
    "name": "C",
    "nutrition": {
      "calories": 120.0,
      "nutrients": {
        "protein": 10.0
      }
    }
  },
  {
    "id": "R021",
    "name": "D",
    "nutrition": {
      "calories": 110.0,
      "nutrients": {
        "protein": 10.0
      }
    }
  },
  {
    "id": "R022",
    "name": "E",
    "nutrition": {
      "calories": 110.0,
      "nutrients": {
        "protein": 10.0
      }
    }
  },
  {
    "id": "R010",
    "name": "A",
    "nutrition": {
      "calories": 100.0,
      "nutrients": {
        "protein": 5.0
      }
    }
  },
  {
    "id": "R011",
    "name": "B",
    "nutrition": {
      "calories": 100.0,
      "nutrients": {
        "protein": 6.0
      }
    }
  }
]
```

**検証ポイント**:
- ✅ caloriesは降順（120.0 > 110.0 > 100.0）
- ✅ **calories同値のグループ内ではidが昇順固定**（R021 < R022、R010 < R011）
- ✅ 典型バグ（全体reverseでidまでdescになる）を回避

#### Part2-2: ナップサック問題

**TC-KNAP-01: 出力JSON構造の厳守（Must）**

```bash
python -m recipe knapsack --data data/sample_data.json --maxCalories 1000 --maxCookingTime 50
```

**実行ログ**:
```
Exit Code: 0
```

**出力（stdout）**:
```json
{
  "selectedIds": ["R002", "R003", "R004", "R005"],
  "totalProtein": 77,
  "totalCalories": 930,
  "totalCookingTime": 48
}
```

**検証ポイント**:
- ✅ キーは `selectedIds`, `totalProtein`, `totalCalories`, `totalCookingTime` の4つ
- ✅ `selectedIds` は辞書順昇順（R002 < R003 < R004 < R005）
- ✅ `total*` は整数値（丸め後int合計）

**TC-KNAP-07: 空集合（期待値を固定：Must）**

```bash
python -m recipe knapsack --data data/sample_data.json --maxCalories 0 --maxCookingTime 0
```

**実行ログ**:
```
Exit Code: 0
```

**出力（stdout）**:
```json
{
  "selectedIds": [],
  "totalProtein": 0,
  "totalCalories": 0,
  "totalCookingTime": 0
}
```

**検証ポイント**:
- ✅ 制約が厳しすぎる場合、空集合を返す
- ✅ 出力形式は仕様書に準拠

**TC-KNAP-06: DP上限超過**

```bash
python -m recipe knapsack --data data/sample_data.json --maxCalories 10000 --maxCookingTime 10000
```

**実行ログ**:
```
Exit Code: 1
```

**出力（stderr）**:
```
Error: DP table size exceeds limit: (10000+1)*(10000+1) = 100020001 > 1000000
```

**検証ポイント**:
- ✅ `(maxCalories_int+1)*(maxCookingTime_int+1) > 1,000,000` の場合、exit code 1
- ✅ stderrに理由が表示される

#### エラー処理のテスト

**必須フィールド欠落**

```bash
python -m recipe list --data data/recipes_bad_missing.json
```

**実行ログ**:
```
Exit Code: 1
```

**出力（stderr）**:
```
Error: Missing required field: id
```

**検証ポイント**:
- ✅ exit code 1（エラー）
- ✅ stderrに理由が表示される

### テスト結果要約

#### Mustテストケース（すべて成功）

**Part1: データ読み込み・バリデーション**

| テストケース | 結果 | 検証内容 |
|------------|------|---------|
| TC-P1-01: 正常JSON読込 | ✅ | exit code 0、stdoutがJSON形式、Raw値（小数）が保持される |
| TC-P1-06: protein欠落は0扱い | ✅ | KeyErrorにならず、0として扱われる |

**Part2-1: ソート**

| テストケース | 結果 | 検証内容 |
|------------|------|---------|
| TC-SORT-01: orderBy=id asc | ✅ | IDsが辞書順昇順でソートされる |
| TC-SORT-03: orderBy=calories asc（Raw小数比較） | ✅ | Raw値（小数含む）で比較される |
| TC-SORT-04: tie-break（主キー同値→id昇順） | ✅ | calories同値の場合、idが昇順でソートされる |
| TC-SORT-06: desc時のtie-break（Must） | ✅ | calories降順だが、同値グループ内ではidが昇順固定 |

**Part2-2: ナップサック**

| テストケース | 結果 | 検証内容 |
|------------|------|---------|
| TC-KNAP-01: 出力JSON構造の厳守 | ✅ | キー4つ、selectedIds辞書順昇順、total*は整数値 |
| TC-KNAP-02: 丸め検証（算術四捨五入） | ✅ | `int(math.floor(x + 0.5))`を使用、`2.5 → 3` |
| TC-KNAP-06: DP上限超過 | ✅ | 上限超過時、exit code 1 |
| TC-KNAP-07: 空集合 | ✅ | 制約厳しい場合、空集合を返す |

#### コードレビュー結果

- ✅ **標準ソートAPI禁止**: `grep -R "sorted("` および `grep -R "\.sort("` で該当なし（0件）
- ✅ **自前ソート**: マージソートを実装（安定ソート）
- ✅ **0-1ナップサック**: 重複なし、降順in-place更新で0-1制約を保証

### Windows PowerShellでの実行例

Windows環境での実行例：

```powershell
# レシピ一覧表示
python -m recipe list --data data\sample_data.json

# ソート（calories昇順）
python -m recipe sort --data data\sample_data.json --orderBy calories --order asc

# ナップサック問題
python -m recipe knapsack --data data\sample_data.json --maxCalories 1000 --maxCookingTime 50

# 出力をファイルに保存
python -m recipe list --data data\sample_data.json | Out-File -Encoding utf8 output.json
```

### macOS/Linuxでの実行例

```bash
# レシピ一覧表示
python3 -m recipe list --data data/sample_data.json

# ソート（calories昇順）
python3 -m recipe sort --data data/sample_data.json --orderBy calories --order asc

# ナップサック問題
python3 -m recipe knapsack --data data/sample_data.json --maxCalories 1000 --maxCookingTime 50

# 出力をファイルに保存
python3 -m recipe list --data data/sample_data.json > output.json 2> error.log
echo $? > exitcode.txt
```

### テストログの取得方法

TEST_PLAN.mdに基づき、テスト実行ログを取得する方法：

**Windows PowerShell**:
```powershell
# テストケースの実行とログ保存
python -m recipe list --data data\sample_data.json 1> logs\TC-P1-01_stdout.json 2> logs\TC-P1-01_stderr.txt
$LASTEXITCODE | Out-File logs\TC-P1-01_exitcode.txt

python -m recipe sort --data data\sample_data.json --orderBy calories --order asc 1> logs\TC-SORT-03_stdout.json 2> logs\TC-SORT-03_stderr.txt
$LASTEXITCODE | Out-File logs\TC-SORT-03_exitcode.txt

python -m recipe knapsack --data data\sample_data.json --maxCalories 1000 --maxCookingTime 50 1> logs\TC-KNAP-01_stdout.json 2> logs\TC-KNAP-01_stderr.txt
$LASTEXITCODE | Out-File logs\TC-KNAP-01_exitcode.txt
```

**macOS/Linux**:
```bash
# テストケースの実行とログ保存
python3 -m recipe list --data data/sample_data.json > logs/TC-P1-01_stdout.json 2> logs/TC-P1-01_stderr.txt
echo $? > logs/TC-P1-01_exitcode.txt

python3 -m recipe sort --data data/sample_data.json --orderBy calories --order asc > logs/TC-SORT-03_stdout.json 2> logs/TC-SORT-03_stderr.txt
echo $? > logs/TC-SORT-03_exitcode.txt

python3 -m recipe knapsack --data data/sample_data.json --maxCalories 1000 --maxCookingTime 50 > logs/TC-KNAP-01_stdout.json 2> logs/TC-KNAP-01_stderr.txt
echo $? > logs/TC-KNAP-01_exitcode.txt
```

**コードレビュー（標準ソートAPI禁止の確認）**:
```bash
# 標準ソートAPIの使用を確認
grep -R "sorted(" . --exclude-dir=__pycache__ --exclude-dir=.git
grep -R "\.sort(" . --exclude-dir=__pycache__ --exclude-dir=.git

# Windows PowerShell
Select-String -Path .\src\*.py -Pattern "sorted\(" -Recurse
Select-String -Path .\src\*.py -Pattern "\.sort\(" -Recurse
```

## 実装の特徴

### 1. 算術四捨五入

仕様書3.2に従い、Python標準の`round()`（Banker's rounding）ではなく、算術四捨五入を実装：

```python
def _arithmetic_round(x: float) -> int:
    """算術四捨五入（0.5は常に切り上げ）"""
    return int(math.floor(x + 0.5))
```

### 2. ソートのtie-break

- 主キー（calories/cookingTime等）でソート
- 同値の場合、id昇順（文字列辞書順）
- **descでもidは昇順固定**（仕様書5.4）

### 3. ナップサックのtie-break

最終解は以下の順で一意に決定（仕様書6.5）：

1. 合計 protein_int 最大
2. 合計 calories_int 最小
3. 合計 cookingTime_int 最小
4. selectedIds（辞書順昇順）のリスト辞書順が最小

### 4. 0-1ナップサックの実装

- 降順in-place更新で0-1制約を保証
- parentテーブルに`prev_i`を含めて循環を防止
- 経路復元時に重複なしを保証

## 検証コマンド

### tie-break検証（recipes_tiebreak_sort.json使用）

```bash
# calories asc + tie-break確認
python3 -m recipe sort --data data/recipes_tiebreak_sort.json --orderBy calories --order asc

# calories desc + tie-break確認（Must）
python3 -m recipe sort --data data/recipes_tiebreak_sort.json --orderBy calories --order desc
```

**期待される結果**:
- asc: calories昇順、同値グループ内でid昇順
- desc: calories降順、**同値グループ内でもid昇順固定**

## エラー処理

- 成功時: exit code 0
- エラー時: exit code 1、stderrにエラーメッセージ

エラー例:
- JSON構文エラー
- 必須フィールド欠落
- ID重複/空文字
- 負の数値
- DPテーブル上限超過

## 仕様書準拠

本実装は`仕様書.md`に完全準拠しています：

- ✅ 標準ソートAPI禁止
- ✅ Raw値と計算値の分離
- ✅ 算術四捨五入（0.5は常に切り上げ）
- ✅ tie-break規則の厳密な実装
- ✅ 出力JSON形式の厳守
- ✅ エラー処理と終了コード

詳細は`仕様書.md`を参照してください。

## AI利用について

本課題の設計および実装にあたり、生成AIを補助的に利用しました。
最終的な設計判断・実装・検証・提出物の内容については、すべて本人が確認したうえで行っています。

### 利用したAI
- ChatGPT：仕様整理、設計方針の検討、レビュー補助
- Cursor：実装補助（コード生成・差分修正）
- Gemini / Claude：仕様書レビュー、設計上のリスク指摘

### 利用目的
- 課題要件の解釈整理と仕様書の明確化
- アルゴリズム設計（自前ソート、2制約0-1ナップサック）の方針検討
- 実装上の不具合や曖昧点の洗い出し

### 利用していないこと
- 課題要件そのものの改変
- 無検証の自動生成コードの提出
- 外部ライブラリによるアルゴリズム代替

生成AIはあくまで補助的なツールとして利用し、最終責任はすべて本人が負っています。


## ライセンス

本プロジェクトは技術課題の提出物です。

