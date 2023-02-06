import datetime

import pytest

from tests_bank_topup import common


REQUEST_PATH = '/topup-internal/v1/execute_autotopup/'


def get_headers(idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN):
    return {'X-Idempotency-Token': idempotency_token}


def get_body(
        bank_uid=common.DEFAULT_YANDEX_BUID,
        watchdog_id=common.DEFAULT_WATCHDOG_ID,
):
    return {
        'buid': bank_uid,
        'watchdog_id': watchdog_id,
        'balance': common.DEFAULT_MONEY,
    }


@pytest.mark.parametrize(
    'bank_uid, watchdog_id',
    [
        (common.ANOTHER_YANDEX_BUID, common.DEFAULT_WATCHDOG_ID),
        (common.DEFAULT_YANDEX_BUID, common.ANOTHER_WATCHDOG_ID),
    ],
)
async def test_not_found_if_watchdog_absent(
        pgsql, taxi_bank_topup, bank_uid, watchdog_id,
):
    common.insert_autotopup(pgsql, common.make_autotopup(bank_uid=bank_uid))
    common.insert_watchdog(
        pgsql,
        common.make_watchdog(bank_uid=bank_uid, watchdog_id=watchdog_id),
    )

    response = await taxi_bank_topup.post(
        REQUEST_PATH,
        headers=get_headers(),
        json=get_body(
            bank_uid=common.DEFAULT_YANDEX_BUID,
            watchdog_id=common.DEFAULT_WATCHDOG_ID,
        ),
    )
    assert response.status_code == 404


async def test_success_if_watchdog_disabled_without_execute(
        pgsql, taxi_bank_topup,
):
    common.insert_autotopup(pgsql, common.make_autotopup())
    common.insert_watchdog(
        pgsql,
        common.make_watchdog(disabled_at=datetime.datetime.now().isoformat()),
    )

    response = await taxi_bank_topup.post(
        REQUEST_PATH, headers=get_headers(), json=get_body(),
    )
    assert response.status_code == 200


async def test_success_if_watchdog_disabled_by_same_execute(
        pgsql, taxi_bank_topup,
):
    common.insert_autotopup(pgsql, common.make_autotopup())
    common.insert_watchdog(
        pgsql,
        common.make_watchdog(
            disabled_at=datetime.datetime.now().isoformat(),
            execute_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
    )

    response = await taxi_bank_topup.post(
        REQUEST_PATH, headers=get_headers(), json=get_body(),
    )
    assert response.status_code == 200


async def test_conflict_if_watchdog_disabled_by_another_execute(
        pgsql, taxi_bank_topup,
):
    common.insert_autotopup(pgsql, common.make_autotopup())
    common.insert_watchdog(
        pgsql,
        common.make_watchdog(
            disabled_at=datetime.datetime.now().isoformat(),
            execute_idempotency_token=common.ANOTHER_IDEMPOTENCY_TOKEN,
        ),
    )

    response = await taxi_bank_topup.post(
        REQUEST_PATH, headers=get_headers(), json=get_body(),
    )
    assert response.status_code == 409


async def test_fail_if_watchdog_disabled_during_processing(
        pgsql, testpoint, taxi_bank_topup,
):
    common.insert_autotopup(pgsql, common.make_autotopup())
    watchdog = common.make_watchdog()
    common.insert_watchdog(pgsql, watchdog)
    watchdog['disabled_at'] = datetime.datetime.now().isoformat()

    @testpoint('disable_autotopup')
    def _disable_autotopup(stats):
        common.update_watchdog(pgsql, watchdog)

    response = await taxi_bank_topup.post(
        REQUEST_PATH, headers=get_headers(), json=get_body(),
    )
    assert response.status_code == 500


async def test_fail_if_autotopup_disabled_during_processing(
        pgsql, testpoint, taxi_bank_topup,
):
    autotopup = common.make_autotopup()
    common.insert_autotopup(pgsql, autotopup)
    common.insert_watchdog(pgsql, common.make_watchdog())
    autotopup['enabled'] = False
    autotopup['disabled_at'] = datetime.datetime.now().isoformat()

    @testpoint('disable_autotopup')
    def _disable_autotopup(stats):
        common.update_autotopup(pgsql, autotopup)

    response = await taxi_bank_topup.post(
        REQUEST_PATH, headers=get_headers(), json=get_body(),
    )
    assert response.status_code == 500


async def test_success_if_watchdog_exists(pgsql, taxi_bank_topup):
    common.insert_autotopup(pgsql, common.make_autotopup())
    common.insert_watchdog(pgsql, common.make_watchdog())

    response = await taxi_bank_topup.post(
        REQUEST_PATH, headers=get_headers(), json=get_body(),
    )
    assert response.status_code == 200
