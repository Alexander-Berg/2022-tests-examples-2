import pytest

from tests_fleet_parks import utils


ENDPOINT_BY_LABEL = '/internal/v1/dispatch-requirements/retrieve-by-label'
ENDPOINT_BY_PARK = '/internal/v1/dispatch-requirements/retrieve-by-park'


HEADERS = {
    'X-Ya-Service-Ticket': utils.SERVICE_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Ya-User-Ticket': utils.SERVICE_TICKET,
}


@pytest.mark.parametrize(
    'query, response_code, service_response',
    [
        (
            {'label_id': 'park_valid1'},
            200,
            {
                'dispatch_requirement': 'only_source_park',
                'label_id': 'park_valid1',
                'park_id': 'park_valid1',
            },
        ),
        (
            {'label_id': 'park_valid2'},
            200,
            {
                'dispatch_requirement': 'source_park_and_all',
                'label_id': 'park_valid2',
                'park_id': 'park_valid2',
            },
        ),
        (
            {'label_id': 'park_valid5'},
            500,
            {'code': '500', 'message': 'Internal Server Error'},
        ),
        (
            {'label_id': 'park_valid4'},
            400,
            {
                'code': 'NOT_SAAS_PARK',
                'message': 'Not a saas park, park_id: park_valid4',
            },
        ),
        (
            {'label_id': 'absent'},
            400,
            {
                'code': 'PARK_NOT_FOUND',
                'message': 'No park found for park_id absent',
            },
        ),
    ],
)
async def test_retrieve_by_label(
        taxi_fleet_parks, query, response_code, service_response,
):
    response = await taxi_fleet_parks.post(
        ENDPOINT_BY_LABEL, json=query, headers=HEADERS,
    )

    assert response.status_code == response_code
    assert response.json() == service_response


@pytest.mark.parametrize(
    'query, response_code, service_response',
    [
        (
            {'park_id': 'park_valid1'},
            200,
            {
                'dispatch_requirement': 'only_source_park',
                'label_id': 'park_valid1',
                'park_id': 'park_valid1',
            },
        ),
        (
            {'park_id': 'park_valid2'},
            200,
            {
                'dispatch_requirement': 'source_park_and_all',
                'label_id': 'park_valid2',
                'park_id': 'park_valid2',
            },
        ),
        (
            {'park_id': 'park_valid5'},
            500,
            {'code': '500', 'message': 'Internal Server Error'},
        ),
        (
            {'park_id': 'park_valid4'},
            400,
            {
                'code': 'NOT_SAAS_PARK',
                'message': 'Not a saas park, park_id: park_valid4',
            },
        ),
        (
            {'park_id': 'absent'},
            400,
            {
                'code': 'PARK_NOT_FOUND',
                'message': 'No park found for park_id absent',
            },
        ),
    ],
)
async def test_retrieve_by_park(
        taxi_fleet_parks, query, response_code, service_response,
):
    response = await taxi_fleet_parks.post(
        ENDPOINT_BY_PARK, json=query, headers=HEADERS,
    )

    assert response.status_code == response_code
    assert response.json() == service_response


@pytest.mark.parametrize(
    'park_id, config_value, park_label',
    [
        pytest.param('park_valid1', {}, 'park_valid1', id='empty config'),
        pytest.param(
            'park_valid1', {'rus': {}}, 'park_valid1', id='empty country',
        ),
        pytest.param(
            'park_valid6',
            {'rus': {'application': {'label': 'park_label'}}},
            'park_valid6',
            id='city not in a cache',
        ),
        pytest.param(
            'park_valid1',
            {
                'rus': {
                    'application': {
                        'label': 'park_label',
                        'exclude': ['park_valid1'],
                    },
                },
            },
            'park_valid1',
            id='excluded park',
        ),
        pytest.param(
            'park_valid1',
            {'rus': {'application': {'label': 'park_label'}}},
            'park_label',
            id='label in config',
        ),
    ],
)
async def test_retrieve_by_park_config_for_label(
        taxi_fleet_parks, taxi_config, park_id, config_value, park_label,
):
    taxi_config.set_values({'FLEET_COUNTRY_PROPERTIES': config_value})

    response = await taxi_fleet_parks.post(
        ENDPOINT_BY_PARK, json={'park_id': park_id}, headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {
        'dispatch_requirement': 'only_source_park',
        'label_id': park_label,
        'park_id': park_id,
    }


def clean_mongo_record(rec):
    return {
        k: v
        for k, v in rec.items()
        if k
        not in [
            'updated_ts',
            'modified_date',
            'dispatch_requirement',
            'is_getting_orders_from_app',
            'search_forced_performer_for_all_preorders',
        ]
    }
