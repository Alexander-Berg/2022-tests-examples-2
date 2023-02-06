import enum
from typing import List
from typing import Optional

import pytest

from tests_umlaas_eats import experiments


class Source(str, enum.Enum):
    CART = 'cart'
    MENU_ITEM = 'menuitem'


class CartItem(dict):
    def __init__(self, public_id: str, quantity: int = 1):
        dict.__init__(self)
        self['public_id'] = public_id
        self['quantity'] = quantity if quantity > 1 else 1


class Cart(dict):
    def __init__(self, items: List[CartItem] = None):
        dict.__init__(self)
        self['items'] = items or []


@pytest.fixture
def _mock_ordershistory_eats_retail_categories(mockserver, load_json):
    @mockserver.json_handler(
        '/eats-retail-categories/v1/orders-history/products/cross-brand',
    )
    def _mock(request):
        return load_json('ordershistory_mock.json')


@pytest.fixture(name='suggest')
def suggest_endpoint(taxi_umlaas_eats):
    """
    Фикстура обращения к ручке /internal/umlaas-eats/v1/retail/suggest.
    """
    url_path: str = '/internal/umlaas-eats/v1/retail/suggest'

    class Context:
        async def send_request(
                self,
                headers: dict = None,
                request_id: str = 'testsuite',
                items: List[str] = None,
                cart: Optional[Cart] = None,
                source: Source = Source.CART,
                brand_id: int = 1,
                place_id: int = 2,
                user_uid: int = 1184610,
        ):
            request_headers: dict = {}
            if headers:
                request_headers.update(headers)

            request_body: dict = {
                'request_id': request_id,
                'items': items or [],
                'cart': cart or Cart(),
                'source': source,
                'brand_id': brand_id,
                'place_id': place_id,
            }

            if 'X-Eats-User' not in request_headers and user_uid is not None:
                request_headers['X-Eats-User'] = f'user_id={user_uid}'

            response = await taxi_umlaas_eats.post(
                url_path, headers=request_headers, json=request_body,
            )
            return response

    return Context()


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=(experiments.eats_retail_suggest(enabled=False)),
            id='disabled experiment',
        ),
        pytest.param(
            marks=(experiments.eats_retail_suggest(enabled=True)),
            id='enabled experiment',
        ),
    ],
)
@pytest.mark.parametrize(
    'source, items, cart',
    [
        pytest.param(
            Source.CART, None, None, id='cart with no items and cart',
        ),
        pytest.param(
            Source.MENU_ITEM, None, None, id='menuitem with no items and cart',
        ),
    ],
)
async def test_endpoint_liveness(suggest, source, items, cart):
    request_id: str = 'test_request_id'
    response = await suggest.send_request(
        request_id=request_id, items=items, cart=cart, source=source,
    )
    assert response.status_code == 200

    response_body: dict = response.json()
    assert response_body['request_id'] == request_id
    assert not response_body['recommendations']
    assert not response_body['experiments']


@pytest.mark.parametrize(
    'source, items, cart, expected_recommendations',
    [
        pytest.param(
            Source.MENU_ITEM,
            ['1'],
            None,
            ['2', '3'],
            marks=(
                experiments.eats_retail_suggest(
                    enabled=True, min_pair_npmi=0, min_suggest_size=0,
                )
            ),
            id='no min npmi filter',
        ),
        pytest.param(
            Source.MENU_ITEM,
            ['1'],
            None,
            ['2'],
            marks=(
                experiments.eats_retail_suggest(
                    enabled=True, min_pair_npmi=0.2, min_suggest_size=0,
                )
            ),
            id='filter out "3" due to min pair npmi',
        ),
        pytest.param(
            Source.MENU_ITEM,
            ['1'],
            None,
            [],
            marks=(
                experiments.eats_retail_suggest(
                    enabled=True, min_pair_npmi=0, min_suggest_size=3,
                )
            ),
            id='no recommendations due to min_suggest_size',
        ),
        pytest.param(
            Source.MENU_ITEM,
            ['5'],
            Cart(items=[CartItem(public_id='6'), CartItem(public_id='7')]),
            ['9', '8', '20'],  # lexicographical sort
            marks=(
                experiments.eats_retail_suggest(
                    enabled=True,
                    min_pair_npmi=0,
                    min_suggest_size=3,
                    max_suggest_size=3,
                )
            ),
            id='max recommendations size',
        ),
        pytest.param(
            Source.MENU_ITEM,
            ['4'],
            Cart(items=[CartItem(public_id='6'), CartItem(public_id='7')]),
            ['5', 'test123', 'test456'],  # lexicographical sort
            marks=(
                experiments.eats_retail_suggest(
                    enabled=True,
                    min_pair_npmi=0,
                    enable_fallback=True,
                    min_suggest_size=3,
                    max_suggest_size=3,
                )
            ),
            id='with fallback',
        ),
    ],
)
async def test_recommendations(
        suggest,
        source: Source,
        items: List[str],
        cart: Optional[Cart],
        expected_recommendations: List[str],
):
    response = await suggest.send_request(
        items=items, source=source, cart=cart,
    )
    assert response.status_code == 200

    actual_recommendations: List[str] = response.json()['recommendations']
    assert len(expected_recommendations) == len(actual_recommendations)
    for expected, actual in zip(
            expected_recommendations, actual_recommendations,
    ):
        assert expected == actual


@pytest.mark.parametrize(
    'source, items, cart, expected_recommendations',
    [
        pytest.param(
            Source.MENU_ITEM,
            ['6'],
            None,
            ['7', '1', '2'],
            marks=(
                experiments.eats_retail_suggest(
                    enabled=True,
                    min_pair_npmi=0,
                    min_suggest_size=0,
                    enable_category_suggest=True,
                )
            ),
            id='enable category suggest',
        ),
    ],
)
async def test_category_suggest(
        suggest,
        source: Source,
        items: List[str],
        cart: Optional[Cart],
        expected_recommendations: List[str],
        _mock_ordershistory_eats_retail_categories,
):
    response = await suggest.send_request(
        items=items, source=source, cart=cart,
    )
    assert response.status_code == 200

    actual_recommendations: List[str] = response.json()['recommendations']
    assert len(expected_recommendations) == len(actual_recommendations)
    for expected, actual in zip(
            expected_recommendations, actual_recommendations,
    ):
        assert expected == actual


@pytest.mark.eats_catalog_storage_cache(file='eats-places-cache.json')
@pytest.mark.parametrize(
    'source, items, cart, expected_recommendations',
    [
        pytest.param(
            Source.CART,
            [],
            Cart(items=[CartItem(public_id='6'), CartItem(public_id='7')]),
            ['4', '2', '1', '3'],
            marks=(
                experiments.eats_retail_suggest(
                    enabled=True,
                    min_pair_npmi=0,
                    min_suggest_size=0,
                    enable_history=True,
                )
            ),
            id='enable history eats_retail_categories',
        ),
    ],
)
async def test_history_retail_categories(
        suggest,
        source: Source,
        items: List[str],
        cart: Optional[Cart],
        expected_recommendations: List[str],
        _mock_ordershistory_eats_retail_categories,
):
    response = await suggest.send_request(
        items=items, source=source, cart=cart,
    )
    assert response.status_code == 200

    actual_recommendations: List[str] = response.json()['recommendations']
    assert len(expected_recommendations) == len(actual_recommendations)
    for expected, actual in zip(
            expected_recommendations, actual_recommendations,
    ):
        assert expected == actual
