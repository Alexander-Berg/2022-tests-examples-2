# pylint: disable=line-too-long
import pytest


@pytest.mark.parametrize(
    'passport_mock, bad_json, expected_status, expected_error_text',
    [
        (
            'client1',
            '{"client_id": "kkskskjd2kj23", "user_phone": "+9992223344",}',
            400,
            'Expecting property name enclosed in double quotes: line 1 column 60 (char 59)',  # noqa
        ),
        (
            'client1',
            '{',
            400,
            'Expecting property name enclosed in double quotes: line 1 column 2 (char 1)',  # noqa
        ),
    ],
    indirect=['passport_mock'],
)
async def test_json_decode_error(
        taxi_corp_auth_client,
        passport_mock,
        bad_json,
        expected_status,
        expected_error_text,
):
    response = await taxi_corp_auth_client.post(
        '/1.0/search/users', data=bad_json,
    )

    response_json = await response.json()
    assert response.status == expected_status
    assert response_json['errors'][0]['text'] == expected_error_text
