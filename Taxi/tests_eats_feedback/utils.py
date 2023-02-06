def load_feedbacks_table(pgsql):
    with pgsql['eats_feedback'].cursor() as cursor:
        cursor.execute(
            'SELECT id, status, comment, order_nr, order_delivery_type '
            + 'FROM eats_feedback.order_feedbacks ORDER BY id ASC',
        )
        return list(list(row) for row in cursor)
