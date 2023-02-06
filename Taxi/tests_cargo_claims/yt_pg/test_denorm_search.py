import os

import pytest


@pytest.fixture(name='personal_client', autouse=True)
def _personal_client(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones(_):
        return {
            'items': [
                {
                    'id': 'debc244580cd48759e5d1764b759f9d6',
                    'value': '+79999999999',
                },
                {
                    'id': '3e684088c55f4f29bd0fa59cb163966f',
                    'value': '+19999999999',
                },
                {
                    'id': '4e243e5adea44cedacb69ef833315b29',
                    'value': '+29999999999',
                },
            ],
        }


AVAILABLE_CRITERIAS = {
    'created_from': '2020-12-31T00:00:00+00:00',
    'created_to': '2021-01-02T00:00:00+00:00',
    'due_from': '2020-12-31T00:00:00+00:00',
    'due_to': '2021-01-03T00:00:00+00:00',
    'claim_id': '9756ae927d7b42dc9bbdcbb832924343',
    'phone': '+19999999999',
    'corp_client_id': '798838e4b169456eb023595801bbb366',
    'external_order_id': '210406-074879',
    'performer_phone': '+79999999999',
    'status': 'failed',
}

AVAILABLE_CRITERIAS_NO_CLAIM = {
    'created_from': '2021-01-02T00:00:00+00:00',
    'created_to': '2020-12-31T00:00:00+00:00',
    'claim_id': '9756ae927d7b42dc9bbdcbb83292434x',
    'phone': '+79999999999',
    'corp_client_id': '798838e4b169456eb023595801bbb36x',
    'external_order_id': '210406-074877',
    'performer_phone': '+29999999999',
    'status': 'new',
}

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.xfail(
        os.getenv('IS_TEAMCITY'),
        strict=False,
        reason='some problems in CI with YT',
    ),
    pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml', 'yt_index.yaml']),
    pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql']),
    pytest.mark.usefixtures('yt_apply'),
]


@pytest.mark.parametrize(
    'criterias',
    (
        {k: v}
        for k, v in AVAILABLE_CRITERIAS.items()
        if k not in ('created_from', 'created_to', 'due_from', 'due_to')
    ),
)
async def test_denorm_search_single_criteria(
        taxi_cargo_claims, criterias, load_json, cut_response,
):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/search',
        json={'offset': 0, 'limit': 10, 'criterias': criterias},
    )

    assert response.status_code == 200, response.status_code
    assert len(response.json()['claims']) == 1, len(response.json()['claims'])
    assert response.json()['claims'][0] == cut_response(
        load_json('expected_response.json'),
    )


@pytest.mark.parametrize(
    'criterias,underlying_query',
    (
        (
            {
                'claim_id': AVAILABLE_CRITERIAS['claim_id'],
                'external_order_id': AVAILABLE_CRITERIAS['external_order_id'],
            },
            'by_claim_id',
        ),
        (
            {
                'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
                'external_order_id': AVAILABLE_CRITERIAS['external_order_id'],
            },
            'by_external_order_id',
        ),
        (
            {
                'claim_id': AVAILABLE_CRITERIAS['claim_id'],
                'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            },
            'by_claim_id',
        ),
    ),
)
async def test_denorm_search_filter_criterias(
        taxi_cargo_claims,
        criterias,
        underlying_query,
        load_json,
        cut_response,
):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/search',
        json={'offset': 0, 'limit': 10, 'criterias': criterias},
    )

    assert response.status_code == 200, response.status_code
    assert len(response.json()['claims']) == 1, len(response.json()['claims'])
    assert response.json()['claims'][0] == cut_response(
        load_json('expected_response.json'),
    )
    assert (
        response.json()['diagnostics']['retriever_function']
        == underlying_query
    )


