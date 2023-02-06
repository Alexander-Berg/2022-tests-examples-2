import datetime

import pytest

_NOW_DATE = datetime.date(year=2007, month=1, day=1)

MOCK_OPERATORS = [
    {
        'id': 1,
        'login': 'operator_1',
        'yandex_uid': 'test_yandex_uid',
        'agent_id': '1000001304',
        'state': 'ready',
        'first_name': 'name',
        'last_name': 'surname',
        'callcenter_id': 'volgograd_cc',
        'roles': ['ru_disp_operator', 'ru_support_operator'],
        'roles_info': [
            {'role': 'ru_disp_operator', 'source': 'admin'},
            {'role': 'ru_support_operator', 'source': 'idm'},
        ],
        'name_in_telephony': 'operator_1',
        'created_at': '2016-06-01T22:05:25+00:00',
        'updated_at': '2016-06-22T22:05:25+00:00',
        'employment_date': _NOW_DATE.isoformat(),
    },
]

OPERATORS_ACTIONS_URL = 'operators/save_actions'


@pytest.mark.parametrize(
    ['body', 'expected_code'],
    [
        pytest.param(
            {
                'chain_id': 'chain2',
                'offer_id': 'offer2',
                'order_id': 'order2',
                'discount_card': '020',
                'base_discount': '10%',
                'call_center_discount': '20%',
                'zone_name': 'podolsk',
                'agent_id': '123',
                'yandex_uid': 'test_yandex_uid',
            },
            200,
            id='ok request',
            marks=[
                pytest.mark.pgsql(
                    'callcenter_stats',
                    files=['callcenter_stats_create_actions.sql'],
                ),
            ],
        ),
        pytest.param(
            {
                'chain_id': 'chain1',
                'offer_id': 'offer3',
                'yandex_uid': 'test_yandex_uid',
            },
            200,
            id='ok request with existing chain_id',
            marks=[
                pytest.mark.pgsql(
                    'callcenter_stats',
                    files=['callcenter_stats_create_actions.sql'],
                ),
            ],
        ),
        pytest.param({'bad_request': 'very_bad'}, 400, id='bad request'),
        pytest.param(
            {'chain_id': 'some_chain_id'}, 400, id='required offer_id missing',
        ),
    ],
)
async def test_operators_save_actions(
        taxi_callcenter_stats, body, expected_code, pgsql, mockserver,
):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list(http_request):
        return mockserver.make_response(
            status=200, json={'next_cursor': 1, 'operators': MOCK_OPERATORS},
        )

    key_to_tuple_index = dict(
        zip(
            (
                'id',
                'chain_id',
                'created_at',
                'offer_id',
                'order_id',
                'discount_card',
                'base_discount',
                'call_center_discount',
                'zone_name',
                'agent_id',
                'yandex_uid',
            ),
            range(11),
        ),
    )
    response = await taxi_callcenter_stats.post(OPERATORS_ACTIONS_URL, body)
    assert response.status_code == expected_code

    if expected_code != 200:
        assert response.json()['code'] == 'bad_action'
        return

    cursor = pgsql['callcenter_stats'].cursor()

    cursor.execute('SELECT * FROM callcenter_stats.actions')
    has_row = False
    for row in cursor:
        for key, value in body.items():
            if row[key_to_tuple_index[key]] != value:
                break
        else:
            has_row = True
    assert has_row


@pytest.mark.config(
    CALLCENTER_STATS_ACTIONS_FOR_SAVING={'actions': ['draft', 'cancel']},
)
@pytest.mark.parametrize(
    ['body', 'expected_code'],
    [
        pytest.param(
            {
                'chain_id': 'chain2',
                'order_id': 'order2',
                'agent_id': '123',
                'yandex_uid': 'test_yandex_uid',
                'action_type': 'cancel',
            },
            200,
            id='new way cancel',
        ),
        pytest.param(
            {
                'chain_id': 'chain2',
                'agent_id': '123',
                'yandex_uid': 'test_yandex_uid',
                'action_type': 'cancel',
            },
            400,
            id='new way cancel, no order',
        ),
        pytest.param(
            {
                'chain_id': 'chain2',
                'order_id': 'order2',
                'agent_id': '123',
                'yandex_uid': 'test_yandex_uid',
                'action_type': 'unknown_action',
            },
            400,
            id='new way unknown_action',
        ),
        pytest.param(
            {
                'chain_id': 'chain2',
                'offer_id': 'offer2',
                'order_id': 'order2',
                'agent_id': '123',
                'yandex_uid': 'test_yandex_uid',
                'action_type': 'draft',
            },
            200,
            id='new way draft',
        ),
    ],
)
async def test_operators_save_actions_new_way(
        taxi_callcenter_stats, body, expected_code, pgsql, mockserver,
):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list(http_request):
        return mockserver.make_response(
            status=200, json={'next_cursor': 1, 'operators': MOCK_OPERATORS},
        )

    key_to_tuple_index = dict(
        zip(
            (
                'id',
                'chain_id',
                'created_at',
                'offer_id',
                'order_id',
                'discount_card',
                'base_discount',
                'call_center_discount',
                'zone_name',
                'agent_id',
                'yandex_uid',
                'action_type',
            ),
            range(12),
        ),
    )
    response = await taxi_callcenter_stats.post(OPERATORS_ACTIONS_URL, body)
    assert response.status_code == expected_code

    if expected_code != 200:
        assert response.json()['code'] in ('bad_action', 'unknown_action')
        return

    cursor = pgsql['callcenter_stats'].cursor()

    cursor.execute('SELECT * FROM callcenter_stats.actions')
    has_row = False
    for row in cursor:
        for key, value in body.items():
            if row[key_to_tuple_index[key]] != value:
                break
        else:
            has_row = True
    assert has_row
