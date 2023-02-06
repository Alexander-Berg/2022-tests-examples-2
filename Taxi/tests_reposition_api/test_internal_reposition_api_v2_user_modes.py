# pylint: disable=import-only-modules
import pytest

OUTDATED_ETAG = '"PwmloejRfMeQMGAD"'
UP_TO_DATE_ETAG = '"27DkPbkRfOa5Y9L6"'
FUTURE_ETAG = '"Q8J0yelYfoaER7OY"'
INVALID_ETAG = '"0123456789abcdef"'


@pytest.mark.now('2017-10-14T12:00:00')
@pytest.mark.parametrize(
    'etag', [None, OUTDATED_ETAG, UP_TO_DATE_ETAG, FUTURE_ETAG, INVALID_ETAG],
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'mode_home.sql'])
async def test_user_modes_empty_db(taxi_reposition_api, pgsql, etag):
    headers = {'Accept-Language': 'en-EN', 'If-None-Match': etag}

    if etag is None:
        del headers['If-None-Match']

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v2/user_modes?uuid=driverSS&dbid=1488',
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        'home': {
            'type': 'free_point',
            'locations': {},
            'client_attributes': {'dead10cc': 'deadbeef'},
            'ready_panel': {
                'title': 'Ready panel',
                'subtitle': 'Ready panel subtitle',
            },
            'permitted_work_modes': ['orders'],
            'restrictions': [],
            'start_screen_text': {'title': 'Home', 'subtitle': 'Drive home'},
            'start_screen_subtitle': 'Drive home',
            'tutorial_body': 'Drive home mode.\n',
        },
    }


@pytest.mark.now('2017-10-14T12:00:00')
@pytest.mark.parametrize(
    'etag', [None, OUTDATED_ETAG, UP_TO_DATE_ETAG, FUTURE_ETAG, INVALID_ETAG],
)
@pytest.mark.parametrize('valid_tanker_key', [True, False])
async def test_user_modes(
        taxi_reposition_api, load_json, etag, pgsql, load, valid_tanker_key,
):
    headers = {'Accept-Language': 'en-EN', 'If-None-Match': etag}

    if etag is None:
        del headers['If-None-Match']

    queries = [load('drivers.sql')]
    if valid_tanker_key:
        queries.append(load('user_modes.sql'))
        expected_json = load_json('user_modes.json')
    else:
        queries.append(load('user_modes_bad_tanker_key.sql'))
        expected_json = load_json('user_modes_bad_tanker_key.json')
    pgsql['reposition'].apply_queries(queries)

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v2/user_modes?uuid=driverSS&dbid=1488',
        headers=headers,
    )

    if etag is None or etag == OUTDATED_ETAG or etag == INVALID_ETAG:
        assert response.status_code == 200
        assert response.json() == expected_json
        assert response.headers['ETag'] == UP_TO_DATE_ETAG
    else:
        assert response.status_code == 304


@pytest.mark.now('2017-10-14T12:00:00')
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'user_modes.sql'])
@pytest.mark.parametrize('config_enabled', [True, False])
async def test_config_zombie_etag(
        taxi_reposition_api, experiments3, config_enabled,
):
    if config_enabled:
        experiments3.add_config(
            name='reposition_api_use_geo_for_zombie_etag',
            consumers=['reposition-api/zombie_etag'],
            match={'predicate': {'type': 'true'}, 'enabled': True},
            clauses=[],
            default_value={'enabled': True},
        )

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v2/user_modes?uuid=uuid&dbid=dbid777',
        headers={'Accept-Language': 'en-EN'},
    )

    expected_etag = (
        '\"tmp_0_4867657185626755466_0_14\"'
        if config_enabled
        else '\"tmp_0_0_14\"'
    )

    assert response.status_code == 200
    assert response.headers['ETag'] == expected_etag
