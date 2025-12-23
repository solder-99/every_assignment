# TEST_PLAN.md（最終版）

## 1. テスト目的

本TEST_PLANは、仕様書.mdに対する合否判定用テスト計画であり、
本計画に記載の Must テストケースをすべて満たすことを合格条件とする。
本テスト計画は、レシピ管理システム実装が仕様書に定義された必須要件（Part1/Part2）を満たすことを、**手動実行＋ログ確認**で検証する。
テストの実行ログ（コマンド、stdout(JSON)、stderr、終了コード）を提出用の証跡として残し、採点者が同じ手順で再現できる形を保証する。

Must は未達の場合に不合格、Should は評価加点または品質確認目的とする。

---

## 2. テスト範囲

### 2.1 Part1（データ構造）

* JSON読み込み（5件以上を想定）
* 必須/任意フィールドの扱い
* 値の妥当性（id一意・空文字不可、負値）
* Nutrition：`nutrients["protein"]` 欠落時は 0 扱い

### 2.2 Part2-1（ソート）

* `orderBy(id|name|calories|cookingTime)` と `order(asc|desc)`
* 標準ソートAPI禁止（自前ソートのみ）
* `calories/cookingTime` は **Raw値（小数含む）**で比較
* tie-break：主キー → **id昇順（固定）**（descでも変えない）

### 2.3 Part2-2（ナップサック）

* 2制約0-1（calories/time制約下でprotein最大）
* DP直前のみ **算術四捨五入**で整数化（calories_int/time_int/protein_int）
* 密DP上限式の順守
* 同点解 tie-break：protein→cal→time→IDリスト辞書順（Python list比較準拠）
* knapsack出力JSON構造（キー/型/合計値定義）順守

---

## 3. テスト方針

* **手動テスト**（CLI実行・ログ確認）。自動テストFWは使用しない
* stdoutは **常にJSONのみ**（人間向け文章・表形式を混ぜない）
* stderrは内容自由（文面一致は不要）。ただし **異常系で理由が分かること**を確認する
* 成功時 exit code 0、異常時 exit code 1
* **再現性優先**：同一データ・同一コマンドで同一結果が出ること（決定性）
* 標準ソートAPI禁止は「実行結果」だけで断定できないため、**コードレビュー（grep）を必須工程**に含める

---

## 4. テスト環境

* Python：3.11+（標準ライブラリのみ）
* OS：任意（Windows/macOS/Linux）
* 文字コード：UTF-8

---

## 5. テスト観点一覧（要件 → 観点 → 合否基準）

| 要件                | 観点       | 合否基準                                        |
| ----------------- | -------- | ------------------------------------------- |
| stdoutはJSONのみ     | 出力形式     | stdoutがJSONとしてパース可能（余計な文字列なし）               |
| exit code         | 成功/失敗    | 成功=0、失敗=1                                   |
| Raw保持             | 表示・ソート   | list/sortの表示・比較にRaw小数が反映                    |
| 標準ソート禁止           | 実装順守     | grep/目視で `sorted`/`.sort`/`Array.sort` 等が不在 |
| tie-break（desc含む） | 降順時の第2キー | 主キーdescでも **idは昇順固定**                       |
| 丸め仕様              | 四捨五入     | `2.5 → 3` を満たす（Banker’sではない）                |
| DP上限              | 計算量制御    | 1,000,000以内は実行、超過はエラー(1)                    |
| knapsack最適性       | 解の優先順位   | protein→cal→time→IDリスト辞書順で一意に決定             |
| protein欠落         | デフォルト値   | KeyErrorにならず 0 扱いで動作                        |
| timerSec無視        | 仕様意図の保証  | timerSec異常値でも落ちず、knapsack結果にも影響しない          |

---

## 6. テストデータ（フィクスチャ）

`data/` 配下に以下を用意（ファイル名例）。
※サンプルデータは自作でよいが、ここで指定する条件を満たすこと。

