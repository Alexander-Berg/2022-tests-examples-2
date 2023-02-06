from tests_bank_userinfo import utils

BUID = '7948e3a9-623c-4524-a390-9e4264d27a77'


async def test_no_buid(taxi_bank_userinfo, mockserver, pgsql):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/unblock_user',
        json={'buid': '7948e3a9-623c-4524-a390-9e4264d27a76'},
    )

    assert response.status_code == 404


async def test_unblock_ok(taxi_bank_userinfo, pgsql):
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/unblock_user', json={'buid': BUID},
    )

    assert response.status_code == 200
    assert response.json() == {'buid_status': 'FINAL'}
    assert utils.select_buid_status(pgsql, BUID) == 'FINAL'
    assert len(utils.select_buid_history(pgsql, BUID)) == 3


async def test_unblock_buid_already_unblocked(
        taxi_bank_userinfo, mockserver, pgsql,
):
    utils.update_buid_status(pgsql, BUID, 'FINAL')
    response = await taxi_bank_userinfo.post(
        '/userinfo-internal/v1/unblock_user', json={'buid': BUID},
    )
    assert response.status_code == 200
    assert response.json() == {'buid_status': 'FINAL'}
    assert utils.select_buid_status(pgsql, BUID) == 'FINAL'
    assert len(utils.select_buid_history(pgsql, BUID)) == 2
