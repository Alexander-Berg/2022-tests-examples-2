import pytest


@pytest.mark.config(
    CURRENCY_FORMATTING_RULES={
        '__default__': {'__default__': 0},
        'RUB': {'__default__': 2, 'iso4217': 2},
    },
)
@pytest.mark.parametrize(
    'order_id, expected_code, expected_response',
    [
        ('00000000000000000000000000000001', 404, 'expected_response_1.json'),
        ('00000000000000000000000000000002', 200, 'expected_response_2.json'),
        ('00000000000000000000000000000003', 200, 'expected_response_3.json'),
        ('00000000000000000000000000000004', 200, 'expected_response_4.json'),
        ('00000000000000000000000000000005', 200, 'expected_response_5.json'),
        ('00000000000000000000000000000006', 200, 'expected_response_6.json'),
    ],
    ids=[
        'unexistent_order',
        'regular_order',
        'paid_supply_order',
        'modification_not_in_cache',
        'no_fixed_price',
        'finished_order',
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v1_order_calc_fastdata(
        taxi_pricing_admin,
        order_id,
        expected_code,
        expected_response,
        load_json,
        order_archive_mock,
):
    order_archive_mock.set_order_proc(load_json('db_order_proc.json'))

    expected_json = load_json(expected_response)

    response = await taxi_pricing_admin.get(
        'v1/order-calc/fastdata', params={'order_id': order_id},
    )
    assert response.status_code == expected_code
    assert response.json() == expected_json


@pytest.mark.parametrize(
    'is_anonymized', [False, True], ids=['not_anonymized', 'anonymized'],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v1_order_calc_fastdata_anonymized_order(
        taxi_pricing_admin,
        is_anonymized,
        load_json,
        order_archive_mock,
        testpoint,
):
    @testpoint('anonymize_response')
    def _anonymize_response(data):
        pass

    order_proc = load_json('db_order_proc.json')
    order_id = '00000000000000000000000000000006'

    order_doc = next(doc for doc in order_proc if doc['_id'] == order_id)
    if is_anonymized:
        order_doc.update({'takeout': {'status': 'anonymized'}})

    order_archive_mock.set_order_proc(order_proc)

    response = await taxi_pricing_admin.get(
        'v1/order-calc/fastdata', params={'order_id': order_id},
    )
    assert response.status_code == 200
    assert _anonymize_response.has_calls == is_anonymized
