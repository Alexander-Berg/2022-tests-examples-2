import datetime

import pytest


@pytest.mark.parametrize('test_name', ['base', 'multiple', 'combo_buffer'])
@pytest.mark.pgsql('combo_contractors', files=['orders.sql'])
async def test_combo_contractors_order_events(
        stq_runner, pgsql, load_json, test_name,
):
    for kwargs in load_json(f'stq_events_{test_name}.json'):
        await stq_runner.combo_contractors_order_events.call(
            task_id='combo_contractors_order_events', args=[], kwargs=kwargs,
        )
    cursor = pgsql['combo_contractors'].cursor()
    cursor.execute(
        """
        select
          order_id,
          dbid_uuid,
          to_char(updated, 'DD Mon YYYY HH:MI:SS') updated,
          taxi_status,
          source,
          destination,
          event_index,
          ready_status,
          tariff_class,
          tariff_zone,
          has_comment,
          calc_alternative_type,
          coalesce(user_phone_id, '') user_phone_id,
          round(
            extract(
              epoch
              FROM
                plan_transporting_time
            )::numeric
          )::integer plan_transporting_time,
          round(
            plan_transporting_distance::numeric
          )::integer plan_transporting_distance,
          coalesce(payment_type, '') payment_type,
          coalesce(corp_client_id, '') corp_client_id,
          combo_info,
          (SELECT CASE WHEN transporting_started_at = NULL THEN NULL
          ELSE to_char(transporting_started_at, 'DD Mon YYYY HH:MI:SS') END)
          as transporting_started_at,
          COALESCE(has_chain_parent, FALSE) as has_chain_parent,
          (SELECT CASE WHEN destinations_changed_at = NULL THEN NULL
          ELSE to_char(destinations_changed_at, 'DD Mon YYYY HH:MI:SS') END)
          as destinations_changed_at
        from
          combo_contractors.customer_order
        order by
          order_id
        """,
    )
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    orders = [dict(zip(colnames, rows[i])) for i in range(len(rows))]
    assert orders == load_json(f'expected_orders_{test_name}.json')

    cursor.execute(
        """
                      SELECT
                        batch_id,
                        order_id
                      FROM
                        combo_contractors.combo_batch
                      ORDER BY
                        order_id
                    """,
    )
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    batches = [dict(zip(colnames, rows[i])) for i in range(len(rows))]
    assert batches == load_json(f'expected_batches_{test_name}.json')


@pytest.mark.now('2018-12-27T16:38:00.000000+0000')
async def test_promised_timestamp_created(stq_runner, pgsql, load_json):
    async def _publish_and_query_db(event):
        await stq_runner.combo_contractors_order_events.call(
            task_id='combo_contractors_order_events', args=[], kwargs=event,
        )
        cursor = pgsql['combo_contractors'].cursor()
        cursor.execute(
            """
            select promised_timestamp
            from combo_contractors.customer_order
            """,
        )
        rows = cursor.fetchall()
        assert len(rows) == 1
        return rows[0]

    event = load_json('stq_events_base.json')[0]
    rows = await _publish_and_query_db(event)
    assert rows == (None,)

    event['order_event']['taxi_status'] = 'transporting'
    event['order_event']['event_index'] += 1
    rows = await _publish_and_query_db(event)
    assert rows == (datetime.datetime(2018, 12, 27, 16, 38, 43),)

    # check that no override happens
    event['order_event']['plan_transporting_time_sec'] += 10
    event['order_event']['event_index'] += 1
    rows = await _publish_and_query_db(event)
    assert rows == (datetime.datetime(2018, 12, 27, 16, 38, 43),)
