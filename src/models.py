"""
レシピ管理システムのデータモデル定義
"""
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Amount:
    """材料の量"""
    raw: str
    value: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class Ingredient:
    """材料"""
    name: str
    amount: Amount


@dataclass
class Step:
    """調理手順"""
    order: int
    text: str
    timerSec: Optional[int] = None


@dataclass
class Nutrition:
    """栄養情報"""
    calories: float  # Raw値（小数可）
    nutrients: Dict[str, float]  # proteinなど

    def get_protein(self) -> float:
        """タンパク質を取得（欠落時は0）"""
        return self.nutrients.get("protein", 0.0)


@dataclass
class Recipe:
    """レシピ"""
    id: str
    name: str
    description: Optional[str] = None
    servings: int = 0
    cookingTime: float = 0.0  # Raw値（分、小数可）
    category: str = ""
    ingredients: List[Ingredient] = None
    steps: List[Step] = None
    nutrition: Optional[Nutrition] = None

    def __post_init__(self):
        if self.ingredients is None:
            self.ingredients = []
        if self.steps is None:
            self.steps = []