* `recipes_ok.json`：正常系（5件以上、小数含む、knapsackが空にならない）
* `recipes_tiebreak_sort.json`：ソート同値（主キー同値でid差あり、desc検証にも使う）
* `recipes_rounding.json`：丸め検証専用（**2.5を含む**）
* `recipes_tiebreak_knapsack.json`：knapsack同点解専用（具体例はTC-KNAP-04参照）
* `recipes_missing_protein.json`：protein欠落（nutrientsはあるがproteinキー無し）
* `recipes_timersec_ignored.json`：timerSec異常値入り
* `recipes_bad_missing.json` / `recipes_bad_duplicate_id.json` / `recipes_bad_empty_id.json` / `recipes_bad_negative.json`

---

## 7. テストケース

> コマンド例は `python -m recipe ...` 形式。実装に合わせて置換してよい。
> すべてのケースで共通：stdoutはJSONのみ／exit code確認。

### 7.1 Part1：読み込み・バリデーション

**TC-P1-01 正常JSON読込**

* 入力：`data/recipes_ok.json`
* 実行：`recipe list --data data/recipes_ok.json`
* OK基準：

  * exit 0
  * stdoutがJSON
  * 小数が表示される（Raw保持）

**TC-P1-02 必須欠落**

* 入力：`data/recipes_bad_missing.json`
* OK基準：exit 1、stderrに理由（文面一致不要）

**TC-P1-03 id重複**

* 入力：`data/recipes_bad_duplicate_id.json`
* OK基準：exit 1、stderrに理由

**TC-P1-04 id空文字**

* 入力：`data/recipes_bad_empty_id.json`
* OK基準：exit 1、stderrに理由

**TC-P1-05 負値**

* 入力：`data/recipes_bad_negative.json`
* OK基準：exit 1、stderrに理由

**TC-P1-06 protein欠落は0扱い（Must）**

* 入力：`data/recipes_missing_protein.json`
* 実行1：`recipe list --data ...`
* OK基準：

  * exit 0
  * 落ちない（KeyError等なし）
* 実行2：`recipe knapsack --data ... --maxCalories 9999 --maxCookingTime 9999`
* OK基準：

  * exit 0
  * 落ちない
  * 欠落proteinレシピは価値0として扱われ、結果に矛盾がない（少なくとも例外にならない）

**TC-P1-07 timerSec異常値でも落ちない（Should）**

* 入力：`data/recipes_timersec_ignored.json`（例：timerSec=-9999 や 1e12）
* 実行：`recipe list --data ...`
* OK基準：exit 0、stdoutがJSON（timerSec検証は必須ではないため、落ちないことを確認）

---

### 7.2 Part2-1：ソート

**TC-SORT-01 orderBy=id asc**

* 実行：`recipe sort --data data/recipes_ok.json --orderBy id --order asc`
* OK基準：idが文字列辞書順で昇順

**TC-SORT-02 orderBy=name asc**

* OK基準：言語標準の文字列比較順

**TC-SORT-03 orderBy=calories asc（Raw小数比較）**

* 入力条件：450.4 と 450.5 を含む
* OK基準：450.4 が先（丸めが混ざらない）

**TC-SORT-04 tie-break（主キー同値→id昇順）**

* 実行：`recipe sort --data data/recipes_tiebreak_sort.json --orderBy calories --order asc`
* OK基準：calories同値なら id 昇順

**TC-SORT-06 desc時のtie-break（Must）**

* 実行：`recipe sort --data data/recipes_tiebreak_sort.json --orderBy calories --order desc`
* OK基準：

  * caloriesはdesc
  * **calories同値のグループ内では id が昇順（固定）**
  * 典型バグ（全体reverseでidまでdescになる）を検出できる

---

### 7.3 Part2-2：ナップサック

**TC-KNAP-01 基本（出力JSON構造の厳守：Must）**

* 実行：`recipe knapsack --data data/recipes_ok.json --maxCalories 1200 --maxCookingTime 45`
* OK基準（stdout JSONが以下を満たす）：

```json
{
  "selectedIds": ["R001", "R003"],
  "totalProtein": 55,
  "totalCalories": 1100,
  "totalCookingTime": 40
}
```

* 厳守事項：

  * キーは `selectedIds,totalProtein,totalCalories,totalCookingTime` の4つ
  * `selectedIds` は辞書順昇順
  * `total*` は **丸め後int合計の整数**

**TC-KNAP-02 丸め検証（算術四捨五入を固定：Must）**

