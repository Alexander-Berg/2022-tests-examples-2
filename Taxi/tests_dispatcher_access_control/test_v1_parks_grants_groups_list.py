import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/grants/groups/list'

OK_REQUEST_NO_GROUPS = {'query': {'park': {'id': 'park_valid1'}}}

OK_REQUEST_WITH_GROUPS_1_2 = {
    'query': {'park': {'id': 'park_valid1', 'group': {'ids': ['1', '2']}}},
}

OK_REQUEST_INVALID_GROUP = {
    'query': {
        'park': {
            'id': 'park_valid1',
            'group': {'ids': ['1', '2', 'group_invalid']},
        },
    },
}

BAD_REQUEST_INVALID_GROUP = {
    'query': {
        'park': {'id': 'park_valid1', 'group': {'ids': ['group_invalid']}},
    },
}

BAD_REQUEST_DUPLICATE_GROUPS = {
    'query': {'park': {'id': 'park_valid1', 'group': {'ids': ['1', '1']}}},
}

BAD_REQUEST_INVALID_PARK = {'query': {'park': {'id': 'park_invalid'}}}

MARKETPLACE = {
    'enable': False,
    'cities': [],
    'countries': [],
    'dbs': [],
    'home_url': '',
}

TEST_PARAMS = [
    (
        OK_REQUEST_NO_GROUPS,
        MARKETPLACE,
        200,
        {
            'groups': [
                {
                    'group_id': '1',
                    'grants': [
                        utils.make_grant('driver_read_common'),
                        utils.make_grant('driver_write_common'),
                    ],
                },
                {
                    'group_id': '2',
                    'grants': [
                        utils.make_grant('car_read_common'),
                        utils.make_grant('car_write_common'),
                    ],
                },
                {
                    'group_id': '3',
                    'grants': [utils.make_grant('support_chat_read')],
                },
                {
                    'group_id': '4',
                    'grants': [utils.make_grant('recurring_payments_read')],
                },
            ],
        },
    ),
    (
        OK_REQUEST_WITH_GROUPS_1_2,
        MARKETPLACE,
        200,
        {
            'groups': [
                {
                    'group_id': '2',
                    'grants': [
                        utils.make_grant('car_read_common'),
                        utils.make_grant('car_write_common'),
                    ],
                },
                {
                    'group_id': '1',
                    'grants': [
                        utils.make_grant('driver_read_common'),
                        utils.make_grant('driver_write_common'),
                    ],
                },
            ],
        },
    ),
    (
        OK_REQUEST_INVALID_GROUP,
        MARKETPLACE,
        200,
        {
            'groups': [
                {
                    'group_id': '2',
                    'grants': [
                        utils.make_grant('car_read_common'),
                        utils.make_grant('car_write_common'),
                    ],
                },
                {
                    'group_id': '1',
                    'grants': [
                        utils.make_grant('driver_read_common'),
                        utils.make_grant('driver_write_common'),
                    ],
                },
            ],
        },
    ),
    (BAD_REQUEST_INVALID_GROUP, MARKETPLACE, 200, {'groups': []}),
    (
        BAD_REQUEST_INVALID_PARK,
        MARKETPLACE,
        400,
        {'code': '400', 'message': 'Park not found'},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {'Name': 'Name1', 'Group': '1', 'YandexUid': '100'},
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'2': json.dumps({'Name': 'Group2'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'3': json.dumps({'Name': 'Group3'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'4': json.dumps({'Name': 'Group4'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:1',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '12',
                        '13',
                        '21',
                        '22',
                        '23',
                        '24',
                        '32',
                        '33',
                        '41',
                        '42',
                        '43',
                        '53',
                        '55',
                        '56',
                        'parks',
                        'cashbox',
                        'carriers',
                        '61',
                        '71',
                        '72',
                        '75',
                        '76',
                        '77',
                        'recurringPayments',
                        'supportChats',
                        'segments',
                        '82',
                        '44',
                        'map',
                    ],
                },
            ),
            'Driver': json.dumps(
                {
                    'tabtaximeter': True,
                    'tabbalance': True,
                    'tabstatus': True,
                    'tabgps': True,
                    'tabrating': True,
                    'tabrobot': True,
                    'tabhistory': True,
                    'tabcomplaints': True,
                    'tabdocuments': True,
                    'tabrecords': True,
                    'tabaccess': True,
                    'tabcheckcar': True,
                    'disableLimit': True,
                    'disableFIO': True,
                    'disableLicense': True,
                    'disablePriority': True,
                    'disablePhone': True,
                    'disableAlhoritm': True,
                    'disableChangeCar': True,
                    'disableChangeStatus': True,
                    'disableProvider': True,
                    'disableRobot': True,
                    'disableBalancePlus': True,
                    'disableBalanceMinus': True,
                    'disableDocumentAdd': True,
                    'disableDocumentDelete': True,
                    'disableScoringRead': True,
                },
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:2',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '12',
                        '13',
                        '21',
                        '22',
                        '23',
                        '24',
                        '32',
                        '33',
                        '41',
                        '42',
                        '43',
                        '52',
                        '53',
                        '56',
                        'parks',
                        'cashbox',
                        'carriers',
                        '61',
                        '71',
                        '72',
                        '75',
                        '76',
                        '77',
                        'recurringPayments',
                        'supportChats',
                        'segments',
                        '82',
                        '44',
                        'map',
                    ],
                },
            ),
            'Car': json.dumps({'tabdrivers': True, 'tabdocuments': True}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:3',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '12',
                        '13',
                        '21',
                        '22',
                        '23',
                        '24',
                        '32',
                        '33',
                        '41',
                        '42',
                        '43',
                        '52',
                        '53',
                        '55',
                        '56',
                        'parks',
                        'cashbox',
                        'carriers',
                        '61',
                        '71',
                        '72',
                        '75',
                        '76',
                        '77',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'recurringPayments',
                    ],
                },
            ),
            'SupportChat': json.dumps({'disableEdit': True}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:4',
        {
            'Menu': json.dumps(
                {
                    'hideMenu': [
                        '12',
                        '13',
                        '21',
                        '22',
                        '23',
                        '24',
                        '32',
                        '33',
                        '41',
                        '42',
                        '43',
                        '52',
                        '53',
                        '55',
                        '56',
                        'parks',
                        'cashbox',
                        'carriers',
                        '61',
                        '71',
                        '72',
                        '75',
                        '76',
                        '77',
                        'segments',
                        '82',
                        '44',
                        'map',
                        'supportChats',
                    ],
                },
            ),
            'RecurringPayments': json.dumps({'disableEdit': True}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Grants:park_valid1:4',
        {'invalid_grant_1': str(True), 'invalid_grant_2': str(False)},
    ],
)
@pytest.mark.parametrize(
    'payload, marketplace, code, expected_response', TEST_PARAMS,
)
async def test_get_grants(
        taxi_dispatcher_access_control,
        taxi_config,
        mock_fleet_parks_list,
        payload,
        marketplace,
        code,
        expected_response,
):
    taxi_config.set_values(dict(TAXIMETER_MARKETPLACE=marketplace))
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=payload,
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == code
    assert response.json() == expected_response
