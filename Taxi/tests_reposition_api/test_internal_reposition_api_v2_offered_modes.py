# pylint: disable=import-only-modules
import pytest

OUTDATED_ETAG = '"27DkPbk5h6e5Y9L6"'
UP_TO_DATE_ETAG = '"Q8J0yelOh2dER7OY"'
FUTURE_ETAG = '"2Q5xmbmwh5eoKM7W"'
INVALID_ETAG = '"0123456789abcasync def"'


@pytest.mark.now('2017-10-14T12:00:00')
@pytest.mark.parametrize(
    'etag', [None, OUTDATED_ETAG, UP_TO_DATE_ETAG, FUTURE_ETAG, INVALID_ETAG],
)
@pytest.mark.pgsql('reposition', files=['drivers.sql'])
async def test_offered_modes_empty_db(taxi_reposition_api, pgsql, etag):
    headers = {'Accept-Language': 'en-EN', 'If-None-Match': etag}

    if etag is None:
        del headers['If-None-Match']

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v2/offered_modes?uuid=driverSS&dbid=1488',
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.now('2017-10-14T12:00:00')
@pytest.mark.parametrize(
    'etag', [None, OUTDATED_ETAG, UP_TO_DATE_ETAG, FUTURE_ETAG, INVALID_ETAG],
)
@pytest.mark.parametrize('valid_tanker_key', [True, False])
async def test_offered_modes(
        taxi_reposition_api, pgsql, load, load_json, etag, valid_tanker_key,
):
    headers = {'Accept-Language': 'en-EN', 'If-None-Match': etag}

    if etag is None:
        del headers['If-None-Match']

    queries = [load('drivers.sql')]
    if valid_tanker_key:
        expected = load_json('offered_modes.json')
        queries.append(load('offered_modes.sql'))
    else:
        expected = load_json('offered_modes_bad_tanker_key.json')
        queries.append(load('offered_modes_bad_tanker_key.sql'))

    pgsql['reposition'].apply_queries(queries)

    response = await taxi_reposition_api.post(
        '/internal/reposition-api/v2/offered_modes?uuid=driverSS&dbid=1488',
        headers=headers,
    )

    if etag is None or etag == OUTDATED_ETAG or etag == INVALID_ETAG:
        assert response.status_code == 200
        actual = response.json()

        actual_restrictions = actual['SuperSurge']['locations']['0'][
            'restrictions'
        ]
        expected_restrictions = expected['SuperSurge']['locations']['0'][
            'restrictions'
        ]
        assert actual_restrictions is not None and (
            actual_restrictions == expected_restrictions
            or actual_restrictions == list(reversed(expected_restrictions))
        )

        assert response.json() == expected
        assert response.headers['ETag'] == UP_TO_DATE_ETAG
    else:
        assert response.status_code == 304
