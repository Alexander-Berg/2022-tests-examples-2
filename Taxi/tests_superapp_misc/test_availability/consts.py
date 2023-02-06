import pytest

URL = 'v1/availability'
DEFAULT_POSITION: list = [37.590533, 55.733863]
INVALID_POSITION: list = [35, 55]
ADDITIONAL_POSITION: list = [31.126322, 58.071481]
ZEROED_POSITION: list = [0, 0]

EMPTY_RESPONSE: dict = {
    'modes': [],
    'products': [],
    'typed_experiments': {'items': [], 'version': -1},
}

SUPERAPP_AVAILABILITY_EXP = 'superapp_availability'

DEFAULT_YANDEX_UID = 'uid'
DEFAULT_PHONE_ID = '88005353535'
DEFAULT_USER_ID = 'user_id'

EDA_STORAGE_AVAILBILITY = (
    '/eats-catalog-storage/internal/eats-catalog-storage'
    '/v1/service/availability'
)

USE_CATLOG_STORAGE = pytest.mark.experiments3(
    is_config=True,
    name='superapp_recieve_eats_availability_from_catalog_storage',
    consumers=['superapp-misc/availability'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
