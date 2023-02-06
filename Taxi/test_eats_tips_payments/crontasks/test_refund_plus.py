import psycopg2.extras
import pytest

from eats_tips_payments.generated.cron import run_cron
from test_eats_tips_payments import conftest


ORDER_ID = 2


@pytest.mark.mysql('chaevieprosto', files=['mysql_chaevieprosto.sql'])
@pytest.mark.pgsql('eats_tips_payments', files=['pg_eats_tips.sql'])
async def test_refund_plus(mysql, pgsql, stq):
    await run_cron.main(
        ['eats_tips_payments.crontasks.refund_plus', '-t', '0'],
    )
    conftest.check_task_queued(
        stq,
        stq.eats_tips_payments_charge_plus,
        {'order_id': ORDER_ID},
        ['operation'],
    )
    assert stq.is_empty

    with mysql['chaevieprosto'].cursor() as cursor:
        cursor.execute('select * from refund_plus order by transaction_id')
        rows = cursor.fetchall()
        assert ((1, 1), (2, 1)) == rows

    cursor = pgsql['eats_tips_payments'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    cursor.execute(
        """
        SELECT plus_amount, cashback_status, is_refunded
        FROM eats_tips_payments.orders
        ORDER BY order_id
        """,
    )
    rows = cursor.fetchall()
    assert rows[0] == {
        'cashback_status': 'success',
        'plus_amount': 10,
        'is_refunded': False,
    }
    assert rows[1] == {
        'cashback_status': 'in-progress',
        'plus_amount': 10,
        'is_refunded': True,
    }
