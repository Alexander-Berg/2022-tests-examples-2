import typing


def create_response(
        valid: bool,
        valid_any: bool,
        error_code: str = None,
        error_description: str = None,
):
    resp = {
        'valid': valid,
        'valid_any': valid_any,
        'descriptions': [],
        'details': [],
    }
    if error_code is not None:
        resp['error_code'] = error_code
    if error_description is not None:
        resp['error_description'] = error_description
    return resp


class StatsCounter:
    counter: int = 0
    brand_id: typing.Optional[str] = None
    business: str = 'restaurant'

    def __init__(self, cnt, brand_id=None, business=None):
        self.counter = cnt
        self.brand_id = brand_id
        if business:
            self.business = business
