# pylint: disable=import-only-modules
import pytest

OUTDATED_ETAG = '"Q8J0yel5i5aER7OY"'
UP_TO_DATE_ETAG = '"2Q5xmbmQijboKM7W"'
FUTURE_ETAG = '"7O9pgenriGeNQxy0"'
INVALID_ETAG = '"0123456789abcdef"'


@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.parametrize(
    'etag', [None, OUTDATED_ETAG, UP_TO_DATE_ETAG, FUTURE_ETAG, INVALID_ETAG],
)
@pytest.mark.pgsql('reposition', files=['drivers.sql', 'mode_home.sql'])
async def test_state_empty_db(taxi_reposition_api, etag):
    headers = {'Accept-Language': 'en-EN', 'If-None-Match': etag}

    if etag is None:
        del headers['If-None-Match']

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v2/state?uuid=uuid&dbid=dbid777',
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {
        'state': {'status': 'no_state'},
        'usages': {
            'home': {
                'start_screen_usages': {'title': '', 'subtitle': ''},
                'usage_allowed': True,
                'usage_limit_dialog': {'title': '', 'body': ''},
            },
        },
    }


@pytest.mark.now('2017-10-15T18:18:46')
@pytest.mark.parametrize(
    'state',
    ['empty', 'active', 'disabled', 'bonus', 'active_bad_usage_tanker_key'],
)
@pytest.mark.parametrize(
    'etag', [None, OUTDATED_ETAG, UP_TO_DATE_ETAG, FUTURE_ETAG, INVALID_ETAG],
)
async def test_state(taxi_reposition_api, pgsql, load, load_json, state, etag):
    queries = [load('drivers.sql'), load(state + '_state.sql')]
    pgsql['reposition'].apply_queries(queries)

    headers = {'Accept-Language': 'en-EN', 'If-None-Match': etag}

    if etag is None:
        del headers['If-None-Match']

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v2/state?uuid=uuid&dbid=dbid777',
        headers=headers,
    )

    if etag is None or etag == OUTDATED_ETAG or etag == INVALID_ETAG:
        assert response.status_code == 200
        assert response.json() == load_json(state + '_state.json')
        assert response.headers['ETag'] == UP_TO_DATE_ETAG
    else:
        assert response.status_code == 304
