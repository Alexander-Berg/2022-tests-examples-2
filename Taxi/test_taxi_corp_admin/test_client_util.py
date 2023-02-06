MOCK_ID = 'mock_id'
DEFAULT_COST_CENTER_TEMPLATE = {  # as config.CORP_COST_CENTERS_TEMPLATES[0]
    'default': True,
    'field_settings': [
        {
            'format': 'text',
            'hidden': False,
            'id': 'cost_center',
            'required': False,
            'services': ['taxi'],
            'title': 'Цель поездки',
            'values': [],
        },
    ],
    'name': 'Основной центр затрат',
}
COST_CENTERS_CREATION_ENABLED = {
    'CORP_COST_CENTERS_NEW_CLIENTS_ENABLED': '2000-07-01T00:00:00+00:00',
}


async def check_cost_centers(db, client_id, should_exist):
    cursor = db.corp_cost_center_options.find({'client_id': client_id})
    cost_centers = await cursor.to_list(None)
    if should_exist:
        assert len(cost_centers) == 1
        cost_center = cost_centers[0]
        for key, value in DEFAULT_COST_CENTER_TEMPLATE.items():
            assert cost_center[key] == value
    else:
        assert cost_centers == []
