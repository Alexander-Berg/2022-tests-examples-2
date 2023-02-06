async def check_order_flow(pgsql, idempotency_key, is_set, status=None):
    with pgsql['eats_order_integration'].dict_cursor() as cursor:
        cursor.execute(
            f'SELECT * FROM order_flow'
            f' WHERE idempotency_key = \'{idempotency_key}\'',
        )
        actual_data = [row for row in cursor]

    if is_set:
        assert len(actual_data) == 1
        actual_elem = actual_data[0]
        print(actual_elem['status'], status)
        assert actual_elem['status'] == status
    else:
        assert not actual_data


def check_fallback_to_core(stq_mock, **kwargs):
    call_args = stq_mock.next_call()
    print(call_args['kwargs'])
    print(kwargs)
    assert call_args['kwargs'] == kwargs
