import dateutil.parser
from typing import Optional
import uuid

import pytest

# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eats_discounts_statistics_plugins.generated_tests import *


ORDER_ID = '123'
DISCOUNTS = [
    {'discount_id': 1, 'discount_value': 10},
    {'discount_id': 2, 'discount_value': 20},
]
PERSONAL_PHONE_ID = 'test_personal_phone_id'
EATER_ID = 'test_eater_id'
YANDEX_UID = 'test_yandex_uid'


def _get_order_id(pgsql, yandex_uid):
    cursor = pgsql['eats_discounts_statistics'].cursor()
    cursor.execute(
        f"""
        SELECT DISTINCT order_id
        FROM eats_discounts_statistics.discount_usages
        WHERE yandex_uid = '{yandex_uid}\';
    """,
    )
    rows = list(row for row in cursor)
    return rows[0][0]


@pytest.mark.config(
    EATS_DISCOUNTS_STATISTICS_ORDER_ID_CLEANUP={
        'enabled': True,
        'interval_after_creation': 10,
    },
)
@pytest.mark.parametrize(
    'time_for_cleanup, excepted_order_id',
    (
        pytest.param('2021-01-01T00:00:00+00:00', ORDER_ID),
        pytest.param('2022-01-02T00:00:00+00:00', ORDER_ID),
        pytest.param('2022-01-12T00:00:00+00:00', None),
    ),
)
@pytest.mark.now('2022-01-01T00:00:00+00:00')
async def test_order_id_cleanup_cron_task(
        client,
        stq_runner,
        mocked_time,
        pgsql,
        time_for_cleanup: str,
        excepted_order_id: Optional[str],
):
    await stq_runner.eats_discounts_statistics_add.call(
        task_id=str(uuid.uuid4()),
        kwargs={
            'order_id': ORDER_ID,
            'discounts': DISCOUNTS,
            'time': '2022-01-01T00:00:00+00:00',
            'eater_id': EATER_ID,
            'yandex_uid': YANDEX_UID,
            'personal_phone_id': PERSONAL_PHONE_ID,
        },
    )
    mocked_time.set(dateutil.parser.parse(time_for_cleanup))
    response = await client.post(
        'service/cron', json={'task_name': 'order_id-cleanup'},
    )
    assert response.status_code == 200
    assert _get_order_id(pgsql, YANDEX_UID) == excepted_order_id


@pytest.mark.now('2022-01-01T00:00:00+00:00')
async def test_order_id_cleanup_cancel(stq_runner, pgsql):
    await stq_runner.eats_discounts_statistics_add.call(
        task_id=str(uuid.uuid4()),
        kwargs={
            'order_id': ORDER_ID,
            'discounts': DISCOUNTS,
            'time': '2022-01-01T00:00:00+00:00',
            'eater_id': EATER_ID,
            'yandex_uid': YANDEX_UID,
            'personal_phone_id': PERSONAL_PHONE_ID,
        },
    )
    await stq_runner.eats_discounts_statistics_cancel.call(
        task_id=str(uuid.uuid4()),
        kwargs={'order_id': ORDER_ID, 'discounts': DISCOUNTS},
    )
    assert _get_order_id(pgsql, YANDEX_UID) is None
