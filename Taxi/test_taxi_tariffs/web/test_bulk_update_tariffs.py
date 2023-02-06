import contextlib
import dataclasses
import datetime
import json

import pytest

import generated.models.taxi_approvals as taxi_approvals_module

from taxi_tariffs.api.common import approvals
from taxi_tariffs.api.common import bulk_updating_tariffs
from taxi_tariffs.generated.service.swagger.models import api

DRAFT_ID = 100


@dataclasses.dataclass
class ApprovalsRequests:
    create_draft: list = dataclasses.field(default_factory=list)
    create_multidraft: list = dataclasses.field(default_factory=list)
    list_: list = dataclasses.field(default_factory=list)


TICKETS = ['TAXIBACKEND-111']
TEST_DATA = (
    pytest.param(
        {
            'variables': [{'home_zone': 'moscow', 'first_airport': 'dme'}],
            'tickets': TICKETS,
            'deferred_apply': '2021-01-01T03:00:00+03:00',
            'updating_category_rule': {
                'category_type': 'application',
                'category_name': 'econom',
                'time_from': '00:00',
                'time_to': '23:59',
                'currency': 'RUB',
                'day_type': 2,
                'minimal': [
                    {'operator': 'ADD', 'second_operand': 1},
                    {'operator': 'MUL', 'second_operand': 2},
                ],
                'minimal_price': [{'operator': 'SET', 'second_operand': 10}],
                'paid_cancel_fix': [{'operator': 'SET', 'second_operand': 15}],
                'add_minimal_to_paid_cancel': {'new_value': False},
                'waiting_included': [
                    {'operator': 'SET', 'second_operand': 20},
                ],
                'waiting_price': [{'operator': 'SET', 'second_operand': 25}],
                'special_taximeters': [
                    {
                        'zone_name': 'suburb',
                        'price': {
                            'time_price_intervals': [
                                {
                                    'begin': 3,
                                    'price': [
                                        {
                                            'operator': 'SET',
                                            'second_operand': 10,
                                        },
                                    ],
                                },
                            ],
                            'distance_price_intervals': [
                                {
                                    'begin': 0,
                                    'price': [
                                        {
                                            'operator': 'SET',
                                            'second_operand': 20,
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ],
                'zonal_prices': [
                    {
                        'source': 'home_zone',
                        'destination': 'first_airport',
                        'route_without_jams': {'new_value': True},
                        'price': {
                            'minimal': [
                                {'operator': 'SET', 'second_operand': 150},
                            ],
                            'once': [
                                {'operator': 'SET', 'second_operand': 100},
                            ],
                            'waiting_included': [
                                {'operator': 'SET', 'second_operand': 200},
                            ],
                            'waiting_price': [
                                {'operator': 'SET', 'second_operand': 120},
                            ],
                            'time_price_intervals': [
                                {
                                    'begin': 15,
                                    'price': [
                                        {
                                            'operator': 'SET',
                                            'second_operand': 30,
                                        },
                                    ],
                                },
                            ],
                            'distance_price_intervals': [
                                {
                                    'begin': 10,
                                    'price': [
                                        {
                                            'operator': 'SET',
                                            'second_operand': 25,
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ],
                'paid_dispatch_distance_price_intervals': [
                    {
                        'begin': 0,
                        'price': [{'operator': 'SET', 'second_operand': 25}],
                        'step': [{'operator': 'SET', 'second_operand': 25}],
                    },
                ],
                'summable_requirements': [
                    {
                        'type': 'animaltransport',
                        'max_price': [
                            {'operator': 'MUL', 'second_operand': 2},
                        ],
                        'multiplier': [
                            {'operator': 'SET', 'second_operand': 20},
                        ],
                        'price': {
                            'included_time': [
                                {'operator': 'SET', 'second_operand': 10},
                            ],
                            'included_distance': [
                                {'operator': 'SET', 'second_operand': 11},
                            ],
                            'time_multiplier': [
                                {'operator': 'SET', 'second_operand': 12},
                            ],
                            'distance_multiplier': [
                                {'operator': 'SET', 'second_operand': 13},
                            ],
                        },
                    },
                ],
            },
        },
        200,
        {'multidraft_id': 1},
        id='Changing moscow tariff',
    ),
    pytest.param(
        {
            'variables': [{'home_zone': 'moscow'}],
            'tickets': TICKETS,
            'updating_category_rule': {
                'category_type': 'application',
                'category_name': 'vip',
                'time_from': '00:00',
                'time_to': '23:59',
                'currency': 'RUB',
                'day_type': 2,
                'minimal': [{'operator': 'ADD', 'second_operand': 1}],
            },
        },
        400,
        {
            'code': 'KEY_NOT_FOUND',
            'message': (
                'category key not found: '
                'CategoryKey(category_name=\'vip\', '
                'category_type=\'application\', '
                'time_from=\'00:00\', time_to=\'23:59\', '
                'day_type=2, currency=\'RUB\')'
            ),
        },
        id='Try changing not existing category in moscow',
    ),
    pytest.param(
        {
            'variables': [{'home_zone': 'moscow'}],
            'tickets': TICKETS,
            'updating_category_rule': {
                'category_type': 'application',
                'category_name': 'econom',
                'time_from': '00:00',
                'time_to': '23:59',
                'currency': 'RUB',
                'day_type': 2,
                'summable_requirements': [
                    {
                        'type': 'invalid',
                        'max_price': [
                            {'operator': 'MUL', 'second_operand': 2},
                        ],
                    },
                ],
            },
        },
        400,
        {
            'code': 'KEY_NOT_FOUND',
            'message': 'summable_requirement key not found: invalid',
        },
        id='Try changing not existing summable_requirement in moscow',
    ),
    pytest.param(
        {
            'variables': [{'home_zone': 'moscow'}],
            'tickets': TICKETS,
            'updating_category_rule': {
                'category_type': 'application',
                'category_name': 'econom',
                'time_from': '00:00',
                'time_to': '23:59',
                'currency': 'RUB',
                'day_type': 2,
                'special_taximeters': [
                    {
                        'zone_name': 'home_zone',
                        'price': {
                            'time_price_intervals': [
                                {
                                    'begin': 10,
                                    'price': [
                                        {
                                            'operator': 'MUL',
                                            'second_operand': 10,
                                        },
                                    ],
                                },
                            ],
                        },
                    },
                ],
            },
        },
        400,
        {
            'code': 'KEY_NOT_FOUND',
            'message': 'special_taximeter key not found: moscow',
        },
        id='Try changing not existing special_taximeter in moscow',
    ),
)


@pytest.fixture()
def drafts_mock(mockserver, data):
    approvals_requests = ApprovalsRequests([], [], [])

    @mockserver.json_handler('/taxi-approvals/drafts/list/')
    def _list_handler(request):
        approvals_requests.list_.append(request.json)  # pylint: disable=E1101
        return []

    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    def _create_draft_hanlder(request):
        request.json.pop('request_id')
        approvals_requests.create_draft.append(  # pylint: disable=E1101
            request.json,
        )
        return {'id': DRAFT_ID, 'version': 1}

    @mockserver.json_handler('/taxi-approvals/multidrafts/create/')
    def _create_multidraft_handler(request):
        request.json.pop('request_id')
        approvals_requests.create_multidraft.append(  # pylint: disable=E1101
            request.json,
        )
        return {'id': 1}

    return approvals_requests


@pytest.mark.parametrize('data, expected_status, expected_content', TEST_DATA)
@pytest.mark.now('2020-01-01T18:00:00+00:00')
async def test_bulk_update_tariffs(
        web_app_client,
        data,
        expected_status,
        expected_content,
        mockserver,
        open_file,
        drafts_mock,
):  # pylint: disable=W0621
    response = await web_app_client.post(
        '/v1/tariffs/bulk_change/',
        json=data,
        headers={'X-Yandex-Login': 'test'},
    )
    assert response.status == expected_status, await response.json()
    content = await response.json()
    assert content == expected_content
    if response.status != 200:
        return

    assert drafts_mock.list_ == [
        {
            'change_doc_ids': ['moscow:set_tariff'],
            'statuses': ['need_approval'],
        },
    ]
    assert drafts_mock.create_multidraft == [
        {
            'attach_drafts': [{'id': 100, 'version': 1}],
            'data': data,
            'description': 'Мультидрафт на изменение тарифов',
            'tickets': {'existed': TICKETS},
        },
    ]

    expected_create_draft = [
        {
            'api_path': 'set_tariff',
            'data': {
                'activation_zone': 'moscow_activation',
                'categories': [
                    {
                        'add_minimal_to_paid_cancel': False,
                        'category_name': 'econom',
                        'category_type': 'application',
                        'currency': 'RUB',
                        'day_type': 2,
                        'included_one_of': [],
                        'meters': [],
                        'minimal': 86,
                        'minimal_price': 10,
                        'name_key': 'interval.24h',
                        'paid_cancel_fix': 15,
                        'paid_dispatch_distance_price_intervals': [
                            {'begin': 0, 'price': 25, 'step': 25},
                        ],
                        'special_taximeters': [
                            {
                                'price': {
                                    'distance_price_intervals': [
                                        {'begin': 0, 'price': 20},
                                    ],
                                    'distance_price_intervals_meter_id': 6,
                                    'time_price_intervals': [
                                        {'begin': 3, 'price': 10},
                                    ],
                                    'time_price_intervals_meter_id': 5,
                                },
                                'zone_name': 'suburb',
                            },
                        ],
                        'summable_requirements': [
                            {
                                'max_price': 200,
                                'multiplier': 20,
                                'price': {
                                    'distance_multiplier': 13,
                                    'included_distance': 11,
                                    'included_time': 10,
                                    'time_multiplier': 12,
                                },
                                'type': 'animaltransport',
                            },
                        ],
                        'time_from': '00:00',
                        'time_to': '23:59',
                        'waiting_included': 20,
                        'waiting_price': 25,
                        'waiting_price_type': 'per_minute',
                        'zonal_prices': [
                            {
                                'destination': 'dme',
                                'price': {
                                    'distance_price_intervals': [
                                        {'begin': 10, 'price': 25},
                                    ],
                                    'distance_price_intervals_meter_id': 6,
                                    'minimal': 150,
                                    'once': 100,
                                    'time_price_intervals': [
                                        {'begin': 15, 'price': 30},
                                    ],
                                    'time_price_intervals_meter_id': 5,
                                    'waiting_included': 200,
                                    'waiting_price': 120,
                                },
                                'route_without_jams': True,
                                'source': 'moscow',
                            },
                        ],
                    },
                ],
                'date_from': '20000101T000000',
                'home_zone': 'moscow',
            },
            'mode': 'push',
            'run_manually': False,
            'service_name': 'admin',
        },
    ]
    if data.get('deferred_apply'):
        for item in expected_create_draft:
            item['deferred_apply'] = data['deferred_apply']
    assert drafts_mock.create_draft == expected_create_draft


@pytest.mark.parametrize(
    'value, rules, expected, error_context',
    (
        (None, None, None, None),
        (None, [api.UpdatingNumberRule('SET', 4)], 4, None),
        (1, [api.UpdatingNumberRule('SET', 4)], 4, None),
        (1, [api.UpdatingNumberRule('ADD', 4)], 5, None),
        (10, [api.UpdatingNumberRule('SUB', 4)], 6, None),
        (2, [api.UpdatingNumberRule('MUL', 4)], 8, None),
        (8, [api.UpdatingNumberRule('DIV', 4)], 2, None),
        (
            0,
            [
                api.UpdatingNumberRule('ADD', 2),
                api.UpdatingNumberRule('MUL', 4),
            ],
            8,
            None,
        ),
        (
            None,
            [api.UpdatingNumberRule('DIV', 4)],
            2,
            pytest.raises(
                bulk_updating_tariffs.UpdatingTariffFailed,
                match='FIELD_IS_NONE',
            ),
        ),
    ),
)
async def test_update_number(value, rules, expected, error_context):
    error_context = error_context or contextlib.nullcontext()
    with error_context:
        assert (
            bulk_updating_tariffs.update_optional_number(value, rules)
            == expected
        )


@pytest.mark.parametrize(
    'value, rules, expected, error_context',
    (
        (
            [api.TariffInterval(begin=0, price=10, end=1)],
            [
                api.UpdatingTariffIntervalRule(
                    0, 1, [api.UpdatingNumberRule('ADD', 10)],
                ),
            ],
            [api.TariffInterval(begin=0, price=20, end=1)],
            None,
        ),
        (
            [api.TariffInterval(begin=0, price=10, end=1, step=1)],
            [
                api.UpdatingTariffIntervalRule(
                    0, 1, None, [api.UpdatingNumberRule('ADD', 10)],
                ),
            ],
            [api.TariffInterval(begin=0, price=10, end=1, step=11)],
            None,
        ),
        (
            [],
            [
                api.UpdatingTariffIntervalRule(
                    0, 1, [api.UpdatingNumberRule('DIV', 4)],
                ),
            ],
            [],
            pytest.raises(
                bulk_updating_tariffs.UpdatingTariffFailed,
                match='KEY_NOT_FOUND',
            ),
        ),
    ),
)
async def test_update_intervals(value, rules, expected, error_context):
    error_context = error_context or contextlib.nullcontext()
    with error_context:
        bulk_updating_tariffs.update_intervals(value, rules, 'test')
        assert repr(value) == repr(expected)  # api classes does not have ==


@pytest.mark.config(
    APPROVALS_CLIENT_QOS={'__default__': {'attempts': 1, 'timeout-ms': 500}},
)
async def test_create_tariff_drafts(web_context, mockserver):
    spb = 'spb'
    moscow = 'moscow'
    draft_id = 10

    @mockserver.handler('/taxi-approvals/drafts/create/')
    def create_draft_handler(request):
        if request.json['data']['home_zone'] == spb:
            return mockserver.make_response(
                'Internal Server Error', status=500,
            )
        return mockserver.make_response(
            json.dumps({'id': draft_id, 'version': 1}), status=200,
        )

    @mockserver.json_handler(f'/taxi-approvals/drafts/{draft_id}/')
    def delete_draft_handler(request):
        return {}

    tariffs = [
        {'home_zone': moscow, 'date_from': datetime.datetime.utcnow()},
        {'home_zone': spb, 'date_from': datetime.datetime.utcnow()},
    ]
    with pytest.raises(
            approvals.CreatingDraftFailed, match='CREATING_DRAFT_FAILED',
    ):
        await approvals.create_tariff_drafts(
            tariffs, 'test', None, web_context,
        )
    assert create_draft_handler.times_called == 2
    assert delete_draft_handler.times_called == 1


async def test_create_tariff_multidraft(web_context, mockserver):
    draft_ids = [1, 2, 3]

    @mockserver.json_handler(f'/taxi-approvals/drafts/', prefix=True)
    def delete_draft_handler(request):
        return {}

    with pytest.raises(
            approvals.CreatingDraftFailed, match='CREATING_MULTIDRAFT_FAILED',
    ):
        await approvals.create_multidraft(
            'test_description',
            [
                taxi_approvals_module.AttachedDraftsItem(draft_id, 1)
                for draft_id in draft_ids
            ],
            {'tickets': TICKETS},
            'test_robot',
            web_context,
        )
    assert delete_draft_handler.times_called == len(draft_ids)
