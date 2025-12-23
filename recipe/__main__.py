#!/usr/bin/env python3
"""
レシピ管理システム CLIエントリーポイント
TEST_PLAN.md/仕様書.mdの形式に対応
"""
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import create_parser, cmd_list, cmd_sort, cmd_knapsack

if __name__ == "__main__":
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

