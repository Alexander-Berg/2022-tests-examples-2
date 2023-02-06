import pytest  # noqa: F401

from tests_cargo_corp import utils


EXTRA_INFO = {'city': 'Moscow', 'inn': '1234567890'}
DRAFT_TAG = 'offer_draft_form'
INFO_TAG = 'offer_info_form'


@pytest.fixture(name='make_client_offer_upsert_request')
def _make_client_offer_upsert_request(taxi_cargo_corp):
    async def wrapper(
            client_id=utils.CORP_CLIENT_ID, json=None, is_admin_mode=False,
    ):
        headers = {'X-B2B-Client-Id': client_id}
        if is_admin_mode:
            headers['X-Request-Mode'] = 'admin'
        response = await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/offer/upsert',
            headers=headers,
            json=json or {},
        )
        return response

    return wrapper


@pytest.mark.parametrize(
    (
        'corp_client_id',
        'expected_code',
        'expected_json',
        'info_tag',
        'is_admin_mode',
    ),
    [
        pytest.param(
            utils.CORP_CLIENT_ID, 200, {}, DRAFT_TAG, False, id='OK-1',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID, 200, {}, DRAFT_TAG, True, id='OK-2',
        ),
        pytest.param(utils.CORP_CLIENT_ID, 200, {}, INFO_TAG, True, id='OK-3'),
        pytest.param(
            utils.CORP_CLIENT_ID,
            403,
            {'code': 'not_allowed', 'message': 'Operation is not allowed'},
            INFO_TAG,
            False,
            id='bad_request_mode',
        ),
        pytest.param(
            utils.CORP_CLIENT_ID_1,
            404,
            {'code': 'not_found', 'message': 'Unknown corp_client'},
            DRAFT_TAG,
            False,
            id='client_not_found',
        ),
    ],
)
async def test_client_upsert_info_offer(
        make_client_offer_upsert_request,
        get_client_extra_info,
        corp_client_id,
        expected_code,
        expected_json,
        info_tag,
        is_admin_mode,
):
    request = {'extra_info': EXTRA_INFO, 'extra_info_tag': info_tag}
    response = await make_client_offer_upsert_request(
        client_id=corp_client_id, json=request, is_admin_mode=is_admin_mode,
    )

    assert response.status_code == expected_code
    assert response.json() == expected_json
    if expected_code == 200:
        extra_info_from_db = get_client_extra_info(utils.CORP_CLIENT_ID)
        assert extra_info_from_db[0] == EXTRA_INFO
        assert extra_info_from_db[1] == info_tag
