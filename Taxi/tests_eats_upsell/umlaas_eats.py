import datetime
from typing import List
from typing import Optional

PlaceID = int
BrandID = int


class SuggestItem(dict):
    def __init__(self, uuid: str, group_id: Optional[str] = None):
        dict.__init__(self)
        self['uuid'] = uuid
        self['group_id'] = group_id or uuid


class RequestItem(dict):
    def __init__(self, uuid: str):
        dict.__init__(self)
        self['uuid'] = uuid


class RequestCartItem(dict):
    def __init__(self, uuid: str, quantity: int = 1):
        dict.__init__(self)
        self['item'] = RequestItem(uuid)
        self['quantity'] = quantity


class SuggestContext(dict):
    def __init__(
            self,
            items: Optional[List[RequestItem]] = None,
            cart_items: Optional[List[RequestCartItem]] = None,
            cart_sum: float = 0,
    ):
        assert not (
            not items and not cart_items
        ), 'both items and cart items can\'t be none'

        dict.__init__(self)
        self['items'] = items or []
        self['cart'] = cart_items or []
        self['cart_sum'] = cart_sum


class SuggestRequest(dict):
    def __init__(
            self,
            context: SuggestContext,
            place_id: PlaceID = 1,
            brand_id: BrandID = 1,
            predicting_at: datetime.datetime = datetime.datetime.now(),
    ):
        dict.__init__(self)
        self['place_id'] = place_id
        self['brand_id'] = brand_id
        self['context'] = context
        self['predicting_at'] = predicting_at.isoformat()
