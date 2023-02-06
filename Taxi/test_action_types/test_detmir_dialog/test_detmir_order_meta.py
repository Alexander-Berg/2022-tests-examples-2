# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.detmir_dialog import get_order_meta

DATA = {
    'order': {
        'code': '5970804885',
        'delivery_number': '2066320516',
        'type': 'web',
        'creationTime': '2021-08-22T13:36:49.000Z',
        'bonus': 7.4,
        'status': 'ready_to_packing',
        'secondaryStatus': None,
        'unknown_payment_status': True,
        'surveys': [],
        'payments': [
            {
                'method': 'cash',
                'status': 'unknown',
                'currency': 'RUB',
                'qr': None,
                'sum': 374.5,
                'provider': None,
            },
        ],
        'deliveryDateRequested': '2021-08-27',
        'deliveryDateCalculated': '2021-08-27',
        'shippingDate': '2021-08-26',
        'assembly_time': '',
        'delivery': {
            'method': 'pickup_store',
            'transport_company': {'name': 'курьерист'},
            'interval': {'from': '9', 'to': '20'},
            'zone': {
                'name': 'UPD_МО Зона 2 (30-50 км от МКАД)',
                'tariff': 'МО Зона 3 (2000;500/250;2000;150;0/399/499;3)',
            },
            'pointOfService': {
                'id': '2250',
                'code': '2218',
                'title': 'Наро-Фоминск, ТЦ «Воскресенский»',
                'description': '',
                'city': 'Наро-Фоминск',
                'city_code': '50000052000',
                'address': {'address': 'Наро-Фоминск, площадь Свободы, 2'},
                'lat': 55.387942,
                'long': 36.735565,
                'region': 'RU-MOS',
                'metro': [],
                'working_hours': 'Ежедневно с 10:00 до 22:00',
                'guide': '',
                'payment_methods': [
                    {'type': 'card', 'threshold': None},
                    {'type': 'cash', 'threshold': None},
                    {'type': 'loyalty', 'threshold': None},
                ],
                'offline_payment_methods': [
                    {'type': 'card', 'threshold': None},
                    {'type': 'cash', 'threshold': None},
                    {'type': 'loyalty', 'threshold': None},
                ],
                'pickup_available': None,
                'express_delivery': True,
                'instore': True,
                'timezone_offset': 3,
                'collection_time': None,
                'storage_period': 5,
                'time_open': {'hours': 10, 'minutes': 0},
                'time_close': {'hours': 22, 'minutes': 0},
                'type': 'store',
                'subtype': 'DM',
                'is_store_pos': False,
                'partial_checkout_available': False,
                'fitting_available': False,
                'return_available': False,
                'is_active': True,
                'assembly_slots': None,
            },
            'pickup_area': {'sector': ''},
        },
        'costs': {
            'discount': {
                'value': 1160.5,
                'bonus': 0,
                'promo': 1160.5,
                'currency': 'RUB',
            },
            'donation': {'value': 0, 'currency': 'RUB'},
            'subtotal': {'value': 374.5, 'currency': 'RUB'},
            'delivery': {'value': 0, 'currency': 'RUB'},
            'total': {'value': 374.5, 'currency': 'RUB'},
            'partial': {'value': 1535, 'currency': 'RUB'},
        },
        'entries': [
            {
                'index': 1,
                'count': 1,
                'collectedCount': 1,
                'product': {
                    'id': '2829831',
                    'code': '1000042802',
                    'productId': '2829831',
                    'bar_codes': [],
                    'type': 'product',
                    'parent_id': None,
                    'article': '',
                    'title': 'Мягкая игрушка Aurora Кролик 20 см 161414A',
                    'description': '',
                    'price': {'price': 699, 'currency': 'RUB'},
                    'old_price': None,
                    'pledge_price': None,
                    'box': None,
                    'promoted': False,
                    'max_order_quantity': None,
                    'sex': ['male', 'female'],
                    'bonus': 0,
                    'rating': 0,
                    'review_count': 0,
                    'pictures': [
                        {
                            'title': '',
                            'original': 'https://static.detmir.st/media_out/831/829/2829831/1500/0.jpg?1615604413896',
                            'web': 'https://static.detmir.st/media_out/831/829/2829831/450/0.jpg?1615604413896',
                            'thumbnail': 'https://static.detmir.st/media_out/831/829/2829831/150/0.jpg?1615604413896',
                        },
                    ],
                    'labels': [],
                    'brands': [],
                    'collections': [],
                    'details': None,
                    'categories': [],
                    'sap_categories': [],
                    'sap_brands': [],
                    'sap_collections': [],
                    'certificates': [],
                    'color': '',
                    'country_id': '0',
                    'country': '',
                    'material': '',
                    'dynamic': {},
                    'variants': [],
                    'videos': [],
                    'documents': [],
                    'link': {
                        'rel': 'product',
                        'href': '/product/index/id/2829831/',
                        'id': '2829831',
                        'web_url': (
                            'https://www.detmir.ru/product/index/id/2829831/'
                        ),
                    },
                    'available': {
                        'online': {'warehouse_codes': []},
                        'offline': {'region_iso_codes': [], 'stores': []},
                    },
                    'delivery': {'restricted': []},
                    'site': '',
                    'promo': False,
                    'signs': [],
                    'creation_date': None,
                    'update_date': None,
                    'published': None,
                    'publication_date': None,
                    'draft_status': '',
                    'vendor_id': '',
                    'vendor': {
                        'id': '',
                        'code': '',
                        'name': '',
                        'description': '',
                        'usersIds': [],
                        'inn': '',
                        'ogrn': '',
                        'phone': '',
                        'address': '',
                    },
                    'year': '',
                    'season': '',
                    'subseason': '',
                    'ages': {},
                    'lining_material': '',
                    'outer_material': '',
                    'stock': 0,
                    'vat': None,
                    'receipt_title': '',
                    'composition': '',
                    'sale_start': '',
                    'sale_end': '',
                    'weight': None,
                    'width': None,
                    'height': None,
                    'length': None,
                    'approval_date': '',
                    'sizetable': [],
                    'size_title': '',
                    'manufacturer_size': '',
                    'linear_size': '',
                    'assets': [],
                },
            },
            {
                'index': 2,
                'count': 1,
                'collectedCount': 1,
                'product': {
                    'id': '3600708',
                    'code': '2104859005',
                    'productId': '3600708',
                    'bar_codes': [],
                    'type': 'product',
                    'parent_id': '3600703',
                    'article': '',
                    'title': 'Комбинезон КотМарКот 86',
                    'description': '',
                    'price': {'price': 642, 'currency': 'RUB'},
                    'old_price': None,
                    'pledge_price': None,
                    'box': None,
                    'promoted': False,
                    'max_order_quantity': None,
                    'sex': ['male', 'female'],
                    'bonus': 0,
                    'rating': 0,
                    'review_count': 0,
                    'pictures': [
                        {
                            'title': '',
                            'original': 'https://static.detmir.st/media_out/703/600/3600703/1500/0.jpg?1622100494150',
                            'web': 'https://static.detmir.st/media_out/703/600/3600703/450/0.jpg?1622100494150',
                            'thumbnail': 'https://static.detmir.st/media_out/703/600/3600703/150/0.jpg?1622100494150',
                        },
                    ],
                    'labels': [],
                    'brands': [],
                    'collections': [],
                    'details': None,
                    'categories': [],
                    'sap_categories': [],
                    'sap_brands': [],
                    'sap_collections': [],
                    'certificates': [],
                    'color': '',
                    'country_id': '0',
                    'country': '',
                    'material': '',
                    'dynamic': {},
                    'variants': [],
                    'videos': [],
                    'documents': [],
                    'link': {
                        'rel': 'product',
                        'href': '/product/index/id/3600708/',
                        'id': '3600708',
                        'web_url': (
                            'https://www.detmir.ru/product/index/id/3600708/'
                        ),
                    },
                    'available': {
                        'online': {'warehouse_codes': []},
                        'offline': {'region_iso_codes': [], 'stores': []},
                    },
                    'delivery': {'restricted': []},
                    'site': '',
                    'promo': False,
                    'signs': [],
                    'creation_date': None,
                    'update_date': None,
                    'published': None,
                    'publication_date': None,
                    'draft_status': '',
                    'vendor_id': '',
                    'vendor': {
                        'id': '',
                        'code': '',
                        'name': '',
                        'description': '',
                        'usersIds': [],
                        'inn': '',
                        'ogrn': '',
                        'phone': '',
                        'address': '',
                    },
                    'year': '',
                    'season': '',
                    'subseason': '',
                    'ages': {},
                    'lining_material': '',
                    'outer_material': '',
                    'stock': 0,
                    'vat': None,
                    'receipt_title': '',
                    'composition': '',
                    'sale_start': '',
                    'sale_end': '',
                    'weight': None,
                    'width': None,
                    'height': None,
                    'length': None,
                    'approval_date': '',
                    'sizetable': [],
                    'size_title': '',
                    'manufacturer_size': '',
                    'linear_size': '',
                    'assets': [],
                },
            },
            {
                'index': 3,
                'count': 1,
                'collectedCount': 1,
                'product': {
                    'id': '2872161',
                    'code': '1000043795',
                    'productId': '2872161',
                    'bar_codes': [],
                    'type': 'product',
                    'parent_id': None,
                    'article': '',
                    'title': 'Чудо-домик Азбукварик Тук-тук',
                    'description': '',
                    'price': {'price': 194, 'currency': 'RUB'},
                    'old_price': None,
                    'pledge_price': None,
                    'box': None,
                    'promoted': False,
                    'max_order_quantity': None,
                    'sex': ['male', 'female'],
                    'bonus': 0,
                    'rating': 0,
                    'review_count': 0,
                    'pictures': [
                        {
                            'title': '',
                            'original': 'https://static.detmir.st/media_out/161/872/2872161/1500/0.jpg',
                            'web': 'https://static.detmir.st/media_out/161/872/2872161/450/0.jpg',
                            'thumbnail': 'https://static.detmir.st/media_out/161/872/2872161/150/0.jpg',
                        },
                    ],
                    'labels': [],
                    'brands': [],
                    'collections': [],
                    'details': None,
                    'categories': [],
                    'sap_categories': [],
                    'sap_brands': [],
                    'sap_collections': [],
                    'certificates': [],
                    'color': '',
                    'country_id': '0',
                    'country': '',
                    'material': '',
                    'dynamic': {},
                    'variants': [],
                    'videos': [],
                    'documents': [],
                    'link': {
                        'rel': 'product',
                        'href': '/product/index/id/2872161/',
                        'id': '2872161',
                        'web_url': (
                            'https://www.detmir.ru/product/index/id/2872161/'
                        ),
                    },
                    'available': {
                        'online': {'warehouse_codes': []},
                        'offline': {'region_iso_codes': [], 'stores': []},
                    },
                    'delivery': {'restricted': []},
                    'site': '',
                    'promo': False,
                    'signs': [],
                    'creation_date': None,
                    'update_date': None,
                    'published': None,
                    'publication_date': None,
                    'draft_status': '',
                    'vendor_id': '',
                    'vendor': {
                        'id': '',
                        'code': '',
                        'name': '',
                        'description': '',
                        'usersIds': [],
                        'inn': '',
                        'ogrn': '',
                        'phone': '',
                        'address': '',
                    },
                    'year': '',
                    'season': '',
                    'subseason': '',
                    'ages': {},
                    'lining_material': '',
                    'outer_material': '',
                    'stock': 0,
                    'vat': None,
                    'receipt_title': '',
                    'composition': '',
                    'sale_start': '',
                    'sale_end': '',
                    'weight': None,
                    'width': None,
                    'height': None,
                    'length': None,
                    'approval_date': '',
                    'sizetable': [],
                    'size_title': '',
                    'manufacturer_size': '',
                    'linear_size': '',
                    'assets': [],
                },
            },
        ],
        'customerCancellationDate': '',
        'customerConfirmationDate': '',
        'prolongation': {'count': 0, 'max_count': 3, 'actual': False},
        'cancel_message': {'type': 'special_pickup', 'paid_notify': False},
        'verification_code': None,
    },
}


