from test_workforce_management.web import util as test_util

URI = 'v1/operators/forecast/modify'
GET_URI = 'v1/operators/forecast/values'
HEADERS = {'X-WFM-Domain': 'taxi'}


DEFAULT_ENTITY = {
    'entity_target': '2020-02-27T03:00:00+03:00',
    'forecast_type': 'weekly',
    'id': 1,
    'name': 'hello i am under the water',
    'records': [],
    'skill': 'not_a_skill',
    'source': 'custom',
    'value_type': 'calls',
    'description': 'hello',
}


def _get_default(**kwargs):
    res = DEFAULT_ENTITY.copy()
    res.update(kwargs)
    return [res]


FIRST_ENTITY_V2 = _get_default(
    records=[
        {
            'base_value': 21.0,
            'id': 1,
            'lower_value': 11.0,
            'record_target': '2020-02-27T04:00:00+03:00',
            'upper_value': 101.0,
        },
        {
            'base_value': 22.0,
            'id': 2,
            'lower_value': 12.0,
            'record_target': '2020-02-27T05:00:00+03:00',
            'upper_value': 102.0,
        },
    ],
)

FIRST_ENTITY_V3 = _get_default(
    records=[
        {
            'base_value': 21.0,
            'id': 1,
            'lower_value': 11.0,
            'record_target': '2020-02-27T04:00:00+03:00',
            'upper_value': 101.0,
        },
        {
            'base_value': 22.0,
            'id': 2,
            'lower_value': 12.0,
            'record_target': '2020-02-27T05:00:00+03:00',
            'upper_value': 102.0,
        },
    ],
)

FIRST_ENTITY_V4 = _get_default(
    records=[
        {
            'base_value': 210.0,
            'id': 1,
            'lower_value': 110.0,
            'record_target': '2020-02-27T04:00:00+03:00',
            'upper_value': 1010.0,
        },
    ],
)


async def test_forecast_modify_base(
        taxi_workforce_management_web, web_context,
):

    insert_data = {
        'forecast_entity': {
            'entity_target': '2020-02-27T03:00:00+03:00',
            'forecast_type': 'weekly',
            'source': 'auto',
            'records': [],
            'skill': 'not_a_skill',
            'value_type': 'calls',
            'name': 'hello i am under the water',
            'description': 'hello',
        },
        'mode': 'modify',
    }

    def update_insert_data(**kwargs):
        insert_data['forecast_entity'].update(kwargs)

    res = await taxi_workforce_management_web.post(
        URI, json=insert_data, headers=HEADERS,
    )
    assert res.status == 200
    json = await res.json()
    new_revision = json['new_revision_id']

    get_res = await taxi_workforce_management_web.post(
        GET_URI, json={}, headers=HEADERS,
    )
    assert (
        test_util.exclude_revision((await get_res.json())['forecast_entities'])
        == _get_default()
    )

    update_insert_data(
        id=1,
        name='hello i am under the water',
        revision_id='2020-06-09T14:23:21.746626 +0000',
    )

    res = await taxi_workforce_management_web.post(
        URI, json=insert_data, headers=HEADERS,
    )
    assert res.status == 409
    update_insert_data(
        id=1,
        revision_id=new_revision,
        records=[
            {
                'base_value': 21.0,
                'lower_value': 11.0,
                'record_target': '2020-02-27T04:00:00+03:00',
                'upper_value': 101.0,
            },
            {
                'base_value': 22.0,
                'lower_value': 12.0,
                'record_target': '2020-02-27T05:00:00+03:00',
                'upper_value': 102.0,
            },
        ],
    )

    res = await taxi_workforce_management_web.post(
        URI, json=insert_data, headers=HEADERS,
    )
    assert res.status == 200
    json = await res.json()
    new_revision = json['new_revision_id']
    get_res = await taxi_workforce_management_web.post(
        GET_URI, json={}, headers=HEADERS,
    )
    assert (
        test_util.exclude_revision((await get_res.json())['forecast_entities'])
        == FIRST_ENTITY_V2
    )

    update_insert_data(
        id=1,
        revision_id=new_revision,
        records=[
            {
                'base_value': 21.0,
                'lower_value': 11.0,
                'record_target': '2020-02-27T04:00:00+03:00',
                'upper_value': 101.0,
                'id': 1,
            },
        ],
    )

    res = await taxi_workforce_management_web.post(
        URI, json=insert_data, headers=HEADERS,
    )
    assert res.status == 200
    json = await res.json()
    new_revision = json['new_revision_id']
    get_res = await taxi_workforce_management_web.post(
        GET_URI, json={}, headers=HEADERS,
    )
    assert (
        test_util.exclude_revision((await get_res.json())['forecast_entities'])
        == FIRST_ENTITY_V3
    )

    insert_data = {
        'forecast_entity': {
            'entity_target': '2020-02-27T03:00:00+03:00',
            'forecast_type': 'weekly',
            'source': 'auto',
            'records': [
                {
                    'base_value': 210.0,
                    'lower_value': 110.0,
                    'record_target': '2020-02-27T04:00:00+03:00',
                    'upper_value': 1010.0,
                    'id': 1,
                },
            ],
            'skill': 'not_a_skill',
            'value_type': 'calls',
            'name': 'hello i am under the water',
            'revision_id': new_revision,
            'id': 1,
        },
        'mode': 'replace',
    }

    res = await taxi_workforce_management_web.post(
        URI, json=insert_data, headers=HEADERS,
    )
    assert res.status == 200
    get_res = await taxi_workforce_management_web.post(
        GET_URI, json={}, headers=HEADERS,
    )
    assert (
        test_util.exclude_revision((await get_res.json())['forecast_entities'])
        == FIRST_ENTITY_V4
    )
