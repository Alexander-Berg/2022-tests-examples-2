import dataclasses
from typing import List
from typing import Optional


class Place:
    """
    Заведение, для которого существуют прото-товары или промо-блюда.
    """

    def __init__(self, place_id: int, brand_id: Optional[int] = None):
        self.place_id = place_id
        self.brand_id = brand_id or place_id


class Product:
    """
    Товар, который хранится в таблице промо-товаров.
    """

    def __init__(
            self,
            product_id: str,
            core_id: Optional[int] = None,
            place: Place = Place(place_id=1),
            suitable_categories: Optional[List[str]] = None,
            non_suitable_categories: Optional[List[str]] = None,
    ):
        self.product_id = product_id
        self.core_id = core_id
        self.place = place
        self.suitable_categories = suitable_categories or []
        self.non_suitable_categories = non_suitable_categories or []


class Dish:
    """
    Блюдо в ресторане, которое хранится в таблице промо-блюд.
    """

    def __init__(self, core_id: int, place: Place = Place(place_id=1)):
        self.core_id = core_id
        self.place = place


@dataclasses.dataclass
class ProductsTable:
    promotion: str
    products: List[Product]


@dataclasses.dataclass
class DishesTable:
    promotion: str
    dishes: List[Dish]
