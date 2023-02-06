EATS_COURIER_SCORING_STARTREK_SETTINGS_BY_REGION = {
    '__default__': {
        'assignee': 'ameshik',
        'followers': [],
        'queue': 'EDACOURIERBAN',
        'defect_descriptions': [
            {
                'defect_type': 'cancel_delay',
                'tanker_key': 'defect_descriptions.cancel_delay',
            },
            {
                'defect_type': 'cancel_not_connected_with_courier',
                'tanker_key': (
                    'defect_descriptions.cancel_not_connected_with_courier'
                ),
            },
            {
                'defect_type': 'cancel_postpayment',
                'tanker_key': 'defect_descriptions.cancel_postpayment',
            },
            {
                'defect_type': 'courier_denial',
                'tanker_key': 'defect_descriptions.courier_denial',
            },
            {
                'defect_type': 'covid_fault',
                'tanker_key': 'defect_descriptions.covid_fault',
            },
            {
                'defect_type': 'damaged_order',
                'tanker_key': 'defect_descriptions.damaged_order',
            },
            {
                'defect_type': 'delay_short',
                'tanker_key': 'defect_descriptions.delay_short',
            },
            {
                'defect_type': 'equipment_fault',
                'tanker_key': 'defect_descriptions.equipment_fault',
            },
            {
                'defect_type': 'force_majeure',
                'tanker_key': 'defect_descriptions.force_majeure',
            },
            {
                'defect_type': 'frod_last_status',
                'tanker_key': 'defect_descriptions.frod_last_status',
            },
            {
                'defect_type': 'frod_not_delivered',
                'tanker_key': 'defect_descriptions.frod_not_delivered',
            },
            {
                'defect_type': 'frod_waiting_time',
                'tanker_key': 'defect_descriptions.frod_waiting_time',
            },
            {
                'defect_type': 'incorrect_status_contact',
                'tanker_key': 'defect_descriptions.incorrect_status_contact',
            },
            {
                'defect_type': 'irrelevant_contact_waiting',
                'tanker_key': 'defect_descriptions.irrelevant_contact_waiting',
            },
            {
                'defect_type': 'mismatch_orders',
                'tanker_key': 'defect_descriptions.mismatch_orders',
            },
            {
                'defect_type': 'missed_comment',
                'tanker_key': 'defect_descriptions.missed_comment',
            },
            {
                'defect_type': 'order_item_lost',
                'tanker_key': 'defect_descriptions.order_item_lost',
            },
            {'defect_type': 'rude', 'tanker_key': 'defect_descriptions.rude'},
            {
                'defect_type': 'taxi_contact',
                'tanker_key': 'defect_descriptions.taxi_contact',
            },
            {
                'defect_type': 'tips_annoying',
                'tanker_key': 'defect_descriptions.tips_annoying',
            },
            {
                'defect_type': 'vehicle_change_contact',
                'tanker_key': 'defect_descriptions.vehicle_change_contact',
            },
        ],
    },
}

EATS_COURIER_SCORING_DEFECT_TYPES = {
    'defect_types': [
        'cancel_delay',
        'cancel_not_connected_with_courier',
        'cancel_postpayment',
        'courier_denial',
        'covid_fault',
        'damaged_order',
        'delay_short',
        'fake_gps',
        'equipment_fault',
        'force_majeure',
        'frod_last_status',
        'frod_not_delivered',
        'frod_waiting_time',
        'incorrect_status_contact',
        'irrelevant_contact_waiting',
        'long_in_rest',
        'mismatch_orders',
        'missed_comment',
        'order_item_lost',
        'rude',
        'taxi_contact',
        'tips_annoying',
        'vehicle_change_contact',
        'antilaw_courier',
        'bad_courier',
        'delay',
        'long_in_rest_qsr',
        'new_defect',
    ],
}

CONFIG_DEFECT_SCORES = [
    {'defect_type': 'antilaw_courier', 'scores': [{'score': 0}]},
    {'defect_type': 'bad_courier', 'scores': [{'score': 0}]},
    {
        'defect_type': 'cancel_delay',
        'scores': [
            {
                'score': 7.5,
                'thresholds_absolute': {'from': 2},
                'thresholds_share': {'from': 0.05},
            },
            {'score': 5},
        ],
    },
    {
        'defect_type': 'cancel_not_connected_with_courier',
        'scores': [
            {
                'score': 7.5,
                'thresholds_absolute': {'from': 2},
                'thresholds_share': {'from': 0.05},
            },
            {'score': 5},
        ],
    },
    {'defect_type': 'courier_denial', 'scores': [{'score': 0}]},
    {
        'defect_type': 'damaged_order',
        'scores': [
            {
                'score': 7.5,
                'thresholds_absolute': {'from': 3},
                'thresholds_share': {'from': 0.04},
            },
            {'score': 5},
        ],
    },
    {'defect_type': 'delay', 'scores': [{'score': 0}]},
    {'defect_type': 'frod_last_status', 'scores': [{'score': 0}]},
    {
        'defect_type': 'frod_not_delivered',
        'scores': [
            {
                'score': 7.5,
                'thresholds_absolute': {'from': 2},
                'thresholds_share': {'from': 0.03},
            },
            {'score': 5},
        ],
    },
    {'defect_type': 'frod_waiting_time', 'scores': [{'score': 0}]},
    {'defect_type': 'long_in_rest_qsr', 'scores': [{'score': 0}]},
]
