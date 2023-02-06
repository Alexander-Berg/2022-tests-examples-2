import pytest

from tests_cargo_corp import utils


LOCAL_CORP_CLIENT_ID = 'some_long_id_string_of_length_32'
LOCAL_CARD_ID = 'card_2'


@pytest.fixture(name='assert_card_is_unbound')
def _assert_card(pgsql):
    def wrapper():
        cursor = pgsql['cargo_corp'].conn.cursor()

        cursor.execute(
            """
            SELECT
                is_bound
            FROM corp_clients.bound_cards
            WHERE
                corp_client_id = '{}'
                AND
                card_id = '{}'
        """.format(
                utils.CORP_CLIENT_ID, utils.CARD_ID,
            ),
        )
        row = cursor.fetchone()
        cursor.close()

        assert not row[0]

    return wrapper


@pytest.mark.parametrize(
    ['corp_client_id', 'card_id', 'expected_code', 'expected_json'],
    (
        pytest.param(utils.CORP_CLIENT_ID, utils.CARD_ID, 200, {}, id='ok'),
        pytest.param(
            LOCAL_CORP_CLIENT_ID,
            utils.CARD_ID,
            404,
            {'code': 'not_found', 'message': 'Unknown corp_client'},
            id='bad corp_client',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID,
            LOCAL_CARD_ID,
            404,
            {'code': 'not_found', 'message': 'Unknown card_id'},
            id='bad card_id',
        ),
    ),
)
async def test_corp_client_unbound_card(
        taxi_cargo_corp,
        user_has_rights,
        register_default_card,
        assert_card_is_unbound,
        corp_client_id,
        card_id,
        expected_code,
        expected_json,
):
    for _ in range(2):
        response = await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/card/unbound',
            headers={'X-B2B-Client-Id': corp_client_id},
            json={'card_id': card_id},
        )
        assert response.status_code == expected_code
        assert response.json() == expected_json
        if expected_code == 200:
            assert_card_is_unbound()
