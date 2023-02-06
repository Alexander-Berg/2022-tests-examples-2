import datetime

import pytest

from taxi.util import dates

from test_workforce_management.web import util as test_util
from workforce_management.common import utils


URI = 'v1/operators/forecast/values'
V2_RECALCULATE_URI = 'v2/operators/forecast/calculate-operators'
CALCULATION_URI = 'v1/operators/forecast/calculations/values'
DELETE_URI = 'v1/operators/forecast/calculations/delete'
START_DATE = '27-02-2020'
HEADERS = {'X-WFM-Domain': 'taxi'}


def parse_and_make_step(provided_datetime: str, hours: int = 0, days: int = 0):
    return dates.localize(
        dates.parse_timestring(provided_datetime, 'UTC')
        + datetime.timedelta(hours=hours, days=days),
    )


def get_records(*ids, index=0):
    return [
        {
            'base_value': 200.0 + index,
            'plan_value': 200.0 + index,
            'id': id_,
            'lower_value': 100.0 + index,
            'record_target': parse_and_make_step(
                START_DATE, ((id_ - 1) % 10) + index, days=index,
            ).isoformat(),
            'upper_value': 1000.0 + index,
        }
        for id_ in ids
    ]


@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        (
            {},
            200,
            [
                {
                    'entity_target': '2020-02-27T03:00:00+03:00',
                    'description': 'description',
                    'forecast_type': 'hourly',
                    'id': 1,
                    'name': 'Forecast 0',
                    'source': 'auto',
                    'records': get_records(*range(1, 11)),
                    'skill': 'not_a_skill',
                    'value_type': 'calls',
                },
                {
                    'entity_target': '2020-02-28T03:00:00+03:00',
                    'description': 'description',
                    'forecast_type': 'hourly',
                    'source': 'auto',
                    'name': 'Forecast 1',
                    'id': 2,
                    'records': get_records(*range(11, 21), index=1),
                    'skill': 'skill',
                    'value_type': 'calls',
                },
            ],
        ),
        (
            {
                'record_filter': {
                    'target_from': '2020-02-27T04:00:00+03:00',
                    'target_to': '2020-02-27T06:00:00+03:00',
                },
            },
            200,
            [
                {
                    'entity_target': '2020-02-27T03:00:00+03:00',
                    'description': 'description',
                    'forecast_type': 'hourly',
                    'name': 'Forecast 0',
                    'id': 1,
                    'source': 'auto',
                    'records': get_records(2, 3),
                    'skill': 'not_a_skill',
                    'value_type': 'calls',
                },
            ],
        ),
        (
            {
                'entity_filter': {'skill': 'skill'},
                'record_filter': {'target_to': '2020-02-28T06:00:00+03:00'},
            },
            200,
            [
                {
                    'entity_target': '2020-02-28T03:00:00+03:00',
                    'forecast_type': 'hourly',
                    'description': 'description',
                    'name': 'Forecast 1',
                    'id': 2,
                    'records': get_records(11, 12, index=1),
                    'skill': 'skill',
                    'source': 'auto',
                    'value_type': 'calls',
                },
            ],
        ),
        ({'entity_filter': {'skill': 'skill', 'source': 'custom'}}, 200, []),
        (
            {'entity_filter': {'id': 1}},
            200,
            [
                {
                    'entity_target': '2020-02-27T03:00:00+03:00',
                    'forecast_type': 'hourly',
                    'description': 'description',
                    'name': 'Forecast 0',
                    'id': 1,
                    'records': get_records(*range(1, 11)),
                    'skill': 'not_a_skill',
                    'source': 'auto',
                    'value_type': 'calls',
                },
            ],
        ),
        (
            {
                'entity_filter': {
                    'target_from': '2020-02-28T03:00:00+03:00',
                    'target_to': '2020-02-28T01:00:00+03:00',
                },
            },
            400,
            None,
        ),
    ],
)
async def test_forecast_base(
        taxi_workforce_management_web,
        web_context,
        fill_forecast_values,
        tst_request,
        expected_status,
        expected_res,
):
    await fill_forecast_values()
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()

    assert (
        test_util.exclude_revision(data['forecast_entities']) == expected_res
    )


def _get_final_values(data):
    return [record.get('final_value') for record in data['records']]


