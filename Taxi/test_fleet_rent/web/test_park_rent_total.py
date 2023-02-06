import pytest


@pytest.mark.pgsql('fleet_rent', files=['base.sql'])
async def test_time_filters(web_app_client):
    response = await web_app_client.post(
        '/v1/park/rents/aggregations?park_id=park_id',
        json={
            'time_range': {
                'from': '2020-01-01T00:00+00:00',
                'to': '2020-01-02T00:00+00:00',
                'applies_to': 'begins_at',
            },
        },
    )
    assert (await response.json()) == {
        'total_by_asset': {
            'car': 0,
            'other': {'chair': 1, 'deposit': 0, 'device': 0, 'misc': 3},
        },
        'total_records': 4,
    }

    response = await web_app_client.post(
        '/v1/park/rents/aggregations?park_id=park_id',
        json={
            'time_range': {
                'from': '2020-01-04T00:00+00:00',
                'applies_to': 'ends_at',
            },
        },
    )
    assert (await response.json()) == {
        'total_by_asset': {
            'car': 0,
            'other': {'chair': 1, 'deposit': 1, 'device': 1, 'misc': 3},
        },
        'total_records': 6,
    }

    response = await web_app_client.post(
        '/v1/park/rents/aggregations?park_id=park_id',
        json={
            'time_range': {
                'from': '2020-01-04T12:00+00:00',
                'applies_to': 'duration',
            },
        },
    )
    assert (await response.json()) == {
        'total_by_asset': {
            'car': 0,
            'other': {'chair': 1, 'deposit': 1, 'device': 1, 'misc': 3},
        },
        'total_records': 6,
    }
