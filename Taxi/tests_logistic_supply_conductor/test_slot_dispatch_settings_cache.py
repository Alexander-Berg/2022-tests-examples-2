import pytest


POLYGON = [
    [54.0, 62.0],
    [54.0, 64.0],
    [52.0, 64.0],
    [52.0, 62.0],
    [54.0, 62.0],
]


def check_optional(actual, expected, field_name):
    if field_name in actual or field_name in expected:
        assert actual[field_name] == expected[field_name]


def check_response(actual_response, expected_response):
    assert len(actual_response) == len(expected_response)
    for actual, expected in zip(actual_response, expected_response):
        assert actual['slot_id'] == expected['slot_id']
        assert actual['data'].keys() == expected['data'].keys()
        assert actual['data']['version'] == expected['data']['version']
        assert actual['data']['polygon'] == expected['data']['polygon']
        check_optional(actual['data'], expected['data'], 'employer_names')
        check_optional(actual['data'], expected['data'], 'order_sources')
        check_optional(actual['data'], expected['data'], 'dispatch_priority')


@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions_with_order_source.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
    ],
)
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param([]),
        pytest.param(
            [
                {
                    'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                    'data': {
                        'polygon': POLYGON,
                        'version': 2,
                        'order_sources': ['C2C'],
                        'dispatch_priority': 120,
                    },
                },
                {
                    'slot_id': 'a278134c-49f2-48bc-b9b6-941c76650508',
                    'data': {
                        'polygon': POLYGON,
                        'version': 2,
                        'order_sources': ['C2C'],
                        'dispatch_priority': 120,
                    },
                },
                {
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                    'data': {
                        'polygon': POLYGON,
                        'version': 2,
                        'order_sources': ['C2C'],
                        'dispatch_priority': 120,
                    },
                },
                {
                    'slot_id': '57079d82-fabd-4e70-9961-09a4733bbc57',
                    'data': {
                        'polygon': POLYGON,
                        'version': 1,
                        'employer_names': ['grocery'],
                    },
                },
                {
                    'slot_id': 'a4e20684-fd40-490c-b6ac-faf0ee074b89',
                    'data': {
                        'polygon': POLYGON,
                        'version': 1,
                        'employer_names': ['vkusvill'],
                        'dispatch_priority': 60,
                    },
                },
            ],
            marks=pytest.mark.pgsql(
                'logistic_supply_conductor', files=['pg_workshift_slots.sql'],
            ),
        ),
    ],
)
async def test_slot_dispatch_settings_update(
        taxi_logistic_supply_conductor, expected_response,
):
    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/caches/slot-dispatch-settings/updates',
        params={'consumer': 'test'},
        json={},
    )
    assert response.status_code == 200

    actual_response = response.json()['slot_dispatch_settings']
    check_response(actual_response, expected_response)


@pytest.mark.parametrize(
    'request_ids, expected_response',
    [
        (
            [
                '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                'a4e20684-fd40-490c-b6ac-faf0ee074b89',
            ],
            [
                {
                    'slot_id': '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
                    'data': {
                        'polygon': POLYGON,
                        'version': 2,
                        'order_sources': ['C2C'],
                        'dispatch_priority': 120,
                    },
                },
                {
                    'slot_id': 'a4e20684-fd40-490c-b6ac-faf0ee074b89',
                    'data': {
                        'polygon': POLYGON,
                        'version': 1,
                        'employer_names': ['vkusvill'],
                        'dispatch_priority': 60,
                    },
                },
            ],
        ),
        (
            ['76a3176e-f759-44bc-8fc7-43ea091bd68b'],
            [
                {
                    'slot_id': '76a3176e-f759-44bc-8fc7-43ea091bd68b',
                    'data': {
                        'polygon': POLYGON,
                        'version': 2,
                        'order_sources': ['C2C'],
                        'dispatch_priority': 120,
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'logistic_supply_conductor',
    files=[
        'pg_workshift_rules.sql',
        'pg_workshift_metadata_with_requirements.sql',
        'pg_workshift_rule_versions_with_order_source.sql',
        'pg_geoareas_small.sql',
        'pg_workshift_quotas.sql',
        'pg_workshift_slots.sql',
    ],
)
async def test_slot_dispatch_settings_retrieve(
        taxi_logistic_supply_conductor, request_ids, expected_response,
):
    response = await taxi_logistic_supply_conductor.post(
        'internal/v1/caches/slot-dispatch-settings/retrieve',
        params={'consumer': 'test'},
        json={'id_in_set': request_ids},
    )
    assert response.status_code == 200

    actual_response = response.json()['slot_dispatch_settings']
    check_response(actual_response, expected_response)
