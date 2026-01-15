"""
2制約0-1ナップサック問題の実装
重み1: calories_int（丸め後整数）
重み2: cookingTime_int（丸め後整数）
価値: protein_int（丸め後整数）
"""
import math
import sys
import os
from typing import List, Tuple, Optional

# プロジェクトルートをパスに追加
if __name__ != "__main__":
    # モジュールとしてインポートされる場合
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.models import Recipe


def _arithmetic_round(x: float) -> int:
    """
    算術四捨五入（0.5は常に切り上げ）
    
    仕様書3.2に従い、Python標準のround()（Banker's rounding）ではなく、
    算術四捨五入を実装する。
    
    Args:
        x: 非負数（calories, cookingTime, protein）
        
    Returns:
        丸め後の整数値
    """
    return int(math.floor(x + 0.5))


def solve_knapsack(recipes: List[Recipe], max_calories: float, max_cooking_time: float) -> dict:
    """
    ナップサック問題を解く
    
    Args:
        recipes: レシピリスト
        max_calories: 最大カロリー（Raw値）
        max_cooking_time: 最大調理時間（Raw値、分）
        
    Returns:
        選択されたレシピIDと合計値の辞書
        
    Raises:
        SystemExit: DPテーブル上限超過時（exit code 1）
    """
    # Raw値を整数に丸める（算術四捨五入）
    max_calories_int = _arithmetic_round(max_calories)
    max_cooking_time_int = _arithmetic_round(max_cooking_time)
    
    # レシピをID昇順にソート（tie-breakのため）
    recipes_sorted = _sort_by_id(recipes)
    
    # 各レシピの整数値を計算
    recipe_values = []
    for recipe in recipes_sorted:
        calories_int = _arithmetic_round(recipe.nutrition.calories)
        cooking_time_int = _arithmetic_round(recipe.cookingTime)
        protein_int = _arithmetic_round(recipe.nutrition.get_protein())
        
        recipe_values.append({
            'recipe': recipe,
            'calories_int': calories_int,
            'cooking_time_int': cooking_time_int,
            'protein_int': protein_int
        })
    
    # DPテーブルサイズチェック
    table_size = (max_calories_int + 1) * (max_cooking_time_int + 1)
    if table_size > 1_000_000:
        print(
            f"Error: DPテーブルサイズが上限を超えています: {table_size} > 1,000,000",
            file=sys.stderr
        )
        sys.exit(1)
    
    # DP実行
    dp, parent = _solve_dp(recipe_values, max_calories_int, max_cooking_time_int)
    
    # 最終解を選択（tie-break (1)-(4)を厳密に適用）
    # 理由：セル座標(c,t)ではなく、実際の合計値(protein, calories, cookingTime)でtie-breakする必要がある
    # セル(c,t)は制約を満たす最大proteinを表すが、実際の合計calories/cookingTimeはc/t以下である可能性がある
    best_c, best_t = _select_final_solution(
        dp, parent, recipe_values, max_calories_int, max_cooking_time_int
    )
    
    # 経路復元
    selected_indices = _reconstruct_path(parent, best_c, best_t, len(recipe_values), max_calories_int, max_cooking_time_int)
    
    # 選択されたレシピIDを取得
    selected_ids = [recipe_values[i]['recipe'].id for i in selected_indices]
    
    # IDリストを辞書順昇順でソート（自前実装）
    selected_ids = _sort_ids(selected_ids)
    
    # 合計値を計算（整数値）
    total_protein = sum(recipe_values[i]['protein_int'] for i in selected_indices)
    total_calories = sum(recipe_values[i]['calories_int'] for i in selected_indices)
    total_cooking_time = sum(recipe_values[i]['cooking_time_int'] for i in selected_indices)
    
    return {
        'selectedIds': selected_ids,
        'totalProtein': total_protein,
        'totalCalories': total_calories,
        'totalCookingTime': total_cooking_time
    }


def _sort_by_id(recipes: List[Recipe]) -> List[Recipe]:
    """
    ID昇順でソート（自前実装、標準ソートAPI禁止）
    バブルソートを使用（簡単な実装）
    """
    result = recipes.copy()
    n = len(result)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j].id > result[j + 1].id:
                # swap
                result[j], result[j + 1] = result[j + 1], result[j]
    
    return result


def _sort_ids(ids: List[str]) -> List[str]:
    """
    IDリストを辞書順昇順でソート（自前実装、標準ソートAPI禁止）
    バブルソートを使用
    """
    result = ids.copy()
    n = len(result)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if result[j] > result[j + 1]:
                # swap
                result[j], result[j + 1] = result[j + 1], result[j]
    
    return result


