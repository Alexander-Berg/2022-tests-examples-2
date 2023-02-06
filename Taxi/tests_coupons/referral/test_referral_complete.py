import pytest

from tests_coupons.referral import util


YANDEX_UID = 'user_acceptor'
PROMOCODE_ID = '00000000-0000-0000-0000-000000000000'
ORDER_ID = 'abcdef123456'
PROMOCODE = 'promo123'

SQL_INSERT_PROMOCODE = f"""
INSERT INTO referral.promocodes
(id, config_id, yandex_uid, promocode, country)
VALUES ('{PROMOCODE_ID}', 1, 'user_donor', '{PROMOCODE}', 'rus')
"""
SQL_INSERT_REFERRAL_COMPLETION = f"""
INSERT INTO referral.referral_completions (yandex_uid, order_id, promocode_id)
VALUES ('{YANDEX_UID}', '{ORDER_ID}', '{PROMOCODE_ID}')
"""


@pytest.mark.parametrize(
    'expected_status_code, was_stq_request',
    [
        pytest.param(400, False, id='without_promocode_db_data'),
        pytest.param(
            200,
            True,
            marks=[
                pytest.mark.pgsql(
                    util.REFERRALS_DB_NAME,
                    files=[util.PGSQL_DEFAULT],
                    queries=[SQL_INSERT_PROMOCODE],
                ),
            ],
            id='save_new_ref_activation',
        ),
        pytest.param(
            200,
            True,
            marks=[
                pytest.mark.pgsql(
                    util.REFERRALS_DB_NAME,
                    files=[util.PGSQL_DEFAULT],
                    queries=[
                        SQL_INSERT_PROMOCODE,
                        SQL_INSERT_REFERRAL_COMPLETION,
                    ],
                ),
            ],
            id='has_previous_ref_activation',
        ),
    ],
)
async def test_save_ref_completion(
        taxi_coupons,
        referrals_postgres_db,
        expected_status_code,
        was_stq_request,
        stq,
):
    body = {
        'yandex_uid': YANDEX_UID,
        'order_id': ORDER_ID,
        'promocode': PROMOCODE,
    }

    response = await taxi_coupons.post('/v1/referral_complete', body)

    assert response.status_code == expected_status_code

    if response.status_code == 200:
        referrals_postgres_db.execute(
            f"""
            SELECT count(*) FROM referral.referral_completions
            WHERE yandex_uid = '{YANDEX_UID}' AND order_id = '{ORDER_ID}' AND
            promocode_id = '{PROMOCODE_ID}';
        """,
        )
        row_count = referrals_postgres_db.fetchone()[0]
        assert row_count == 1

    assert stq.coupons_generate_referral_reward.times_called == int(
        was_stq_request,
    )

    if was_stq_request:
        request_pararms = stq.coupons_generate_referral_reward.next_call()
        assert request_pararms['queue'] == 'coupons_generate_referral_reward'
        assert request_pararms['id'] == ORDER_ID
        assert request_pararms['kwargs']['order_id'] == ORDER_ID


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=[
                pytest.mark.pgsql(
                    util.REFERRALS_DB_NAME,
                    files=[util.PGSQL_DEFAULT],
                    queries=[SQL_INSERT_PROMOCODE],
                ),
            ],
        ),
    ],
)
async def test_metrics_exist(taxi_coupons, taxi_coupons_monitor):
    body = {
        'yandex_uid': YANDEX_UID,
        'order_id': ORDER_ID,
        'promocode': PROMOCODE,
    }
    response = await taxi_coupons.post('/v1/referral_complete', body)

    assert response.status_code == 200

    metrics_name = 'referral-complete-statistics'
    metrics = await taxi_coupons_monitor.get_metrics(metrics_name)

    assert metrics_name in metrics.keys()
