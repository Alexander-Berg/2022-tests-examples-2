import pytest

from . import utils


@pytest.mark.parametrize('measure_version', [None, '1', '2'])
async def test_items_info_stub_200(
        taxi_eats_picker_orders,
        create_order,
        mockserver,
        load_json,
        measure_version,
):
    @mockserver.json_handler(
        """/eats-nomenclature/v1/place/products/"""
        """search-by-barcode-or-vendor-code""",
    )
    def _mock_integrations(request):
        assert request.query['place_id'] == '1'
        assert request.json == {
            'items': [
                {'barcode': '987654321098', 'vendor_code': None},
                {'barcode': None, 'vendor_code': None},
            ],
        }
        expected_item = load_json('expected_item.json')
        return {
            'matched_items': [
                {
                    'barcode': '987654321098',
                    'sku': None,
                    'item': expected_item,
                },
            ],
            'not_matched_items': [],
        }

    create_order(eats_id='4321')
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/info',
        json={
            'eats_id': '4321',
            'picker_info_items': [
                {'barcode': '987654321098'},
                {'vendor_code': None},
            ],
        },
        headers=utils.make_headers(None, measure_version),
    )
    assert response.status_code == 200
    expected_response = load_json('expected_response_items_measure_v2.json')
    assert expected_response == response.json()


async def test_items_info_404(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/info',
        json={'eats_id': '111', 'picker_info_items': []},
        headers=utils.da_headers(),
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'order_not_found',
        'message': 'Заказ не найден',
    }


async def test_items_info_401(taxi_eats_picker_orders):
    bad_header = {'X-Request-Application-Version': '9.99 (9999)'}
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/info',
        json={'eats_id': '111', 'picker_info_items': []},
        headers=bad_header,
    )
    assert response.status_code == 401


async def test_items_info_400(taxi_eats_picker_orders):
    response = await taxi_eats_picker_orders.post(
        '/4.0/eats-picker/api/v1/items/info',
        json={'eeeets_id': '111', 'picker_info_items': []},
        headers=utils.da_headers(),
    )
    assert response.status_code == 400