async def test_forecast_recalculate(
        taxi_workforce_management_web, web_context, fill_forecast_values,
):
    revisions = await fill_forecast_values()
    revision_id = utils.serialize_date_revision(revisions[0]['updated_at'])

    default_settings = {
        'sla': 0.95,
        'average_handle_time': 54,
        'service_time': 4,
        'absence_periods_percentage': [
            {'hour_from': 0, 'hour_to': 9, 'value': 0.05},
            {'hour_from': 23, 'hour_to': 6, 'value': 0.08},
        ],
        'break_percentage': 0.08,
    }

    res = await taxi_workforce_management_web.post(
        V2_RECALCULATE_URI,
        json={
            'forecast_id': 1,
            'revision_id': '2020',
            'periods': [{'settings': default_settings}],
        },
        headers=HEADERS,
    )
    assert res.status == 400

    async def check_settings(
            settings, values, record_target_from=None, record_target_to=None,
    ):
        nonlocal revision_id
        json_settings = default_settings.copy()
        json_settings.update(settings)

        period = {'calculation_id': 1, 'settings': json_settings}
        if record_target_from:
            period['record_target_from'] = record_target_from
        if record_target_to:
            period['record_target_to'] = record_target_to

        json_request = {
            'forecast_id': 1,
            'revision_id': revision_id,
            'periods': [period],
        }

        res = await taxi_workforce_management_web.post(
            V2_RECALCULATE_URI, json=json_request, headers=HEADERS,
        )
        assert res.status == 200
        revision_json = await res.json()

        res = await taxi_workforce_management_web.post(
            URI, json={'entity_filter': {'id': 1}}, headers=HEADERS,
        )
        json = await res.json()

        assert _get_final_values(json['forecast_entities'][0]) == values

        revision_id = revision_json['new_revision_id']

    await check_settings({}, [7.0] * 10)
    await check_settings({'sla': 0.5}, [4.0] * 10)
    await check_settings(
        {
            'sla': 0.98,
            'absence_periods_percentage': [
                {'hour_from': 1, 'hour_to': 3, 'value': 0.5},
            ],
        },
        [8.0, 12.0, 12.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0],
    )
    await check_settings(
        {'sla': 0.98, 'service_time': 1},
        [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 8.0],
    )
    await check_settings({'sla': 0.8, 'average_handle_time': 20}, [3.0] * 10)
    await check_settings(
        {'sla': 0.8, 'average_handle_time': 20, 'average_sessions_count': 2},
        [1.0] * 10,
    )
    await check_settings(
        {'sla': 1, 'average_handle_time': 20},
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.0, 9.0, 8.0],
        record_target_from='2020-02-27T10:00:00+03:00',
    )
    await check_settings(
        {'sla': 1, 'average_handle_time': 60},
        [0.0, 0.0, 0.0, 0.0, 0.0, 15.0, 15.0, 15.0, 0.0, 0.0],
        record_target_from='2020-02-27T08:00:00+03:00',
        record_target_to='2020-02-27T11:00:00+03:00',
    )

    res = await taxi_workforce_management_web.post(
        URI, json={'entity_filter': {'forecast_id': 1}}, headers=HEADERS,
    )
    json = await res.json()

    for row in json['forecast_entities'][0]['records'][1:3]:
        row['plan_value'] *= 2

    res = await taxi_workforce_management_web.post(
        'v1/operators/forecast/modify',
        json={
            'forecast_entity': json['forecast_entities'][0],
            'mode': 'modify',
        },
        headers=HEADERS,
    )

    assert res.status == 200
    res = await res.json()
    revision_id = res['new_revision_id']
    await check_settings(
        {'sla': 0.98, 'service_time': 1},
        [9.0, 14.0, 14.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 8.0],
    )


