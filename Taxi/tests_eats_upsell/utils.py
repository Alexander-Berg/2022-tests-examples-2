import enum


def build_core_item(item_id: int, name: str = None, available: bool = True):
    """
    Собирает позицию меню ресторана.
    """

    if not name:
        name = 'name {}'.format(item_id)

    return {
        'id': item_id,
        'name': name,
        'description': 'description {}'.format(item_id),
        'available': available,
        'inStock': None,
        'price': 10,
        'decimalPrice': '10',
        'promoPrice': None,
        'decimalPromoPrice': None,
        'optionsGroups': [],
        'picture': None,
        'weight': '100кг',
        'promoTypes': [],
        'adult': False,
        'shippingType': 'all',
    }


class Business(str, enum.Enum):
    Restaurant = ('restaurant',)
    Shop = ('shop',)
    Store = 'store'