* 入力：`data/recipes_rounding.json`
* データ条件（必須）：

  * `protein = 2.5` を含むレシピ（ほかの値は自由）
* 合否判定を一意にする手順：

  1. `maxCalories/maxCookingTime` を十分大にして knapsack を実行
  2. 出力 `totalProtein` が「算術四捨五入」で集計されていることを確認
* OK基準：

  * `2.5` は **3** として扱われる（Banker’s roundなら2になりうるため差分で検出）

**TC-KNAP-03 bestセル探索（protein同値→cal最小→time最小）**

* OK基準：最大proteinの中でcal最小、次にtime最小が選ばれる

**TC-KNAP-04 tie-break（IDリスト辞書順最小：Must）**

* 入力：`data/recipes_tiebreak_knapsack.json`
* データ条件（具体例：これが成立するようにデータを作る）

  * 2つの組合せが **同じ (protein_int, calories_int, time_int)** になる
  * 例：以下の2案が同点になるように設計

    * 案A：`selectedIds = ["R001", "R010"]`
    * 案B：`selectedIds = ["R002", "R003"]`
  * Pythonのlist比較では `["R001","R010"] < ["R002","R003"]`（先頭比較でR001が小さい）
* 実行：`recipe knapsack --data ... --maxCalories ... --maxCookingTime ...`
* OK基準：**案Aが選ばれる**

**TC-KNAP-05 DP上限ちょうど**

* 条件：`(maxCalories_int+1)*(maxCookingTime_int+1) == 1,000,000`
* OK基準：exit 0

**TC-KNAP-06 DP上限超過**

* 条件：`> 1,000,000`
* OK基準：exit 1

**TC-KNAP-07 空集合（期待値を固定：Must）**

* 実行：`recipe knapsack --data data/recipes_ok.json --maxCalories 0 --maxCookingTime 0`
* OK基準（stdout JSONを以下に固定）：

```json
{
  "selectedIds": [],
  "totalProtein": 0,
  "totalCalories": 0,
  "totalCookingTime": 0
}
```

* 注：仕様書は空集合を禁止していないため、**“提出用の一意な期待値”**としてここで固定する（実装者が迷わないため）

---

## 8. CLI引数の異常系（Should）

**TC-CLI-01 未知のorderBy**

* 実行：`recipe sort --data data/recipes_ok.json --orderBy foo --order asc`
* OK基準：exit 1（argparseのエラーでも可）、stdoutはJSONを維持できれば望ましいが必須ではない

**TC-CLI-02 orderがasc/desc以外**

* 実行：`recipe sort --data ... --orderBy id --order up`
* OK基準：exit 1

**TC-CLI-03 maxCaloriesが非数**

* 実行：`recipe knapsack --data ... --maxCalories abc --maxCookingTime 10`
* OK基準：exit 1

---

## 9. コードレビュー手順（禁止API検出：Should）

実行前に、リポジトリ全体に対して以下を確認し、結果をログ化する。

* 例（grep）：

  * `grep -R "sorted(" -n .`
  * `grep -R "\.sort(" -n .`
* OK基準：該当なし（0件）

※言語標準の比較演算子 `< > ==` の使用は許可されているため検出対象外。

---

## 10. テスト実行手順（ログ作成）

### 10.1 ログ命名規則（Should）

* `logs/<TC-ID>_stdout.json`
* `logs/<TC-ID>_stderr.txt`
* `logs/<TC-ID>_exitcode.txt`

例：`logs/TC-KNAP-01_stdout.json`

### 10.2 取得方法（例）

* macOS/Linux：

  * `python -m recipe ... > logs/TC-XXX_stdout.json 2> logs/TC-XXX_stderr.txt; echo $? > logs/TC-XXX_exitcode.txt`
* Windows PowerShell：

  * `python -m recipe ... 1> logs\TC-XXX_stdout.json 2> logs\TC-XXX_stderr.txt`
  * `$LASTEXITCODE | Out-File logs\TC-XXX_exitcode.txt`

---

## 11. テスト結果の記録方法（提出への転用）

提出物の「実行方法とテスト結果」には、最低限以下を掲載する：

* 実行コマンド（コピペ可能）
* stdout（JSONファイル添付 or 主要部分貼付）
* exit code（0/1）
* 期待値に対してOKである根拠（1行）

---