import datetime


import pytest


@pytest.mark.parametrize(
    'testcase',
    [
        'create',
        'update',
        'found_first_order',
        'found_second_order',
        'not_found',
        'not_acceptable',
    ],
)
async def test_performer_for_order(
        taxi_combo_matcher, load_json, load, pgsql, testcase,
):
    cursor = pgsql['combo_matcher'].cursor()
    cursor.execute(load(f'setup_{testcase}.sql'))

    request = load_json(f'request_{testcase}.json')
    response = await taxi_combo_matcher.post(
        '/performer-for-order', json=request,
    )

    if testcase == 'not_acceptable':
        assert response.status_code == 406
        return

    assert response.status_code == 200

    assert response.json() == load_json(f'response_{testcase}.json')

    cursor.execute(
        """
    select
      order_id,
      zone,
      point,
      point_b,
      to_char(created, 'DD Mon YYYY HH:MI:SS') as created,
      to_char(due, 'DD Mon YYYY HH:MI:SS') as due,
      matching_id,
      revision,
      allowed_classes,
      lookup,
      callback,
      user_id,
      status,
      times_matched,
      times_dispatched
    from
      combo_matcher.order_meta
    """,
    )

    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    rows = [dict(zip(colnames, row)) for row in rows]

    assert sorted(rows, key=lambda x: x['order_id']) == load_json(
        f'order_meta_{testcase}.json',
    )
