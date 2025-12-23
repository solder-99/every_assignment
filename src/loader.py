"""
JSONファイルからレシピデータを読み込む機能
"""
import json
import sys
import os
from typing import List

# プロジェクトルートをパスに追加
if __name__ != "__main__":
    # モジュールとしてインポートされる場合
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

from src.models import Recipe, Ingredient, Amount, Step, Nutrition


def load_recipes(json_path: str) -> List[Recipe]:
    """
    JSONファイルからレシピリストを読み込む
    
    Args:
        json_path: JSONファイルのパス
        
    Returns:
        レシピのリスト
        
    Raises:
        SystemExit: エラー時（exit code 1）
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: ファイルが見つかりません: {json_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: JSON構文エラー: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(data, list):
        print("Error: JSONは配列である必要があります", file=sys.stderr)
        sys.exit(1)
    
    recipes = []
    seen_ids = set()
    
    for idx, item in enumerate(data):
        try:
            recipe = _parse_recipe(item, idx)
            
            # ID重複チェック
            if recipe.id in seen_ids:
                print(f"Error: IDが重複しています: {recipe.id}", file=sys.stderr)
                sys.exit(1)
            if not recipe.id:  # 空文字チェック
                print(f"Error: IDが空文字です（インデックス {idx}）", file=sys.stderr)
                sys.exit(1)
            
            seen_ids.add(recipe.id)
            recipes.append(recipe)
            
        except KeyError as e:
            print(f"Error: 必須フィールドが欠落しています（インデックス {idx}）: {e}", file=sys.stderr)
            sys.exit(1)
        except (ValueError, TypeError) as e:
            print(f"Error: データ型エラー（インデックス {idx}）: {e}", file=sys.stderr)
            sys.exit(1)
    
    return recipes


def _parse_recipe(item: dict, idx: int) -> Recipe:
    """辞書からRecipeオブジェクトを生成"""
    
    # 必須フィールドチェック
    required_fields = ['id', 'name', 'servings', 'cookingTime', 'category', 'ingredients', 'steps', 'nutrition']
    for field in required_fields:
        if field not in item:
            raise KeyError(field)
    
    # Nutrition
    nutrition_data = item['nutrition']
    if not isinstance(nutrition_data, dict) or 'calories' not in nutrition_data:
        raise ValueError("nutrition.calories が必須です")
    
    nutrients = nutrition_data.get('nutrients', {})
    if not isinstance(nutrients, dict):
        nutrients = {}
    
    nutrition = Nutrition(
        calories=float(nutrition_data['calories']),
        nutrients={k: float(v) for k, v in nutrients.items()}
    )
    
    # Ingredients
    ingredients = []
    for ing_data in item['ingredients']:
        if 'name' not in ing_data or 'amount' not in ing_data:
            raise ValueError("ingredient.name と ingredient.amount が必須です")
        
        amount_data = ing_data['amount']
        if 'raw' not in amount_data:
            raise ValueError("ingredient.amount.raw が必須です")
        
        amount = Amount(
            raw=amount_data['raw'],
            value=amount_data.get('value'),
            unit=amount_data.get('unit')
        )
        
        ingredients.append(Ingredient(
            name=ing_data['name'],
            amount=amount
        ))
    
    # Steps
    steps = []
    for step_data in item['steps']:
        if 'order' not in step_data or 'text' not in step_data:
            raise ValueError("step.order と step.text が必須です")
        
        steps.append(Step(
            order=int(step_data['order']),
            text=step_data['text'],
            timerSec=step_data.get('timerSec')
        ))
    
    # Recipe
    recipe = Recipe(
        id=str(item['id']),
        name=str(item['name']),
        description=item.get('description'),
        servings=int(item['servings']),
        cookingTime=float(item['cookingTime']),
        category=str(item['category']),
        ingredients=ingredients,
        steps=steps,
        nutrition=nutrition
    )
    
    # 負の数値チェック（任意だが実装）
    if recipe.servings < 0:
        raise ValueError("servings は負の値にできません")
    if recipe.cookingTime < 0:
        raise ValueError("cookingTime は負の値にできません")
    if nutrition.calories < 0:
        raise ValueError("calories は負の値にできません")
    
    return recipe
