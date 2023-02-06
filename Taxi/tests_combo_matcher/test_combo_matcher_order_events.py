import json

import pytest


@pytest.mark.parametrize('testcase', ['dispatch', 'remove'])
async def test_order_events(
        taxi_combo_matcher,
        mockserver,
        pgsql,
        stq_runner,
        load,
        load_json,
        testcase,
):
    @mockserver.json_handler('/lookup/event')
    def _lookup_event(data):
        request = json.loads(data.get_data())
        assert request['status'] == 'found'
        assert request['candidate'] == {
            'metadata': {'combo': {'active': True}},
            'id': 'dbid_uuid0',
            'car_number': 'car_number0',
            'unique_driver_id': 'udid0',
        }
        return {'success': True}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def _defreeze(request):
        return mockserver.make_response(status=200)

    cursor = pgsql['combo_matcher'].cursor()
    sql_query = load(f'setup_{testcase}.sql').format(
        callback_url=mockserver.url('/lookup/event'),
    )
    cursor.execute(sql_query)

    events = load_json(f'events_{testcase}.json')

    for event in events:
        await stq_runner.combo_matcher_order_events.call(
            task_id='test_task', kwargs=event,
        )

    cursor = pgsql['combo_matcher'].cursor()
    cursor.execute(
        """
    select
      order_id,
      status,
      matching_id,
      revision,
      times_dispatched
    from
      combo_matcher.order_meta
    order by order_id
    """,
    )

    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    rows = [dict(zip(colnames, row)) for row in rows]

    assert rows == load_json(f'order_meta_{testcase}.json')
