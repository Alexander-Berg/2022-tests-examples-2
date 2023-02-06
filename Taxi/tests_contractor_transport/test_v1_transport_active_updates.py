import pytest


DS_CACHE_ENABLED = {
    '__default__': {
        'cache_enabled': True,
        'full_update_request_parts_count': 1,
        'last_revision_overlap_sec': 1,
    },
}


@pytest.mark.config(DRIVER_STATUSES_CACHE_SETTINGS=DS_CACHE_ENABLED)
@pytest.mark.pgsql(
    'contractors_transport', files=['contractors_transport.sql'],
)
@pytest.mark.parametrize(
    'query_parameters, response_json',
    [
        ({}, 'all_contractors.json'),
        (
            {'cursor': '2020-06-18T21:00:00+0000_park4_driver4|1234567_2'},
            'last_contractor.json',
        ),
        (
            {'cursor': '2020-06-18T21:00:00+0000_park4_driver4|1234567_3'},
            'empty.json',
        ),
        ({'only_active_contractors': 'true'}, 'active_contractors.json'),
    ],
)
async def test_transport_updates(
        taxi_contractor_transport, query_parameters, response_json, load_json,
):
    response = await taxi_contractor_transport.get(
        'v1/transport-active/updates', params=query_parameters,
    )
    assert response.status_code == 200
    assert response.json() == load_json(response_json)


@pytest.mark.config(DRIVER_STATUSES_CACHE_SETTINGS=DS_CACHE_ENABLED)
@pytest.mark.pgsql(
    'contractors_transport', files=['contractors_transport.sql'],
)
async def test_active_parts_updates(taxi_contractor_transport):
    url = 'v1/transport-active/updates?limit=1&only_active_contractors=true'

    async def _get_with_cursor(cursor=None):
        request_url = url
        params = {'only_active_contractors': True, 'limit': 1}
        if cursor:
            params['cursor'] = cursor
        response = await taxi_contractor_transport.get(
            request_url, params=params,
        )
        assert response.status_code == 200
        return response.json()

    response = await _get_with_cursor()
    transport = response['contractors_transport']
    assert len(transport) == 1
    assert transport[0]['contractor_id'] == 'park4_driver4'
    cursor = response['cursor']
    assert (
        cursor
        == '1593778762506000_park4_driver4|2020-07-03T11:49:22+0000_0|1593776962_0'  # noqa: E501
    )

    response = await _get_with_cursor(cursor)
    transport = response['contractors_transport']
    assert len(transport) == 1
    assert transport[0]['contractor_id'] == 'park4_driver5'
    cursor = response['cursor']
    assert (
        cursor
        == '1593778762506000_park4_driver5|2020-07-03T11:49:22+0000_0|1593776962_0'  # noqa: E501
    )

    response = await _get_with_cursor(cursor)
    assert response['contractors_transport'] == []


async def test_bad_request(taxi_contractor_transport):
    response = await taxi_contractor_transport.get(
        'v1/transport-active/updates?cursor=12345',
    )
    assert response.status_code == 400
