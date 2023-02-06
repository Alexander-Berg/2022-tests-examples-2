import pytest  # noqa: F401

from tests_cargo_corp import utils

TIMESTAMP_RESULT = '2021-10-08 13:04:55+03'
TIMESTAMP1 = '2021-10-08T10:04:55+00:00'
TIMESTAMP2 = '2000-10-08T10:04:55+00:00'


@pytest.mark.pgsql('cargo_corp', queries=[utils.get_client_create_request()])
@pytest.mark.parametrize(
    'requests_',
    (
        pytest.param(
            [
                {
                    'clid': utils.CORP_CLIENT_ID,
                    'timestamp': TIMESTAMP1,
                    'expected_code': 200,
                },
                {
                    'clid': utils.CORP_CLIENT_ID,
                    'timestamp': TIMESTAMP2,
                    'expected_code': 200,
                },
            ],
            id='ok_and_overwrite_attempt',
        ),
        pytest.param(
            [
                {
                    'clid': 'bad' + utils.CORP_CLIENT_ID[3:],
                    'timestamp': TIMESTAMP1,
                    'expected_code': 404,
                },
            ],
            id='wrong_clid',
        ),
    ),
)
async def test_client_registration_date(
        taxi_cargo_corp, get_client_by_id, requests_,
):
    for request_ in requests_:
        corp_client_id = request_['clid']
        timestamp = request_['timestamp']
        expected_code = request_['expected_code']
        response = await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/update-registered',
            headers={
                'X-B2B-Client-Id': corp_client_id,
                'X-Yandex-Uid': utils.YANDEX_UID,
            },
            json={'registered_ts': timestamp},
        )
        assert response.status_code == expected_code

        if expected_code == 200:
            result = get_client_by_id(utils.CORP_CLIENT_ID)
            assert result[1] == TIMESTAMP_RESULT
