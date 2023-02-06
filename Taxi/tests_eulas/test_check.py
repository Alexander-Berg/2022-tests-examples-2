import operator

import pytest


SORT_KEY = operator.itemgetter('yandex_uid') and operator.itemgetter('type')
URL = 'eulas/v1/check'

YANDEX_UID = 0
EULA_TYPE = 1


async def test_get_not_allowed(taxi_eulas):
    json = {'yandex_uids': ['12345678'], 'types': ['gdpr']}
    response = await taxi_eulas.get(URL, json=json)
    assert response.status_code == 405, response.text


@pytest.mark.config(EULAS_SERVICE_ENABLED=False)
async def test_service_disabled(taxi_eulas):
    json = {'yandex_uids': ['12345678'], 'types': ['gdpr']}
    response = await taxi_eulas.post(URL, json=json)
    assert response.status_code == 403, response.text
    assert response.json() == {'code': '403', 'message': 'Eulas: forbidden'}


@pytest.mark.now('2019-01-01T10:10:10+0300')
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_simple(taxi_eulas, pgsql):
    json = {'yandex_uids': ['2', '4'], 'types': ['a', 'b']}

    response = await taxi_eulas.post(
        URL, json=json, headers={'Accept-Language': 'en'},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    expected_response = {
        'eulas': [
            {
                'yandex_uid': '2',
                'type': 'b',
                'status': 'accepted',
                'valid_till': '2020-03-01T16:11:13+0000',
                'signed_at': '2018-01-01T16:11:13+0000',
            },
            {'yandex_uid': '4', 'type': 'b', 'status': 'unknown'},
            {'yandex_uid': '2', 'type': 'a', 'status': 'unknown'},
            {'yandex_uid': '4', 'type': 'a', 'status': 'unknown'},
        ],
    }

    data['eulas'].sort(key=SORT_KEY)
    expected_response['eulas'].sort(key=SORT_KEY)
    assert data == expected_response


@pytest.mark.now('2019-01-01T10:10:10+0300')
@pytest.mark.parametrize(
    'request_body, expected_code, expected_response',
    [
        (
            {'yandex_uids': ['2'], 'types': ['b']},
            200,
            {
                'eulas': [
                    {
                        'yandex_uid': '2',
                        'type': 'b',
                        'status': 'accepted',
                        'valid_till': '2020-03-01T16:11:13+0000',
                        'signed_at': '2018-01-01T16:11:13+0000',
                    },
                ],
            },
        ),
        (
            {'types': ['b']},
            400,
            {'code': '400', 'message': 'Field \'yandex_uids\' is missing'},
        ),
        (
            {'yandex_uids': ['2']},
            400,
            {'code': '400', 'message': 'Field \'types\' is missing'},
        ),
    ],
)
@pytest.mark.pgsql('eulas', files=['users.sql'])
async def test_request(
        taxi_eulas, request_body, expected_code, expected_response,
):
    response = await taxi_eulas.post(URL, json=request_body)

    assert response.status_code == expected_code, response.text

    data = response.json()
    if expected_code == 400:
        assert data['code'] == '400'
    else:
        assert data == expected_response
