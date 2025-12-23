"""
レシピ管理システム メイン処理
Part1 + Part2（必須）の実装
"""
import argparse
import json
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.loader import load_recipes
from src.sort import sort_recipes
from src.knapsack import solve_knapsack


def cmd_list(args):
    """recipe list コマンド"""
    recipes = load_recipes(args.data)
    
    # JSON出力（仕様書に従い、Raw値を出力）
    output = []
    for recipe in recipes:
        output.append({
            "id": recipe.id,
            "name": recipe.name,
            "description": recipe.description,
            "servings": recipe.servings,
            "cookingTime": recipe.cookingTime,
            "category": recipe.category,
            "nutrition": {
                "calories": recipe.nutrition.calories,
                "nutrients": recipe.nutrition.nutrients
            }
        })
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_sort(args):
    """recipe sort コマンド"""
    recipes = load_recipes(args.data)
    sorted_recipes = sort_recipes(recipes, args.orderBy, args.order)
    
    # JSON出力（仕様書に従い、Raw値を出力）
    output = []
    for recipe in sorted_recipes:
        output.append({
            "id": recipe.id,
            "name": recipe.name,
            "description": recipe.description,
            "servings": recipe.servings,
            "cookingTime": recipe.cookingTime,
            "category": recipe.category,
            "nutrition": {
                "calories": recipe.nutrition.calories,
                "nutrients": recipe.nutrition.nutrients
            }
        })
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_knapsack(args):
    """recipe knapsack コマンド"""
    recipes = load_recipes(args.data)
    result = solve_knapsack(recipes, args.maxCalories, args.maxCookingTime)
    
    # JSON出力（仕様書6.6に従い、整数値を出力）
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_test_sort(args):
    """開発用: test_sort コマンド（互換性維持）"""
    recipes = load_recipes(args.json_path)
    sorted_recipes = sort_recipes(recipes, args.order_by, args.order)
    
    # JSON出力（仕様書に従い、Raw値を出力）
    output = []
    for recipe in sorted_recipes:
        output.append({
            "id": recipe.id,
            "name": recipe.name,
            "description": recipe.description,
            "servings": recipe.servings,
            "cookingTime": recipe.cookingTime,
            "category": recipe.category,
            "nutrition": {
                "calories": recipe.nutrition.calories,
                "nutrients": recipe.nutrition.nutrients
            }
        })
    
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_test_knapsack(args):
    """開発用: test_knapsack コマンド（互換性維持）"""
    recipes = load_recipes(args.json_path)
    result = solve_knapsack(recipes, args.max_calories, args.max_cooking_time)
    
    # JSON出力（仕様書6.6に従い、整数値を出力）
    print(json.dumps(result, ensure_ascii=False, indent=2))


def create_parser():
    """argparseパーサーを作成"""
    parser = argparse.ArgumentParser(
        prog='recipe',
        description='レシピ管理システム'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='サブコマンド')
    
    # recipe list --data <path>
    parser_list = subparsers.add_parser('list', help='レシピ一覧を表示')
    parser_list.add_argument('--data', required=True, help='JSONファイルのパス')
    parser_list.set_defaults(func=cmd_list)
    
    # recipe sort --data <path> --orderBy <id|name|calories|cookingTime> --order <asc|desc>
    parser_sort = subparsers.add_parser('sort', help='レシピをソート')
    parser_sort.add_argument('--data', required=True, help='JSONファイルのパス')
    parser_sort.add_argument(
        '--orderBy',
        choices=['id', 'name', 'calories', 'cookingTime'],
        required=True,
        help='ソートキー'
    )
    parser_sort.add_argument(
        '--order',
        choices=['asc', 'desc'],
        required=True,
        help='ソート順'
    )
    parser_sort.set_defaults(func=cmd_sort)
    
    # recipe knapsack --data <path> --maxCalories <number> --maxCookingTime <number>
    parser_knapsack = subparsers.add_parser('knapsack', help='ナップサック問題を解く')
    parser_knapsack.add_argument('--data', required=True, help='JSONファイルのパス')
    parser_knapsack.add_argument('--maxCalories', type=float, required=True, help='最大カロリー')
    parser_knapsack.add_argument('--maxCookingTime', type=float, required=True, help='最大調理時間（分）')
    parser_knapsack.set_defaults(func=cmd_knapsack)
    
    # 開発用コマンド（互換性維持）
    parser_test_sort = subparsers.add_parser('test_sort', help='[開発用] ソートテスト')
    parser_test_sort.add_argument('json_path', help='JSONファイルのパス')
    parser_test_sort.add_argument('order_by', help='ソートキー')
    parser_test_sort.add_argument('order', help='ソート順')
    parser_test_sort.set_defaults(func=cmd_test_sort)
    
    parser_test_knapsack = subparsers.add_parser('test_knapsack', help='[開発用] ナップサックテスト')
    parser_test_knapsack.add_argument('json_path', help='JSONファイルのパス')
    parser_test_knapsack.add_argument('max_calories', type=float, help='最大カロリー')
    parser_test_knapsack.add_argument('max_cooking_time', type=float, help='最大調理時間（分）')
    parser_test_knapsack.set_defaults(func=cmd_test_knapsack)
    
    return parser


def main():
    """メイン処理"""
    # 既存のtest_sort/test_knapsackコマンド形式（位置引数）との互換性を維持
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'test_sort':
            if len(sys.argv) != 5:
                print("Usage: python main.py test_sort <json_path> <orderBy> <order>", file=sys.stderr)
                sys.exit(1)
            args = argparse.Namespace(
                json_path=sys.argv[2],
                order_by=sys.argv[3],
                order=sys.argv[4]
            )
            cmd_test_sort(args)
            return
        elif sys.argv[1] == 'test_knapsack':
            if len(sys.argv) != 5:
                print("Usage: python main.py test_knapsack <json_path> <maxCalories> <maxCookingTime>", file=sys.stderr)
                sys.exit(1)
            args = argparse.Namespace(
                json_path=sys.argv[2],
                max_calories=float(sys.argv[3]),
                max_cooking_time=float(sys.argv[4])
            )
            cmd_test_knapsack(args)
            return
    
    # 新しいCLI形式（argparse）
    parser = create_parser()
    
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # argparseのエラーをexit code 1に統一（仕様書8.1: エラー時は1）
        if e.code != 0:
            sys.exit(1)
        raise
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except SystemExit:
        # load_recipes等でsys.exit(1)が呼ばれた場合はそのまま
        raise
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
