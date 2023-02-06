from projects.support.rules_compiler import config_utils


def test_utils(load_json):
    dump = load_json('dump_example.json')
    macro2freq = {}
    config = config_utils.get_rules_config(dump, macro2freq)

    assert 'dr_drivers_document_requirements' in config
    assert 'dr_account_update_driver_info_name' in config
    assert 'dr_complaint_irt_altercation' in config
    assert 'dr_payment_review_taxometr_balance_withdrawal' in config
    assert 'dr_info_account' in config

    assert not config['dr_drivers_document_requirements']
    assert not config['dr_account_update_driver_info_name']
    assert not config['dr_info_account']

    assert config['dr_complaint_irt_altercation'] == [
        {
            'actions': [{'action': 'dismiss', 'arguments': {}}],
            'frequency': 1,
            'status': 'not_reply',
            'rules': ['success_order_flg is true and final_ride_duration < 2'],
        },
    ]

    assert config['dr_payment_review_taxometr_balance_withdrawal'] == [
        {
            'actions': [
                {'action': 'close', 'arguments': {'macro_id': 173552}},
            ],
            'frequency': 1,
            'status': 'ok',
            'rules': [
                'success_order_flg is true and tariff != \'cruise\' '
                'and tariff != \'minivan\' and tariff != \'ubervan\'',
            ],
        },
        {
            'actions': [
                {
                    'action': 'suggest_forward',
                    'arguments': {'line': 'accounts'},
                },
                {'action': 'comment', 'arguments': {'macro_id': 173549}},
            ],
            'frequency': 1,
            'status': 'waiting',
            'rules': ['success_order_flg is true'],
        },
    ]