async def test_v2_forecast_recalculate(
        taxi_workforce_management_web, web_context, fill_forecast_values,
):
    revisions = await fill_forecast_values()
    calculation_id = None
    revision_id = utils.serialize_date_revision(revisions[0]['updated_at'])

    default_settings = {
        'sla': 0.95,
        'average_handle_time': 54,
        'service_time': 4,
        'absence_periods_percentage': [
            {'hour_from': 0, 'hour_to': 9, 'value': 0.05},
            {'hour_from': 23, 'hour_to': 6, 'value': 0.08},
        ],
        'break_percentage': 0.08,
    }

    res = await taxi_workforce_management_web.post(
        V2_RECALCULATE_URI,
        json={
            'forecast_id': 1,
            'revision_id': '2020',
            'periods': [{'settings': default_settings}],
        },
        headers=HEADERS,
    )
    assert res.status == 400

    async def check_settings(
            settings, values, record_target_from=None, record_target_to=None,
    ):
        nonlocal revision_id
        nonlocal calculation_id
        json_settings = default_settings.copy()
        json_settings.update(settings)
        json_request = {'forecast_id': 1, 'revision_id': revision_id}
        period = {'settings': json_settings}
        if calculation_id:
            period['calculation_id'] = calculation_id
        if record_target_from:
            period['record_target_from'] = record_target_from
        if record_target_to:
            period['record_target_to'] = record_target_to
        json_request['periods'] = [period]
        res = await taxi_workforce_management_web.post(
            V2_RECALCULATE_URI, json=json_request, headers=HEADERS,
        )
        assert res.status == 200
        revision_json = await res.json()

        res = await taxi_workforce_management_web.post(
            URI, json={'entity_filter': {'forecast_id': 1}}, headers=HEADERS,
        )
        json = await res.json()

        assert _get_final_values(json['forecast_entities'][0]) == values

        revision_id = revision_json['new_revision_id']

    await check_settings({}, [7.0] * 10)

    res = await taxi_workforce_management_web.post(
        CALCULATION_URI, json={'forecast_id': 1}, headers=HEADERS,
    )
    json = await res.json()
    calculation_id = json['calculations'][0]['id']

    await check_settings({'sla': 0.5}, [4.0] * 10)
    await check_settings(
        {
            'sla': 0.98,
            'absence_periods_percentage': [
                {'hour_from': 1, 'hour_to': 3, 'value': 0.5},
            ],
        },
        [8.0, 12.0, 12.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0],
    )
    await check_settings(
        {'sla': 0.98, 'service_time': 1},
        [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 8.0],
    )
    await check_settings({'sla': 0.8, 'average_handle_time': 20}, [3.0] * 10)
    await check_settings(
        {'sla': 1, 'average_handle_time': 20},
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 9.0, 9.0, 8.0],
        record_target_from='2020-02-27T10:00:00+03:00',
    )
    await check_settings(
        {'sla': 1, 'average_handle_time': 60},
        [0.0, 0.0, 0.0, 0.0, 0.0, 15.0, 15.0, 15.0, 0.0, 0.0],
        record_target_from='2020-02-27T08:00:00+03:00',
        record_target_to='2020-02-27T11:00:00+03:00',
    )

    res = await taxi_workforce_management_web.post(
        URI, json={'entity_filter': {'forecast_id': 1}}, headers=HEADERS,
    )
    json = await res.json()

    for row in json['forecast_entities'][0]['records'][1:3]:
        row['plan_value'] *= 2

    res = await taxi_workforce_management_web.post(
        'v1/operators/forecast/modify',
        json={
            'forecast_entity': json['forecast_entities'][0],
            'mode': 'modify',
        },
        headers=HEADERS,
    )

    assert res.status == 200
    res = await res.json()
    revision_id = res['new_revision_id']
    await check_settings(
        {'sla': 0.98, 'service_time': 1},
        [9.0, 14.0, 14.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 8.0],
    )


