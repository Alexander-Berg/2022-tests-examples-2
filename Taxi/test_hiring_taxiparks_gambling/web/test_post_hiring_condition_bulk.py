import pytest

ROUTE = '/v2/hiring-conditions/bulk_post'


@pytest.mark.parametrize(
    'case',
    [
        'all',
        'deleted',
        'one_existed',
        'empty',
        'not_existed',
        'not_existed_and_one_existed',
    ],
)
async def test_post_hiring_condition_bulk(
        web_app_client, taxi_hiring_taxiparks_gambling_web, load_json, case,
):
    request = load_json('requests.json')[case]
    response = await taxi_hiring_taxiparks_gambling_web.post(
        ROUTE, json=request,
    )

    expected_response = load_json('expected_responses.json')[case]
    assert expected_response['status'] == response.status
    assert expected_response['data'] == await response.json()
