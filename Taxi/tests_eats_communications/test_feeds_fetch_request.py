import pytest


FEEDS_FETCH_RESPONSES = {
    'fetch': {
        'polling_delay': 60,
        'etag': 'my-tag',
        'feed': [],
        'has_more': False,
    },
    'fetch_by_id': {'feed': []},
}


def make_experiment(name, default_value):
    return pytest.mark.experiments3(
        name=name,
        consumers=['eats-communications/communications'],
        default_value=default_value,
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    )


@pytest.mark.parametrize(
    'url,fetch_url',
    [
        pytest.param(
            '/eats/v1/eats-communications/v1/communications',
            'fetch',
            id='communications',
        ),
        pytest.param(
            '/eats/v1/eats-communications/v1/communications/retrieve',
            'fetch_by_id',
            id='communications/retrieve',
        ),
        pytest.param(
            '/eats-communications/v1/layout/communications',
            'fetch',
            id='layout/communications',
        ),
    ],
)
@make_experiment('enabled', {'enabled': True})
@make_experiment('disabled', {'enabled': False})
@make_experiment('enabled_2', {'enabled': True, 'unused': 123})
@make_experiment('enabled_wrong_type', {'enabled': 1})
@make_experiment('no_enabled', {'unused': 123})
@make_experiment('not_object', 123)
async def test_fetch_communications(
        taxi_eats_communications, mockserver, url, fetch_url,
):
    @mockserver.json_handler('/feeds/v1/' + fetch_url)
    def feeds(request):
        assert set(request.json['channels']) == set(
            ['experiment:enabled', 'experiment:enabled_2'],
        )
        return FEEDS_FETCH_RESPONSES[fetch_url]

    if url.endswith('layout/communications'):

        @mockserver.json_handler('/eda-catalog/v1/shortlist')
        def _shortlist(request):
            return {'payload': {'places': []}}

    response = await taxi_eats_communications.post(
        url,
        json={
            'application': {
                'device_id': 'my_device_id',
                'platform': 'my_platform',
                'screen_resolution': {},
            },
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'ids': ['id_1'],
        },
    )
    assert feeds.times_called == 1
    assert response.status_code == 200
