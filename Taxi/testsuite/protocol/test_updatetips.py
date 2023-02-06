import pytest


def test_order_not_found(taxi_protocol):
    body = {
        'orderid': 'asdfasdf8c83b49edb274ce0992f337061047375',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'tips': {'type': 'percent', 'value': 0},
    }
    response = taxi_protocol.post('3.0/updatetips', json=body)
    assert response.status_code == 404


@pytest.mark.parametrize(
    'orderid, tips_type, tips_value',
    [
        ('8c83b49edb274ce0992f337061041111', 'flat', 10),
        ('8c83b49edb274ce0992f337061043333', 'percent', 5),
        ('8c83b49edb274ce0992f337061042222', 'percent', 15),
    ],
)
@pytest.mark.parametrize('use_order_core', [False, True])
def test_updatetips(
        orderid,
        tips_type,
        tips_value,
        mockserver,
        db,
        taxi_protocol,
        now,
        mock_order_core,
        use_order_core,
        config,
):
    if use_order_core:
        config.set_values(dict(PROCESSING_BACKEND_CPP_SWITCH=['update-tips']))
    request = {
        'orderid': orderid,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'tips': {'type': tips_type, 'value': tips_value},
    }
    query = {'_id': request['orderid']}
    old_proc = db.order_proc.find_one(query)
    assert old_proc is not None
    version = old_proc['order']['version']
    response = taxi_protocol.post('3.0/updatetips', request)
    assert response.status_code == 200

    if use_order_core:
        assert mock_order_core.post_event_times_called == 1
        return

    proc = db.order_proc.find_one(query)
    assert proc['processing']['need_start'] is True
    assert proc['order_info']['need_sync'] is True

    if tips_type == 'flat':
        tips_perc = 0
    else:
        tips_perc = tips_value

    assert proc['order']['creditcard']['tips']['type'] == tips_type
    assert proc['order']['creditcard']['tips']['value'] == tips_value
    assert proc['order']['creditcard']['tips_perc_default'] == tips_perc
    assert proc['order']['version'] == version + 1
    last_status_update = proc['order_info']['statistics']['status_updates'][-1]

    assert last_status_update == {
        'q': 'tips',
        'a': {
            'tips_percent': tips_perc,
            'tips_type': tips_type,
            'tips_value': tips_value,
        },
        'c': last_status_update['c'],
        'h': True,
    }


@pytest.mark.config(MAX_TIPS_BY_CURRENCY={'RUB': 100.0})
def test_overtips(taxi_protocol):
    request = {
        'orderid': '8c83b49edb274ce0992f337061041111',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'tips': {'type': 'flat', 'value': 101.0},
    }
    response = taxi_protocol.post('3.0/updatetips', request)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'tips,expected_code,expected_tips',
    [
        (
            {'type': 'percent', 'value': 0},
            200,
            {'type': 'percent', 'value': 0},
        ),
        (
            {'type': 'percent', 'decimal_value': '0'},
            200,
            {'type': 'percent', 'value': 0},
        ),
        ({'type': 'flat', 'value': 0}, 200, {'type': 'flat', 'value': 0}),
        (
            {'type': 'flat', 'decimal_value': '0'},
            200,
            {'type': 'flat', 'value': 0},
        ),
        ({'type': 'percent', 'value': 150}, 400, None),
        ({'type': 'percent', 'decimal_value': '150'}, 400, None),
        (
            {'type': 'flat', 'value': 150.23},
            200,
            {'type': 'flat', 'value': 150.23},
        ),
        (
            {'type': 'flat', 'decimal_value': '150.23'},
            200,
            {'type': 'flat', 'value': 150.23},
        ),
        ({'type': 'flat', 'decimal_value': '!!!'}, 400, None),
    ],
)
def test_updatetips_tips_parsing(
        taxi_protocol, db, tips, expected_code, expected_tips,
):
    request = {
        'orderid': '8c83b49edb274ce0992f337061041111',
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'tips': tips,
    }

    response = taxi_protocol.post('3.0/updatetips', request)

    assert response.status_code == expected_code

    if expected_code == 200:
        proc = db.order_proc.find_one({'_id': request['orderid']})
        assert proc['order']['creditcard']['tips'] == expected_tips


@pytest.mark.parametrize(
    'orderid, tips_type, tips_value',
    [
        ('8c83b49edb274ce0992f337061044444', 'flat', 10),
        ('8c83b49edb274ce0992f337061044444', 'percent', 5),
        ('8c83b49edb274ce0992f337061044444', 'percent', 15),
    ],
)
@pytest.mark.parametrize('use_order_core', [False, True])
def test_updatetips_reorder(
        orderid,
        tips_type,
        tips_value,
        mockserver,
        db,
        taxi_protocol,
        now,
        mock_order_core,
        use_order_core,
        config,
):
    if use_order_core:
        config.set_values(dict(PROCESSING_BACKEND_CPP_SWITCH=['update-tips']))
    request = {
        'orderid': orderid,
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'tips': {'type': tips_type, 'value': tips_value},
    }

    query = {'_id': orderid}
    query_reorder = {'reorder.id': orderid}

    old_proc = db.order_proc.find_one(query)
    assert old_proc is None

    old_proc_reorder = db.order_proc.find_one(query_reorder)
    assert old_proc_reorder is not None
    version_reorder = old_proc_reorder['order']['version']

    response = taxi_protocol.post('3.0/updatetips', request)
    assert response.status_code == 200

    if use_order_core:
        assert mock_order_core.post_event_times_called == 1
        return

    for q, v in zip([query_reorder], [version_reorder]):
        proc = db.order_proc.find_one(q)
        assert proc['processing']['need_start'] is True
        assert proc['order_info']['need_sync'] is True

        if tips_type == 'flat':
            tips_perc = 0
        else:
            tips_perc = tips_value

        assert proc['order']['creditcard']['tips']['type'] == tips_type
        assert proc['order']['creditcard']['tips']['value'] == tips_value
        assert proc['order']['creditcard']['tips_perc_default'] == tips_perc
        assert proc['order']['version'] == v + 1
        last_status_update = proc['order_info']['statistics'][
            'status_updates'
        ][-1]

        assert last_status_update == {
            'q': 'tips',
            'a': {
                'tips_percent': tips_perc,
                'tips_type': tips_type,
                'tips_value': tips_value,
            },
            'c': last_status_update['c'],
            'h': True,
        }
