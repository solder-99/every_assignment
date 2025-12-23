"""
自前ソート機能（標準ソートAPI禁止）
マージソートを使用（安定ソート）
"""
import sys
import os
from typing import List, Callable

# プロジェクトルートをパスに追加
if __name__ != "__main__":
    # モジュールとしてインポートされる場合
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.models import Recipe


def sort_recipes(recipes: List[Recipe], order_by: str, order: str) -> List[Recipe]:
    """
    レシピリストをソートする
    
    Args:
        recipes: ソート対象のレシピリスト
        order_by: ソートキー（id|name|calories|cookingTime）
        order: ソート順（asc|desc）
        
    Returns:
        ソート済みレシピリスト（新しいリスト）
    """
    if order_by not in ['id', 'name', 'calories', 'cookingTime']:
        raise ValueError(f"不正なorderBy: {order_by}")
    if order not in ['asc', 'desc']:
        raise ValueError(f"不正なorder: {order}")
    
    # 比較関数を作成
    compare_func = _create_compare_func(order_by, order)
    
    # マージソートでソート（安定ソート）
    return _merge_sort(recipes, compare_func)


def _create_compare_func(order_by: str, order: str) -> Callable[[Recipe, Recipe], int]:
    """
    比較関数を作成
    
    Returns:
        比較関数（a < b なら負、a == b なら0、a > b なら正）
    """
    def compare_id(a: Recipe, b: Recipe) -> int:
        """ID比較（文字列辞書順）"""
        if a.id < b.id:
            return -1
        elif a.id > b.id:
            return 1
        return 0
    
    def compare_name(a: Recipe, b: Recipe) -> int:
        """名前比較（文字列辞書順）"""
        if a.name < b.name:
            return -1
        elif a.name > b.name:
            return 1
        # tie-break: id昇順
        return compare_id(a, b)
    
    def compare_calories(a: Recipe, b: Recipe, reverse: bool = False) -> int:
        """カロリー比較（Raw値）"""
        if a.nutrition.calories < b.nutrition.calories:
            return 1 if reverse else -1
        elif a.nutrition.calories > b.nutrition.calories:
            return -1 if reverse else 1
        # tie-break: id昇順（常に昇順、reverseに関係なく）
        return compare_id(a, b)
    
    def compare_cooking_time(a: Recipe, b: Recipe, reverse: bool = False) -> int:
        """調理時間比較（Raw値）"""
        if a.cookingTime < b.cookingTime:
            return 1 if reverse else -1
        elif a.cookingTime > b.cookingTime:
            return -1 if reverse else 1
        # tie-break: id昇順（常に昇順、reverseに関係なく）
        return compare_id(a, b)
    
    # 比較関数を選択
    if order_by == 'id':
        base_compare = compare_id
        # idの場合は降順でも符号反転でOK（tie-breakなし）
        if order == 'desc':
            return lambda a, b: -base_compare(a, b)
        else:
            return base_compare
    elif order_by == 'name':
        base_compare = compare_name
        # nameの場合は降順でも符号反転でOK（tie-breakはid昇順固定）
        if order == 'desc':
            return lambda a, b: -base_compare(a, b)
        else:
            return base_compare
    elif order_by == 'calories':
        # 降順の場合、主キーのみ反転、tie-breakは常にid昇順
        if order == 'desc':
            return lambda a, b: compare_calories(a, b, reverse=True)
        else:
            return lambda a, b: compare_calories(a, b, reverse=False)
    else:  # cookingTime
        # 降順の場合、主キーのみ反転、tie-breakは常にid昇順
        if order == 'desc':
            return lambda a, b: compare_cooking_time(a, b, reverse=True)
        else:
            return lambda a, b: compare_cooking_time(a, b, reverse=False)


def _merge_sort(arr: List[Recipe], compare: Callable[[Recipe, Recipe], int]) -> List[Recipe]:
    """
    マージソート（安定ソート）
    
    Args:
        arr: ソート対象リスト
        compare: 比較関数
        
    Returns:
        ソート済みリスト
    """
    if len(arr) <= 1:
        return arr.copy()
    
    mid = len(arr) // 2
    left = _merge_sort(arr[:mid], compare)
    right = _merge_sort(arr[mid:], compare)
    
    return _merge(left, right, compare)


def _merge(left: List[Recipe], right: List[Recipe], compare: Callable[[Recipe, Recipe], int]) -> List[Recipe]:
    """マージ処理"""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if compare(left[i], right[j]) <= 0:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    # 残りを追加
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result
