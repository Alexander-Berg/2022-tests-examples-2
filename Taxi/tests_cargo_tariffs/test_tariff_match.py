import pytest

from . import conftest


@pytest.fixture(name='v1_tariffs_match')
async def _v1_tariffs_match(taxi_cargo_tariffs):
    class Client:
        url = '/api/b2b/cargo-tariffs/v1/tariffs/match'
        params = {'service': 'ndd_client'}
        filters = []
        headers = {'X-B2B-Client-Id': '0123456789012345678901234567890a'}

        async def match(self):
            return await taxi_cargo_tariffs.post(
                self.url,
                params=self.params,
                json={'filters': self.filters},
                headers=self.headers,
            )

    return Client()


@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER={
        'ndd_client': [
            {
                'condition_group_name': 'client',
                'fields': [{'name': 'employer_id'}],
            },
        ],
    },
)
async def test_not_found(v1_tariffs_match):
    resp = await v1_tariffs_match.match()
    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'bad_request',
        'message': 'Не существует тарифов с заданными условиями',
    }


def choose_next_filter(filters):
    for filter_ in filters:
        if filter_['choices']:
            return {
                'field_name': filter_['field_name'],
                'value': filter_['choices'][0]['value'],
            }
    return None


@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER=conftest.default_conditions_order_config(),
)
async def test_happy_path(
        add_tariffs, tariff_json_example, v1_tariffs_match, taxi_cargo_tariffs,
):
    await add_tariffs(tariff_json_example)
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)

    resp = await v1_tariffs_match.match()
    assert resp.status_code == 200
    iteratios = len(resp.json()['filters'])
    for _ in range(iteratios):
        next_filter = choose_next_filter(resp.json()['filters'])
        v1_tariffs_match.filters.append(next_filter)
        resp = await v1_tariffs_match.match()
        assert resp.status_code == 200

    assert len(resp.json()['filters']) == iteratios
    assert 'doc' in resp.json()
    assert 'next_filters' not in resp.json()


@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER=conftest.default_conditions_order_config(),
)
async def test_empty_filters(
        add_tariffs,
        tariff_json_example,
        v1_tariffs_match,
        taxi_cargo_tariffs,
        fill_db,
):
    await fill_db()
    await add_tariffs(tariff_json_example)
    await taxi_cargo_tariffs.invalidate_caches(clean_update=True)

    resp = await v1_tariffs_match.match()
    assert resp.status_code == 200
    assert len(resp.json()['filters']) == 3
    assert resp.json()['filters'][0] == {
        'choices': [{'text': 'Moscow_CKAD', 'value': 'Moscow_CKAD'}],
        'field_name': 'source_zone',
        'text': 'source_zone',
    }


@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER=conftest.default_conditions_order_config(),
)
async def test_one_filter(tariff_json_example, add_tariffs, v1_tariffs_match):
    await add_tariffs(tariffs=tariff_json_example)

    v1_tariffs_match.filters = [
        {'field_name': 'source_zone', 'value': 'Moscow_CKAD'},
    ]
    resp = await v1_tariffs_match.match()
    assert resp.status_code == 200
    assert resp.json()['filters'][0] == {
        'chosen_value': {'text': 'Moscow_CKAD', 'value': 'Moscow_CKAD'},
        'field_name': 'source_zone',
        'text': 'source_zone',
        'choices': [],
    }
    for filter_ in resp.json()['filters'][1:]:
        assert 'chosen_value' not in filter_
        assert filter_['choices']


@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_ORDER=conftest.default_conditions_order_config(),
)
async def test_all_filters_are_set(
        add_tariffs, v1_tariffs_match, tariff_json_example,
):
    await add_tariffs(tariffs=tariff_json_example)

    v1_tariffs_match.filters = [
        {'field_name': 'source_zone', 'value': 'Moscow_CKAD'},
        {'field_name': 'destination_zone', 'value': 'Moscow_CKAD'},
        {'field_name': 'tariff_category', 'value': 'interval_with_fees'},
    ]

    resp = await v1_tariffs_match.match()
    assert resp.status_code == 200
    assert 'doc' in resp.json()
    for filter_ in resp.json()['filters']:
        assert 'chosen_value' in filter_
        assert not filter_['choices']