def _solve_dp(recipe_values: List[dict], max_calories: int, max_cooking_time: int) -> Tuple[List[List[int]], List[List[Optional[Tuple[int, int, int, int]]]]]:
    """
    DPを実行
    
    Returns:
        (dp, parent)
        dp[c][t] = 最大protein_int
        parent[c][t] = (prev_c, prev_t, recipe_index, prev_i) または None
        prev_i: 前のアイテム位置（経路復元時の循環防止用）
    """
    n = len(recipe_values)
    
    # dp[c][t] = 最大protein_int
    dp = [[0] * (max_cooking_time + 1) for _ in range(max_calories + 1)]
    
    # parent[c][t] = (prev_c, prev_t, recipe_index, prev_i) または None
    # prev_i: 前のアイテム位置（経路復元時に i を減らすことで循環を防ぐ）
    parent = [[None] * (max_cooking_time + 1) for _ in range(max_calories + 1)]
    
    # 各レシピについて
    for recipe_idx, rv in enumerate(recipe_values):
        calories = rv['calories_int']
        cooking_time = rv['cooking_time_int']
        protein = rv['protein_int']
        
        # 0-1ナップサック: 降順in-place更新で0-1制約を保証
        # 理由: 降順更新により、dp[prev_c][prev_t]はまだ更新されていない（前のレシピまでの値）ので、
        # 同じレシピを複数回選ぶことを防げる
        # 昇順更新だと、同じレシピを複数回選んでしまう可能性がある
        for c in range(max_calories, calories - 1, -1):
            for t in range(max_cooking_time, cooking_time - 1, -1):
                # このレシピを選ばない場合（現在の値）
                current_value = dp[c][t]
                
                # このレシピを選ぶ場合（前のレシピまでのDPテーブルを参照）
                prev_c = c - calories
                prev_t = t - cooking_time
                if prev_c < 0 or prev_t < 0:
                    continue
                
                new_value = dp[prev_c][prev_t] + protein
                
                # 更新（より良い値の場合のみ）
                # 重要: parentテーブルは(prev_c, prev_t, recipe_idx, prev_i)を保存する
                # prev_i は parent[prev_c][prev_t] から取得（経路復元時に i が減ることを保証）
                if new_value > current_value:
                    dp[c][t] = new_value
                    # prev_i を parent[prev_c][prev_t] から取得
                    # parent[prev_c][prev_t] が None の場合は prev_i = -1（最初のレシピ）
                    if parent[prev_c][prev_t] is not None:
                        _, _, _, prev_i = parent[prev_c][prev_t]
                    else:
                        prev_i = -1  # 最初のレシピまで遡った
                    parent[c][t] = (prev_c, prev_t, recipe_idx, prev_i)
    
    return dp, parent