@pytest.fixture(name='mock_order_meta', autouse=True)
def _mock_order_meta(mockserver):
    @mockserver.json_handler('/detmir-orders/v2/orders/.*', regex=True)
    def _(req):
        return mockserver.make_response(json=DATA)


@pytest.mark.parametrize(
    '_call_param',
    [
        [],
        [param_module.ActionParam({'response_mapping': []})],
        pytest.param(
            [
                param_module.ActionParam(
                    {'response_mapping': [{'key': 'value'}]},
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_detmir_order_meta_validation(_call_param):
    _ = get_order_meta.OrderMetaAction('test', 'test_detmir', '0', _call_param)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'XXX-XXXX'}],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'track_number', 'value': 'some'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_detmir_order_meta_state_validation(state, _call_param):
    action = get_order_meta.OrderMetaAction(
        'test', 'test_detmir', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.pgsql('supportai_actions', files=['sample.sql'])
@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'XXX-XXXX'}],
                ),
            ),
            [],
        ),
    ],
)
@pytest.mark.russian_post_mock(records=[{'oper_type': 'Test'}])
async def test_detmir_order_meta_call(web_context, state, _call_param):
    action = get_order_meta.OrderMetaAction(
        'detmir_dialog', 'geo_stores2ids_dm', '1', _call_param,
    )

    _state = await action(web_context, state)

    assert 'order_status' in _state.features
    assert 'is_late' in _state.features
