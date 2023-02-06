def test_events_eda_signature_base(taxi_antifraud, db):
    params = [
        [
            {'uid': 'uid1', 'signature': 'signature1'},
            {'frauder': False, 'proc_status': 'parse_failed'},
        ],
        [
            {'uid': 'uid2', 'signature': 'signature2'},
            {
                'frauder': True,
                'proc_status': 'parse_failed',
                'rule_id': 'test_rule1',
            },
        ],
    ]

    response = taxi_antifraud.post(
        'v1/events/eda/signature', json={'couriers': [p[0] for p in params]},
    )
    assert 200 == response.status_code
    assert {} == response.json()

    for p in params:
        record = db.antifraud_courier_client_info.find_one(
            {'_id': p[0]['uid']},
            {
                '_id': False,
                'frauder': True,
                'proc_status': True,
                'rule_id': True,
            },
        )
        assert record == p[1]
