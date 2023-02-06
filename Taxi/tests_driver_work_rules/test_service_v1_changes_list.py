import pytest

from tests_driver_work_rules import defaults


ENDPOINT = 'service/v1/changes/list'


@pytest.mark.pgsql('misc', files=['changes.sql'])
@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (
            # select object changes with driver authors: 2 variant of writing
            {
                'query': {
                    'park_id': 'extra_super_park_id_1',
                    'object_id': 'extra_super_object_id_2',
                },
                'limit': 2,
            },
            {
                'park_id': 'extra_super_park_id_1',
                'cursor': (
                    '{"date":"2012-02-02T02:02:02+00:00",'
                    '"id":"extra_super_entry_id_2"}'
                ),
                'object': {
                    'id': 'extra_super_object_id_2',
                    'type': 'MongoDB.Docs.Car.CarDoc',
                },
                'changes': [
                    {
                        'created_at': '2012-02-04T02:02:04+00:00',
                        'created_by': {
                            'identity': 'driver',
                            'driver_profile_id': 'extra_super_user_id_5',
                        },
                        'difference': [
                            {
                                'after': '5dc5216101123b786a285e62',
                                'before': '',
                                'field': 'Id',
                            },
                        ],
                    },
                    {
                        'created_at': '2012-02-03T02:02:03+00:00',
                        'created_by': {
                            'identity': 'driver',
                            'driver_profile_id': 'extra_super_user_id_5',
                        },
                        'difference': [
                            {
                                'after': '5dc5216101123b786a285e62',
                                'before': '',
                                'field': 'Id',
                            },
                            {
                                'after': 'f645b7c9d5e5216104574e521610f731',
                                'before': '',
                                'field': 'CarId',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            # select object changes with fleet-api author: 1 variant of writing
            {
                'query': {
                    'park_id': 'extra_super_park_id_1',
                    'object_id': 'extra_super_object_id_4',
                },
                'limit': 1,
            },
            {
                'park_id': 'extra_super_park_id_1',
                'object': {
                    'id': 'extra_super_object_id_4',
                    'type': 'MongoDB.Docs.Car.CarDoc',
                },
                'changes': [
                    {
                        'created_at': '2014-04-04T04:04:04+00:00',
                        'created_by': {
                            'identity': 'fleet-api',
                            'key_id': 'tralala',
                        },
                        'difference': [
                            {
                                'after': 'О986МР57',
                                'before': 'О986МР56',
                                'field': 'Number',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            # select object changes with tech-support authors:
            # 7 variant of writing
            {
                'query': {
                    'park_id': 'extra_super_park_id_1',
                    'object_id': 'extra_super_object_id_1',
                },
                'limit': 7,
            },
            {
                'park_id': 'extra_super_park_id_1',
                'object': {
                    'id': 'extra_super_object_id_1',
                    'type': 'Yandex.Taximeter.Core.Repositori',
                },
                'changes': [
                    {
                        'created_at': '2011-11-16T11:11:17+00:00',
                        'created_by': {'identity': 'tech-support'},
                        'difference': [
                            {
                                'after': 'Skoda Rapid [391]',
                                'before': 'Пусто',
                                'field': 'Смена ТС',
                            },
                        ],
                    },
                    {
                        'created_at': '2011-11-16T11:11:16+00:00',
                        'created_by': {'identity': 'tech-support'},
                        'difference': [
                            {
                                'after': 'Skoda Rapid [391]',
                                'before': 'Пусто',
                                'field': 'Смена ТС',
                            },
                        ],
                    },
                    {
                        'created_at': '2011-11-15T11:11:15+00:00',
                        'created_by': {'identity': 'tech-support'},
                        'difference': [
                            {
                                'after': 'Skoda Rapid [391]',
                                'before': 'Пусто',
                                'field': 'Смена ТС',
                            },
                        ],
                    },
                    {
                        'created_at': '2011-11-14T11:11:14+00:00',
                        'created_by': {'identity': 'tech-support'},
                        'difference': [
                            {
                                'after': 'Skoda Rapid [391]',
                                'before': 'Пусто',
                                'field': 'Смена ТС',
                            },
                        ],
                    },
                    {
                        'created_at': '2011-11-13T11:11:13+00:00',
                        'created_by': {'identity': 'tech-support'},
                        'difference': [
                            {
                                'after': '22.03.2016 2:53:30',
                                'before': '31.01.2016 13:35:44',
                                'field': 'DateCreate',
                            },
                        ],
                    },
                    {
                        'created_at': '2011-11-12T11:11:12+00:00',
                        'created_by': {'identity': 'tech-support'},
                        'difference': [
                            {
                                'after': '22.03.2016 2:53:30',
                                'before': '31.01.2016 13:35:44',
                                'field': 'DateCreate',
                            },
                        ],
                    },
                    {
                        'created_at': '2011-11-11T11:11:11+00:00',
                        'created_by': {'identity': 'tech-support'},
                        'difference': [
                            {
                                'after': '22.03.2016 2:53:30',
                                'before': '31.01.2016 13:35:44',
                                'field': 'DateCreate',
                            },
                            {
                                'after': 'Уволен',
                                'before': 'Работает',
                                'field': 'WorkStatus',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            # select object changes with platform authors
            {
                'query': {
                    'park_id': 'extra_super_park_id_1',
                    'object_id': 'extra_super_object_id_3',
                },
                'limit': 5,
            },
            {
                'park_id': 'extra_super_park_id_1',
                'object': {
                    'id': 'extra_super_object_id_3',
                    'type': 'Entities.Driver.DriverWorkRule',
                },
                'changes': [
                    {
                        'created_at': '2013-03-04T03:03:04+00:00',
                        'created_by': {'identity': 'platform'},
                        'difference': [
                            {
                                'after': 'False',
                                'before': '',
                                'field': 'IsDriverFixEnabled',
                            },
                        ],
                    },
                    {
                        'created_at': '2013-03-04T03:03:04+00:00',
                        'created_by': {'identity': 'platform'},
                        'difference': [
                            {
                                'after': 'True',
                                'before': 'False',
                                'field': 'IsEnabled',
                            },
                        ],
                    },
                    {
                        'created_at': '2013-03-03T03:03:03+00:00',
                        'created_by': {'identity': 'platform'},
                        'difference': [
                            {
                                'after': 'False',
                                'before': '',
                                'field': 'IsDriverFixEnabled',
                            },
                        ],
                    },
                    {
                        'created_at': '2013-03-02T03:03:02+00:00',
                        'created_by': {'identity': 'platform'},
                        'difference': [
                            {
                                'after': 'False',
                                'before': '',
                                'field': 'IsEnabled',
                            },
                        ],
                    },
                    {
                        'created_at': '2013-03-01T03:03:01+00:00',
                        'created_by': {'identity': 'platform'},
                        'difference': [
                            {
                                'after': 'False',
                                'before': '',
                                'field': 'YandexDisablePayUserCancelOrder',
                            },
                            {
                                'after': 'True',
                                'before': '',
                                'field': 'WorkshiftsEnabled',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            # select object changes with dispatcher authors
            {
                'query': {
                    'park_id': 'extra_super_park_id_0',
                    'object_id': 'extra_super_object_id_1',
                },
                'limit': 4,
            },
            {
                'park_id': 'extra_super_park_id_0',
                'object': {
                    'id': 'extra_super_object_id_1',
                    'type': 'Entities.Driver.DriverWorkRule',
                },
                'changes': [
                    {
                        'created_at': '2020-02-25T22:22:24+00:00',
                        'created_by': {
                            'identity': 'dispatcher',
                            'dispatcher_name': 'Техподдержка',
                            'dispatcher_id': 'extra_super_user_id_7',
                        },
                        'difference': [
                            {
                                'after': 'False',
                                'before': 'True',
                                'field': 'DisableDynamicYandexCommission',
                            },
                        ],
                    },
                    {
                        'created_at': '2020-02-24T22:22:24+00:00',
                        'created_by': {
                            'identity': 'dispatcher',
                            'dispatcher_name': 'Техподдержка',
                            'dispatcher_id': 'extra_super_user_id_7',
                        },
                        'difference': [
                            {
                                'after': 'False',
                                'before': 'True',
                                'field': 'DisableDynamicYandexCommission',
                            },
                        ],
                    },
                    {
                        'created_at': '2020-02-23T22:22:23+00:00',
                        'created_by': {
                            'identity': 'dispatcher',
                            'dispatcher_name': 'Тамара Боромировна',
                            'dispatcher_id': 'extra_super_user_id_1',
                            'user_ip': '109.188.125.30',
                        },
                        'difference': [
                            {
                                'after': '22,00',
                                'before': '22',
                                'field': 'WorkshiftCommissionPercent',
                            },
                        ],
                    },
                    {
                        'created_at': '2020-02-22T22:22:22+00:00',
                        'created_by': {
                            'identity': 'dispatcher',
                            'dispatcher_name': 'Тамара Боромировна',
                            'dispatcher_id': 'extra_super_user_id_1',
                            'user_ip': '109.188.125.30',
                        },
                        'difference': [
                            {
                                'after': '6',
                                'before': '0',
                                'field': 'CommisisonForSubventionPercent',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            # select all changes of object
            {
                'query': {
                    'park_id': 'extra_super_park_id_0',
                    'object_id': 'extra_super_object_id_0',
                },
                'limit': 100,
            },
            {
                'park_id': 'extra_super_park_id_0',
                'object': {
                    'id': 'extra_super_object_id_0',
                    'type': 'TaxiServer.Models.Driver.Driver',
                },
                'changes': [
                    {
                        'created_at': '2010-10-15T10:10:15+00:00',
                        'created_by': {'identity': 'platform'},
                        'difference': [
                            {
                                'after': 'Свои, Яндекс',
                                'before': 'Свои, Яндекс, UpUp',
                                'field': 'ProviderSelected',
                            },
                        ],
                    },
                    {
                        'created_at': '2010-10-12T10:10:12+00:00',
                        'created_by': {'identity': 'platform'},
                        'difference': [
                            {
                                'after': '[88] FORD GALAXY',
                                'before': '[83] FORD GALAXY',
                                'field': 'Смена ТС',
                            },
                        ],
                    },
                    {
                        'created_at': '2010-10-12T10:10:12+00:00',
                        'created_by': {
                            'identity': 'dispatcher',
                            'dispatcher_name': 'Тамара Боромировна',
                            'dispatcher_id': 'extra_super_user_id_1',
                        },
                        'difference': [
                            {
                                'after': '-600,00',
                                'before': '50,00',
                                'field': 'Лимит',
                            },
                        ],
                    },
                    {
                        'created_at': '2010-10-12T10:10:12+00:00',
                        'created_by': {'identity': 'platform'},
                        'difference': [
                            {
                                'after': 'списал  7000',
                                'before': 'вернется позже',
                                'field': 'Comment',
                            },
                        ],
                    },
                    {
                        'created_at': '2010-10-11T10:10:11+00:00',
                        'created_by': {'identity': 'platform'},
                        'difference': [
                            {
                                'after': '01.01.0001 0:00:00',
                                'before': '23.12.2015 7:15:58',
                                'field': 'DateCreate',
                            },
                            {
                                'after': '[75] FORD GALAXIE',
                                'before': '[80] FORD GALAXY',
                                'field': 'Смена ТС',
                            },
                        ],
                    },
                    {
                        'created_at': '2010-10-10T10:10:10+00:00',
                        'created_by': {
                            'identity': 'dispatcher',
                            'dispatcher_name': 'Акакий Вениаминович',
                            'dispatcher_id': 'extra_super_user_id_0',
                            'user_ip': '2a02:2168:1ec3:',
                        },
                        'difference': [
                            {
                                'after': '03.01.2010 13:50:28',
                                'before': '27.12.2009 20:39:26',
                                'field': 'DateCreate',
                            },
                        ],
                    },
                ],
            },
        ),
        (
            # select nonexistent object history
            {
                'query': {
                    'park_id': 'extra_super_park_id_0',
                    'object_id': 'nonexistent_object_id',
                },
                'limit': 100,
            },
            {
                'park_id': 'extra_super_park_id_0',
                'object': {'id': 'nonexistent_object_id'},
                'changes': [],
            },
        ),
    ],
)
async def test_ok(
        taxi_driver_work_rules,
        fleet_parks_shard,
        pgsql,
        request_body,
        expected_response,
):
    response = await taxi_driver_work_rules.post(
        ENDPOINT, headers=defaults.HEADERS, json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.pgsql('misc', files=['changes.sql'])
@pytest.mark.parametrize(
    'request_body, expected_responses',
    [
        (
            {
                'query': {
                    'park_id': 'extra_super_park_id_0',
                    'object_id': 'extra_super_object_id_0',
                },
                'limit': 2,
            },
            [
                {
                    'park_id': 'extra_super_park_id_0',
                    'cursor': (
                        '{"date":"2010-10-12T10:10:12+00:00",'
                        '"id":"extra_super_entry_id_2"}'
                    ),
                    'object': {
                        'id': 'extra_super_object_id_0',
                        'type': 'TaxiServer.Models.Driver.Driver',
                    },
                    'changes': [
                        {
                            'created_at': '2010-10-15T10:10:15+00:00',
                            'created_by': {'identity': 'platform'},
                            'difference': [
                                {
                                    'after': 'Свои, Яндекс',
                                    'before': 'Свои, Яндекс, UpUp',
                                    'field': 'ProviderSelected',
                                },
                            ],
                        },
                        {
                            'created_at': '2010-10-12T10:10:12+00:00',
                            'created_by': {'identity': 'platform'},
                            'difference': [
                                {
                                    'after': '[88] FORD GALAXY',
                                    'before': '[83] FORD GALAXY',
                                    'field': 'Смена ТС',
                                },
                            ],
                        },
                    ],
                },
                {
                    'park_id': 'extra_super_park_id_0',
                    'cursor': (
                        '{"date":"2010-10-11T10:10:11+00:00",'
                        '"id":"extra_super_entry_id_1"}'
                    ),
                    'object': {
                        'id': 'extra_super_object_id_0',
                        'type': 'TaxiServer.Models.Driver.Driver',
                    },
                    'changes': [
                        {
                            'created_at': '2010-10-12T10:10:12+00:00',
                            'created_by': {
                                'identity': 'dispatcher',
                                'dispatcher_name': 'Тамара Боромировна',
                                'dispatcher_id': 'extra_super_user_id_1',
                            },
                            'difference': [
                                {
                                    'after': '-600,00',
                                    'before': '50,00',
                                    'field': 'Лимит',
                                },
                            ],
                        },
                        {
                            'created_at': '2010-10-12T10:10:12+00:00',
                            'created_by': {'identity': 'platform'},
                            'difference': [
                                {
                                    'after': 'списал  7000',
                                    'before': 'вернется позже',
                                    'field': 'Comment',
                                },
                            ],
                        },
                    ],
                },
                {
                    'park_id': 'extra_super_park_id_0',
                    'object': {
                        'id': 'extra_super_object_id_0',
                        'type': 'TaxiServer.Models.Driver.Driver',
                    },
                    'changes': [
                        {
                            'created_at': '2010-10-11T10:10:11+00:00',
                            'created_by': {'identity': 'platform'},
                            'difference': [
                                {
                                    'after': '01.01.0001 0:00:00',
                                    'before': '23.12.2015 7:15:58',
                                    'field': 'DateCreate',
                                },
                                {
                                    'after': '[75] FORD GALAXIE',
                                    'before': '[80] FORD GALAXY',
                                    'field': 'Смена ТС',
                                },
                            ],
                        },
                        {
                            'created_at': '2010-10-10T10:10:10+00:00',
                            'created_by': {
                                'identity': 'dispatcher',
                                'dispatcher_name': 'Акакий Вениаминович',
                                'dispatcher_id': 'extra_super_user_id_0',
                                'user_ip': '2a02:2168:1ec3:',
                            },
                            'difference': [
                                {
                                    'after': '03.01.2010 13:50:28',
                                    'before': '27.12.2009 20:39:26',
                                    'field': 'DateCreate',
                                },
                            ],
                        },
                    ],
                },
            ],
        ),
        (
            {
                'query': {
                    'park_id': 'extra_super_park_id_0',
                    'object_id': 'extra_super_object_id_0',
                },
                'limit': 4,
            },
            [
                {
                    'park_id': 'extra_super_park_id_0',
                    'cursor': (
                        '{"date":"2010-10-11T10:10:11+00:00",'
                        '"id":"extra_super_entry_id_1"}'
                    ),
                    'object': {
                        'id': 'extra_super_object_id_0',
                        'type': 'TaxiServer.Models.Driver.Driver',
                    },
                    'changes': [
                        {
                            'created_at': '2010-10-15T10:10:15+00:00',
                            'created_by': {'identity': 'platform'},
                            'difference': [
                                {
                                    'after': 'Свои, Яндекс',
                                    'before': 'Свои, Яндекс, UpUp',
                                    'field': 'ProviderSelected',
                                },
                            ],
                        },
                        {
                            'created_at': '2010-10-12T10:10:12+00:00',
                            'created_by': {'identity': 'platform'},
                            'difference': [
                                {
                                    'after': '[88] FORD GALAXY',
                                    'before': '[83] FORD GALAXY',
                                    'field': 'Смена ТС',
                                },
                            ],
                        },
                        {
                            'created_at': '2010-10-12T10:10:12+00:00',
                            'created_by': {
                                'identity': 'dispatcher',
                                'dispatcher_name': 'Тамара Боромировна',
                                'dispatcher_id': 'extra_super_user_id_1',
                            },
                            'difference': [
                                {
                                    'after': '-600,00',
                                    'before': '50,00',
                                    'field': 'Лимит',
                                },
                            ],
                        },
                        {
                            'created_at': '2010-10-12T10:10:12+00:00',
                            'created_by': {'identity': 'platform'},
                            'difference': [
                                {
                                    'after': 'списал  7000',
                                    'before': 'вернется позже',
                                    'field': 'Comment',
                                },
                            ],
                        },
                    ],
                },
                {
                    'park_id': 'extra_super_park_id_0',
                    'object': {
                        'id': 'extra_super_object_id_0',
                        'type': 'TaxiServer.Models.Driver.Driver',
                    },
                    'changes': [
                        {
                            'created_at': '2010-10-11T10:10:11+00:00',
                            'created_by': {'identity': 'platform'},
                            'difference': [
                                {
                                    'after': '01.01.0001 0:00:00',
                                    'before': '23.12.2015 7:15:58',
                                    'field': 'DateCreate',
                                },
                                {
                                    'after': '[75] FORD GALAXIE',
                                    'before': '[80] FORD GALAXY',
                                    'field': 'Смена ТС',
                                },
                            ],
                        },
                        {
                            'created_at': '2010-10-10T10:10:10+00:00',
                            'created_by': {
                                'identity': 'dispatcher',
                                'dispatcher_name': 'Акакий Вениаминович',
                                'dispatcher_id': 'extra_super_user_id_0',
                                'user_ip': '2a02:2168:1ec3:',
                            },
                            'difference': [
                                {
                                    'after': '03.01.2010 13:50:28',
                                    'before': '27.12.2009 20:39:26',
                                    'field': 'DateCreate',
                                },
                            ],
                        },
                    ],
                },
            ],
        ),
    ],
)
async def test_cursor(
        taxi_driver_work_rules,
        fleet_parks_shard,
        pgsql,
        request_body,
        expected_responses,
):
    for expected_response in expected_responses:
        response = await taxi_driver_work_rules.post(
            ENDPOINT, headers=defaults.HEADERS, json=request_body,
        )
        assert response.status_code == 200
        response_body = response.json()
        assert response_body == expected_response

        if 'cursor' in response_body:
            request_body['cursor'] = response_body['cursor']