def _select_final_solution(
    dp: List[List[int]],
    parent: List[List[Optional[Tuple[int, int, int, int]]]],
    recipe_values: List[dict],
    max_calories: int,
    max_cooking_time: int
) -> Tuple[int, int]:
    """
    最終解を選択（tie-break (1)-(4)を厳密に適用）
    
    tie-break規則：
    1. totalProtein_int 最大
    2. totalCalories_int 最小
    3. totalCookingTime_int 最小
    4. selectedIds（辞書順昇順）のリスト辞書順が最小
    
    理由：セル座標(c,t)ではなく、実際の合計値で比較する必要がある。
    セル(c,t)から復元したレシピ組合せの合計calories/cookingTimeは、必ずしもc/tと等しくない。
    
    Returns:
        (best_c, best_t)
    """
    # ステップ1: 最大protein_intを持つ全てのセルを集める
    max_protein = -1
    max_protein_cells = []
    for c in range(max_calories + 1):
        for t in range(max_cooking_time + 1):
            if dp[c][t] > max_protein:
                max_protein = dp[c][t]
                max_protein_cells = [(c, t)]
            elif dp[c][t] == max_protein:
                max_protein_cells.append((c, t))
    
    # エッジケース: 全てのセルが0の場合でも、セル(0,0)は存在するはずだが、念のためチェック
    if not max_protein_cells:
        return 0, 0
    
    # ステップ2: 各セルから復元して、実際の合計値でtie-break (1)-(3)を適用
    candidates = []
    best_total_protein = -1
    best_total_calories = max_calories + 1
    best_total_cooking_time = max_cooking_time + 1
    
    for c, t in max_protein_cells:
        # 経路復元して実際の合計値を計算
        selected_indices = _reconstruct_path(parent, c, t, len(recipe_values), max_calories, max_cooking_time)
        total_protein = sum(recipe_values[i]['protein_int'] for i in selected_indices)
        total_calories = sum(recipe_values[i]['calories_int'] for i in selected_indices)
        total_cooking_time = sum(recipe_values[i]['cooking_time_int'] for i in selected_indices)
        
        # tie-break (1)-(3)で候補を絞り込む
        if total_protein > best_total_protein:
            # (1) protein最大で更新
            best_total_protein = total_protein
            best_total_calories = total_calories
            best_total_cooking_time = total_cooking_time
            candidates = [(c, t, total_protein, total_calories, total_cooking_time)]
        elif total_protein == best_total_protein:
            if total_calories < best_total_calories:
                # (2) calories最小で更新
                best_total_calories = total_calories
                best_total_cooking_time = total_cooking_time
                candidates = [(c, t, total_protein, total_calories, total_cooking_time)]
            elif total_calories == best_total_calories:
                if total_cooking_time < best_total_cooking_time:
                    # (3) cookingTime最小で更新
                    best_total_cooking_time = total_cooking_time
                    candidates = [(c, t, total_protein, total_calories, total_cooking_time)]
                elif total_cooking_time == best_total_cooking_time:
                    # (1)-(3)が全て同値の候補
                    candidates.append((c, t, total_protein, total_calories, total_cooking_time))
    
    # ステップ3: 候補が1つならそれを返す
    if len(candidates) == 1:
        return candidates[0][0], candidates[0][1]
    
    # ステップ4: 候補が複数ある場合、tie-break (4)で最終決定
    # IDリスト（辞書順昇順にソート済み）の辞書順比較で最小を選ぶ
    best_c, best_t = candidates[0][0], candidates[0][1]
    best_id_list = _get_id_list_from_cell(parent, best_c, best_t, recipe_values, max_calories, max_cooking_time)
    
    for c, t, _, _, _ in candidates[1:]:
        id_list = _get_id_list_from_cell(parent, c, t, recipe_values, max_calories, max_cooking_time)
        
        # Pythonのlist辞書順比較（先頭から比較、短い方が先に終われば小さい）
        if _compare_id_lists(id_list, best_id_list) < 0:
            best_c, best_t = c, t
            best_id_list = id_list
    
    return best_c, best_t


def _get_id_list_from_cell(
    parent: List[List[Optional[Tuple[int, int, int, int]]]],
    c: int,
    t: int,
    recipe_values: List[dict],
    max_calories: int,
    max_cooking_time: int
) -> List[str]:
    """
    セルから経路復元してIDリストを取得（辞書順昇順でソート済み）
    """
    selected_indices = _reconstruct_path(parent, c, t, len(recipe_values), max_calories, max_cooking_time)
    selected_ids = [recipe_values[i]['recipe'].id for i in selected_indices]
    return _sort_ids(selected_ids)


def _compare_id_lists(list_a: List[str], list_b: List[str]) -> int:
    """
    IDリストの辞書順比較（Pythonのlist比較準拠）
    
    Returns:
        list_a < list_b なら負、list_a == list_b なら0、list_a > list_b なら正
    """
    min_len = min(len(list_a), len(list_b))
    for i in range(min_len):
        if list_a[i] < list_b[i]:
            return -1
        elif list_a[i] > list_b[i]:
            return 1
    
    # 先頭が同じ場合、短い方が小さい
    if len(list_a) < len(list_b):
        return -1
    elif len(list_a) > len(list_b):
        return 1
    return 0


def _reconstruct_path(parent: List[List[Optional[Tuple[int, int, int, int]]]], 
                     best_c: int, best_t: int, n_recipes: int,
                     max_calories: int, max_cooking_time: int) -> List[int]:
    """
    経路復元して選択されたレシピのインデックスを取得
    
    降順in-place更新により0-1制約は保証されているため、
    parent[c][t]がNoneになるまで経路を辿れば良い
    
    Returns:
        選択されたレシピのインデックスリスト（重複なし）
    """
    selected_indices = []
    c = best_c
    t = best_t
    
    # parent[c][t]がNoneになるまで経路を辿る
    while parent[c][t] is not None:
        prev_c, prev_t, recipe_idx, prev_i = parent[c][t]
        selected_indices.append(recipe_idx)
        c = prev_c
        t = prev_t
    
    return selected_indices