@pytest.mark.parametrize(
    'criterias',
    (
        {
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            'created_from': AVAILABLE_CRITERIAS['created_from'],
        },
        {
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            'created_to': AVAILABLE_CRITERIAS['created_to'],
        },
        {
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            'created_from': AVAILABLE_CRITERIAS['created_from'],
            'created_to': AVAILABLE_CRITERIAS['created_to'],
        },
        {
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            'phone': AVAILABLE_CRITERIAS['phone'],
        },
        {
            'status': AVAILABLE_CRITERIAS['status'],
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
        },
        {
            'status': AVAILABLE_CRITERIAS['status'],
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            'phone': AVAILABLE_CRITERIAS['phone'],
        },
        {
            'status': AVAILABLE_CRITERIAS['status'],
            'performer_phone': AVAILABLE_CRITERIAS['performer_phone'],
        },
        {
            'status': AVAILABLE_CRITERIAS['status'],
            'phone': AVAILABLE_CRITERIAS['phone'],
        },
        {
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            'due_from': AVAILABLE_CRITERIAS['due_from'],
        },
        {
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            'due_to': AVAILABLE_CRITERIAS['due_to'],
        },
        {
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            'due_from': AVAILABLE_CRITERIAS['due_from'],
            'due_to': AVAILABLE_CRITERIAS['due_to'],
        },
    ),
)
async def test_denorm_search_combined_criterias(
        taxi_cargo_claims, criterias, load_json, cut_response,
):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/search',
        json={'offset': 0, 'limit': 10, 'criterias': criterias},
    )

    assert response.status_code == 200, response.status_code
    assert len(response.json()['claims']) == 1, len(response.json()['claims'])
    assert response.json()['claims'][0] == cut_response(
        load_json('expected_response.json'),
    )


@pytest.mark.parametrize(
    'criterias',
    (
        {k: v}
        for k, v in AVAILABLE_CRITERIAS_NO_CLAIM.items()
        if k not in ('created_from', 'created_to')
    ),
)
async def test_denorm_search_single_criteria_no_result(
        taxi_cargo_claims, criterias,
):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/search',
        json={'offset': 0, 'limit': 10, 'criterias': criterias},
    )

    assert response.status_code == 200, response.status_code
    assert response.json()['claims'] == [], len(response.json()['claims'])


@pytest.mark.parametrize(
    'criterias',
    (
        {
            'claim_id': AVAILABLE_CRITERIAS_NO_CLAIM['claim_id'],
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
        },
        {
            'claim_id': AVAILABLE_CRITERIAS['claim_id'],
            'corp_client_id': AVAILABLE_CRITERIAS_NO_CLAIM['corp_client_id'],
        },
    ),
)
async def test_denorm_search_filter_criterias_no_result(
        taxi_cargo_claims, criterias,
):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/search',
        json={'offset': 0, 'limit': 10, 'criterias': criterias},
    )

    assert response.status_code == 200, response.status_code
    assert response.json()['claims'] == [], len(response.json()['claims'])


@pytest.mark.parametrize(
    'criterias',
    (
        {
            'corp_client_id': AVAILABLE_CRITERIAS_NO_CLAIM['corp_client_id'],
            'created_to': AVAILABLE_CRITERIAS['created_to'],
        },
        {
            'corp_client_id': AVAILABLE_CRITERIAS['corp_client_id'],
            'created_to': AVAILABLE_CRITERIAS_NO_CLAIM['created_to'],
        },
    ),
)
async def test_denorm_search_combined_criterias_no_result(
        taxi_cargo_claims, criterias,
):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/search',
        json={'offset': 0, 'limit': 10, 'criterias': criterias},
    )

    assert response.status_code == 200, response.status_code
    assert response.json()['claims'] == [], len(response.json()['claims'])


async def test_denorm_search_no_criteria(
        taxi_cargo_claims, load_json, cut_response,
):
    response = await taxi_cargo_claims.post(
        '/v1/test/claim/search',
        json={'offset': 0, 'limit': 10, 'criterias': {}},
    )

    assert response.status_code == 200, response.status_code
    assert len(response.json()['claims']) == 1, len(response.json()['claims'])
    assert response.json()['claims'][0] == cut_response(
        load_json('expected_response.json'),
    )