@pytest.mark.parametrize(
    'dates_to_calculate, result, status, values_after_deleting_first',
    (
        pytest.param(
            [
                ('2020-02-27T08:00:00+03:00', '2020-02-27T09:00:00+03:00'),
                ('2020-02-27T09:00:00+03:00', '2020-02-27T11:00:00+03:00'),
            ],
            [
                {
                    'forecast_id': 1,
                    'id': 1,
                    'record_target_from': '2020-02-27T08:00:00+03:00',
                    'record_target_to': '2020-02-27T09:00:00+03:00',
                    'settings': {
                        'absence_periods_percentage': [
                            {'hour_from': 0, 'hour_to': 9, 'value': 0.05},
                            {'hour_from': 23, 'hour_to': 6, 'value': 0.08},
                        ],
                        'average_handle_time': 54,
                        'average_sessions_count': 1,
                        'break_percentage': 0.08,
                        'service_time': 4,
                        'sla': 0.95,
                    },
                },
                {
                    'forecast_id': 1,
                    'id': 2,
                    'record_target_from': '2020-02-27T09:00:00+03:00',
                    'record_target_to': '2020-02-27T11:00:00+03:00',
                    'settings': {
                        'absence_periods_percentage': [
                            {'hour_from': 0, 'hour_to': 9, 'value': 0.05},
                            {'hour_from': 23, 'hour_to': 6, 'value': 0.08},
                        ],
                        'average_handle_time': 54,
                        'average_sessions_count': 1,
                        'break_percentage': 0.08,
                        'service_time': 4,
                        'sla': 0.95,
                    },
                },
            ],
            200,
            [None, None, None, None, None, 0.0, 7.0, 7.0, None, None],
            id='successful_calculation',
        ),
        pytest.param(
            [
                (None, None),
                ('2020-02-27T09:00:00+03:00', '2020-02-27T11:00:00+03:00'),
            ],
            [],
            400,
            [],
            id='two_calculation_cross_each_other',
        ),
        pytest.param(
            [
                ('2020-02-27T03:00:00+03:00', '2020-02-27T04:00:00+03:00'),
                ('2020-02-27T04:00:00+03:00', '2020-02-27T05:00:00+03:00'),
                ('2020-02-29T09:00:00+03:00', '2020-02-29T11:00:00+03:00'),
            ],
            [],
            400,
            [],
            id='calculation_beyond_of_forecast',
        ),
        pytest.param(
            [
                ('2020-02-27T03:00:00+03:00', '2020-02-27T04:00:00+03:00'),
                ('2020-02-27T04:00:00+03:00', '2020-02-27T05:00:00+03:00'),
                ('2020-02-27T05:00:00+03:00', '2020-02-27T06:00:00+03:00'),
            ],
            [
                {
                    'forecast_id': 1,
                    'id': 1,
                    'record_target_from': '2020-02-27T03:00:00+03:00',
                    'record_target_to': '2020-02-27T04:00:00+03:00',
                    'settings': {
                        'absence_periods_percentage': [
                            {'hour_from': 0, 'hour_to': 9, 'value': 0.05},
                            {'hour_from': 23, 'hour_to': 6, 'value': 0.08},
                        ],
                        'average_handle_time': 54,
                        'average_sessions_count': 1,
                        'break_percentage': 0.08,
                        'service_time': 4,
                        'sla': 0.95,
                    },
                },
                {
                    'forecast_id': 1,
                    'id': 2,
                    'record_target_from': '2020-02-27T04:00:00+03:00',
                    'record_target_to': '2020-02-27T05:00:00+03:00',
                    'settings': {
                        'absence_periods_percentage': [
                            {'hour_from': 0, 'hour_to': 9, 'value': 0.05},
                            {'hour_from': 23, 'hour_to': 6, 'value': 0.08},
                        ],
                        'average_handle_time': 54,
                        'average_sessions_count': 1,
                        'break_percentage': 0.08,
                        'service_time': 4,
                        'sla': 0.95,
                    },
                },
                {
                    'forecast_id': 1,
                    'id': 3,
                    'record_target_from': '2020-02-27T05:00:00+03:00',
                    'record_target_to': '2020-02-27T06:00:00+03:00',
                    'settings': {
                        'absence_periods_percentage': [
                            {'hour_from': 0, 'hour_to': 9, 'value': 0.05},
                            {'hour_from': 23, 'hour_to': 6, 'value': 0.08},
                        ],
                        'average_handle_time': 54,
                        'average_sessions_count': 1,
                        'break_percentage': 0.08,
                        'service_time': 4,
                        'sla': 0.95,
                    },
                },
            ],
            200,
            [0.0, 7.0, 7.0, None, None, None, None, None, None, None],
            id='many_calculations',
        ),
    ),
)
async def test_forecast_recalculate_entities(
        taxi_workforce_management_web,
        fill_forecast_values,
        dates_to_calculate,
        result,
        status,
        values_after_deleting_first,
):
    revisions = await fill_forecast_values(2)
    revision_id = utils.serialize_date_revision(revisions[0]['updated_at'])

    default_settings = {
        'sla': 0.95,
        'average_handle_time': 54,
        'service_time': 4,
        'absence_periods_percentage': [
            {'hour_from': 0, 'hour_to': 9, 'value': 0.05},
            {'hour_from': 23, 'hour_to': 6, 'value': 0.08},
        ],
        'break_percentage': 0.08,
    }

    request = {'forecast_id': 1, 'revision_id': revision_id, 'periods': []}

    for date in dates_to_calculate:
        record_from_date, record_to_date = date
        period = {'settings': default_settings}
        if record_from_date:
            period['record_target_from'] = record_from_date
        if record_to_date:
            period['record_target_to'] = record_to_date
        request['periods'].append(period)

    res = await taxi_workforce_management_web.post(
        V2_RECALCULATE_URI, json=request, headers=HEADERS,
    )
    json = await res.json()

    if res.status == 200:
        revision_id = json['new_revision_id']

    res = await taxi_workforce_management_web.post(
        CALCULATION_URI, json={'forecast_id': 1}, headers=HEADERS,
    )
    json = await res.json()

    assert json['calculations'] == result
    if json['calculations']:
        calculation_id = json['calculations'][0]['id']
    else:
        return

    await taxi_workforce_management_web.post(
        DELETE_URI,
        json={
            'calculation_ids': [calculation_id],
            'forecast_id': 1,
            'revision_id': revision_id,
        },
        headers=HEADERS,
    )

    res = await taxi_workforce_management_web.post(
        CALCULATION_URI, json={'forecast_id': 1}, headers=HEADERS,
    )
    json = await res.json()
    assert json['calculations'] == result[1:]

    res = await taxi_workforce_management_web.post(
        URI, json={'entity_filter': {'forecast_id': 1}}, headers=HEADERS,
    )
    json = await res.json()

    assert (
        _get_final_values(json['forecast_entities'][0])
        == values_after_deleting_first
    )
