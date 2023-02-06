import pytest

from . import conftest


@pytest.fixture(name='v1_tariffs_list')
async def _v1_tariffs_list(taxi_cargo_tariffs):
    class Client:
        url = '/cargo-tariffs/admin/v1/tariffs/list'
        params = {'service': 'ndd_client'}
        filters = []

        async def list(self):
            return await taxi_cargo_tariffs.post(
                self.url, params=self.params, json={'filters': self.filters},
            )

    return Client()


async def test_empty_filters(v1_tariffs_list, fill_db):
    tariff_id, _ = await fill_db()
    resp = await v1_tariffs_list.list()
    assert resp.status_code == 200
    assert resp.json() == {
        'filters': [
            {
                'choices': [{'text': 'corp_id_1', 'value': 'corp_id_1'}],
                'field_name': 'employer_id',
                'text': 'employer_id',
            },
        ],
        'tariff_list': [
            {'conditions': ['employer_id = corp_id_1'], 'id': tariff_id},
        ],
    }


async def test_one_filter(v1_tariffs_list):
    v1_tariffs_list.filters = [
        {'field_name': 'employer_id', 'value': 'corp_id_1'},
    ]
    resp = await v1_tariffs_list.list()
    assert resp.status_code == 200
    assert 'chosen_value' in resp.json()['filters'][0]


async def test_empty_tariff_list(v1_tariffs_list):
    v1_tariffs_list.filters = [{'field_name': 'employer_id', 'value': 'aliia'}]
    resp = await v1_tariffs_list.list()
    assert resp.status_code == 200
    assert not resp.json()['tariff_list']


async def test_bad_characters(v1_tariffs_list):
    v1_tariffs_list.filters = [
        {'field_name': 'value\' and sign = \'', 'value': 'aliia'},
    ]
    resp = await v1_tariffs_list.list()
    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'validation_error',
        'message': 'Невалидный символ: \'',
    }


@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER=conftest.default_conditions_order_config(),
)
async def test_conditions_with_number(
        add_tariffs, tariff_json_example, v1_tariffs_list, fill_db,
):
    await fill_db()
    await add_tariffs(tariff_json_example)

    v1_tariffs_list.filters = [
        {'field_name': 'source_zone', 'value': 'Moscow_CKAD'},
        {'field_name': 'destination_zone', 'value': 'Moscow_CKAD'},
    ]
    resp = await v1_tariffs_list.list()
    assert resp.status_code == 200
    assert resp.json()['filters'] == [
        {
            'choices': [
                {
                    'text': '0123456789012345678901234567890a',
                    'value': '0123456789012345678901234567890a',
                },
                {'text': 'corp_id_1', 'value': 'corp_id_1'},
            ],
            'field_name': 'employer_id',
            'text': 'employer_id',
        },
        {
            'choices': [{'text': 'Moscow_CKAD', 'value': 'Moscow_CKAD'}],
            'chosen_value': {'text': 'Moscow_CKAD', 'value': 'Moscow_CKAD'},
            'field_name': 'source_zone',
            'text': 'source_zone',
        },
        {
            'choices': [
                {'text': 'Moscow_CKAD', 'value': 'Moscow_CKAD'},
                {'text': 'SPB_KAD', 'value': 'SPB_KAD'},
            ],
            'chosen_value': {'text': 'Moscow_CKAD', 'value': 'Moscow_CKAD'},
            'field_name': 'destination_zone',
            'text': 'destination_zone',
        },
        {
            'choices': [
                {'text': 'interval_strict', 'value': 'interval_strict'},
                {'text': 'interval_with_fees', 'value': 'interval_with_fees'},
            ],
            'field_name': 'tariff_category',
            'text': 'tariff_category',
        },
    ]
    assert len(resp.json()['tariff_list']) == 2
