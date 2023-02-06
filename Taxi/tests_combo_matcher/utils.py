def get_orders_in_database(pgsql):
    cursor = pgsql['combo_matcher'].cursor()
    cursor.execute('SELECT * from combo_matcher.order_meta')
    return sorted([row for row in cursor])


async def select_matchings(pgsql, with_combo_info=False):
    cursor = pgsql['combo_matcher'].cursor()
    columns = ['id', 'orders', 'performer']
    if with_combo_info:
        columns.append('combo_info')
    cursor.execute(
        f"""
        select
          {','.join(columns)}
        from
          combo_matcher.matchings
        """,
    )
    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(colnames, row)) for row in rows]


async def select_order_meta(pgsql):
    cursor = pgsql['combo_matcher'].cursor()
    cursor.execute(
        """
        select
          order_id,
          matching_id,
          status,
          revision,
          candidate,
          times_matched,
          times_dispatched
        from
          combo_matcher.order_meta
        """,
    )
    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(colnames, row)) for row in rows]


async def select_order_ids(pgsql):
    cursor = pgsql['combo_matcher'].cursor()
    cursor.execute(
        """
        select
          order_id
        from
          combo_matcher.order_meta
        """,
    )
    return sorted([row[0] for row in cursor])
