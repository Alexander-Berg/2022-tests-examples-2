import copy
import json

import pytest


HEADERS = {
    'Cookie': 'Session_id=123',
    'Content-Type': 'application/json',
    'X-Yandex-UID': '44',
}

PAYMENTMETHODS_RESPONSE = {
    'default_payment_method_id': 'cash',
    'last_payment_method': {
        'id': 'cash-89c43fa2faab4518849ae29fdc25926d',
        'type': 'cash',
    },
    'methods': [
        {
            'can_order': True,
            'hide_user_cost': False,
            'id': 'cash',
            'label': 'Наличные',
            'type': 'cash',
            'zone_available': True,
        },
        {
            'can_order': True,
            'cost_center': '',
            'description': 'Осталось 2955 из 6000 руб.',
            'hide_user_cost': False,
            'id': 'corp-89c43fa2faab4518849ae29fdc25926d',
            'label': 'Команда Яндекс.Такси',
            'type': 'corp',
            'zone_available': True,
        },
    ],
}

MOCKING_HANDLERS = [
    'ordersdraft',
    'expectedpositions',
    'nearestposition',
    'profile',
    'zoneinfo',
    'orderscommit',
    'expecteddestinations',
    'orderssearch',
    'orderscancel',
    'ordersestimate',
    'zonaltariffdescription',
    'paymentmethods',
    'nearestzone',
]


def prepare_database(pgsql, is_corp_client=True):
    with pgsql['callcenter_exams'].cursor() as cursor:
        cursor.execute(
            'INSERT INTO callcenter_exams.exam_questions '
            '(question_id, audio_link, answer) '
            'VALUES (\'q_6\', \'q6_default_link\', \'{"ordersdraft": '
            '{"payment": {"type": "cash", "payment_method_id": "cash"}, '
            '"route": [{"geopoint": [54.58, 73.23]}, '
            '{"geopoint": [54.58, 74.0]}], "class": ["econom"], '
            '"requirements": {}}}\'::jsonb)',
        )

        cursor.execute(
            'INSERT INTO callcenter_exams.mock_responses '
            '(question_id, handler, answer, is_default) '
            'VALUES (\'q_6\', \'orderssearch\', '
            '\'{"orders":[{"payment": {"payment_method_id": "corp", '
            '"type": "corp"}, '
            '"request":{"requirements": {}, "route": ['
            '{"geopoint": [54.58, 73.23]}, {"geopoint": [54.58, 74.0]}'
            '], "class": "econom"}, '
            '"status": "waiting"}]}\'::jsonb, FALSE)',
        )

        paymentmethods_response = copy.deepcopy(PAYMENTMETHODS_RESPONSE)
        if not is_corp_client:
            paymentmethods_response['methods'] = [
                method
                for method in paymentmethods_response['methods']
                if method['type'] != 'corp'
            ]
        cursor.execute(
            'INSERT INTO callcenter_exams.mock_responses '
            '(question_id, handler, answer, is_default) '
            'VALUES '
            '(\'q_6\', \'paymentmethods\', %s, FALSE)',
            (json.dumps(paymentmethods_response),),
        )


def update_route(route):
    additional_dict = {
        'city': 'Москва',
        'fullname': 'Россия, Москва, Большая Татарская улица, 35с4',
        'short_text': 'Большая Татарская улица, 35с4',
    }
    for point in route:
        point.update(additional_dict)
    return route


@pytest.mark.parametrize(
    ['request_type', 'question_id', 'request_data', 'resp_code', 'resp'],
    [
        (
            'create',
            'new_q',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': True,
                'audio_link': 'link',
                'difficulty': 'easy',
            },
            200,
            {},
        ),
        (
            'create',
            'q_5',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': True,
                'audio_link': 'link',
            },
            400,
            {
                'code': 'DATABASE_QUERY_ERROR',
                'message': 'Attempt to insert existing question_id',
            },
        ),
        (
            'create',
            'new_q',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': False,
                'audio_link': 'link',
                'orderssearch': [
                    {
                        'data': {
                            'payment': {
                                'payment_method_id': 'corp',
                                'type': 'corp',
                            },
                            'requirements': {},
                            'route': [{'geopoint': [54.58, 73.23]}],
                            'class': ['econom'],
                        },
                        'status': 'waiting',
                    },
                ],
            },
            200,
            {},
        ),
        (
            'modify',
            'new_q',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': True,
                'audio_link': 'link',
            },
            404,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Modification of uncreated question',
            },
        ),
        (
            'modify',
            'q_5',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': True,
                'audio_link': 'link',
            },
            200,
            {},
        ),
        (
            'modify',
            'q_5',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': True,
                'audio_link': 'link',
                'orderssearch': [
                    {
                        'data': {
                            'payment': {
                                'payment_method_id': 'cash',
                                'type': 'cash',
                            },
                            'requirements': {},
                            'route': [{'geopoint': [54.58, 73.23]}],
                            'class': ['econom'],
                        },
                        'status': 'waiting',
                    },
                ],
            },
            200,
            {},
        ),
        (
            'modify',
            'q_6',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': False,
                'audio_link': 'link',
            },
            200,
            {},
        ),
        (
            'modify',
            'q_6',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': True,
                'audio_link': 'link',
                'orderssearch': [
                    {
                        'data': {
                            'payment': {
                                'payment_method_id': 'cash',
                                'type': 'cash',
                            },
                            'requirements': {},
                            'route': [{'geopoint': [54.58, 73.23]}],
                            'class': ['econom'],
                        },
                        'status': 'waiting',
                    },
                ],
            },
            200,
            {},
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_create_modify_question(
        mock_yamaps,
        load_json,
        web_app_client,
        pgsql,
        request_type,
        question_id,
        request_data,
        resp_code,
        resp,
):
    @mock_yamaps('/yandsearch')
    async def _handle(request):
        return load_json('yamaps.json')

    if request_type == 'modify':
        prepare_database(pgsql)

    test_request = {'question_id': question_id, **request_data}
    url = '/v1/modify_question'

    if request_type == 'create':
        response = await web_app_client.post(
            url, json=test_request, headers=HEADERS,
        )
    if request_type == 'modify':
        response = await web_app_client.put(
            url, json=test_request, headers=HEADERS,
        )

    assert response.status == resp_code
    if resp != {}:
        assert await response.json() == resp

    if resp_code == 200:
        with pgsql['callcenter_exams'].cursor() as cursor:
            cursor.execute(
                f'SELECT audio_link, answer FROM '
                f'callcenter_exams.exam_questions WHERE '
                f'question_id=\'{question_id}\'',
            )
            assert cursor.rowcount == 1
            res = cursor.fetchone()

            expected_db_resp = copy.deepcopy(request_data)
            orderssearch_response = expected_db_resp.pop('orderssearch', None)
            is_corp_client = expected_db_resp.pop('is_corp_client', None)
            audio_link = expected_db_resp.pop('audio_link', None)
            expected_db_resp['ordersdraft'] = expected_db_resp['ordersdraft'][
                'data'
            ]
            assert res[-1] == expected_db_resp
            assert res[-2] == audio_link

            for handler in MOCKING_HANDLERS:
                cursor.execute(
                    f'SELECT is_default, answer FROM '
                    f'callcenter_exams.mock_responses WHERE '
                    f'question_id=\'{question_id}\' and handler=\'{handler}\'',
                )
                assert cursor.rowcount == 1
                res = cursor.fetchone()

                if handler not in ['orderssearch', 'paymentmethods']:
                    assert res[-2]

                if handler == 'orderssearch':
                    if orderssearch_response:
                        expected_orderssearch_resp = {
                            'orders': [
                                {
                                    'status': 'waiting',
                                    'payment': orderssearch_response[i][
                                        'data'
                                    ]['payment'],
                                    'request': {
                                        'route': update_route(
                                            orderssearch_response[i]['data'][
                                                'route'
                                            ],
                                        ),
                                        'class': 'econom',
                                        'requirements': orderssearch_response[
                                            i
                                        ]['data']['requirements'],
                                    },
                                    'userid': (
                                        '34bf63e5a78f41768f61a031cfce189a'
                                    ),
                                    'orderid': (
                                        '56e5d63c055b1773a159dfde66ffaaa0'
                                    ),
                                    'cancel_disabled': False,
                                    'cost_message_details': {
                                        'cost_breakdown': [],
                                    },
                                    'cancel_rules': {
                                        'state': 'free',
                                        'title': 'Бесплатная отмена',
                                        'message': (
                                            'Сейчас отмена бесплатна. '
                                            'После приезда водителя '
                                            'за неё, возможно, '
                                            'придётся заплатить'
                                        ),
                                        'message_support': '',
                                        'state_change_estimate': 434,
                                    },
                                    'driver': {
                                        'name': 'Симонов Исай Богданович',
                                        'phone': '+70003660291',
                                    },
                                    'vehicle': {
                                        'color': 'коричневый',
                                        'model': 'Lexus ES',
                                        'plates': 'Т808СР777',
                                        'location': [54.58, 73.23],
                                        'color_code': '200204',
                                        'short_car_number': '808',
                                    },
                                }
                                for i in range(len(orderssearch_response))
                            ],
                        }
                        assert res[-1] == expected_orderssearch_resp
                    assert res[-2] == (orderssearch_response is None)

                if handler == 'paymentmethods':
                    if is_corp_client:
                        assert 'corp' in [
                            method['type'] for method in res[-1]['methods']
                        ]
                    else:
                        assert 'corp' not in [
                            method['type'] for method in res[-1]['methods']
                        ]
                    assert not res[-2]


@pytest.mark.parametrize(
    ['question_id', 'resp_code'], [('q_1', 200), ('q_6', 204)],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_delete_question(web_app_client, pgsql, question_id, resp_code):
    url = f'/v1/modify_question?question_id={question_id}'

    response = await web_app_client.delete(url, headers=HEADERS)

    assert response.status == resp_code

    with pgsql['callcenter_exams'].cursor() as cursor:
        for db in ['exam_questions', 'mock_responses']:
            cursor.execute(
                f'SELECT question_id FROM '
                f'callcenter_exams.{db} WHERE '
                f'question_id=\'{question_id}\'',
            )
            assert cursor.rowcount == 0


@pytest.mark.parametrize(
    ['question_id', 'resp_code', 'resp'],
    [
        (
            'q_6',
            200,
            {
                'audio_link': 'q6_default_link',
                'ordersdraft': {
                    'data': {
                        'class': ['econom'],
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {},
                        'route': [
                            {'geopoint': [54.58, 73.23]},
                            {'geopoint': [54.58, 74.0]},
                        ],
                    },
                },
                'orderssearch': [
                    {
                        'data': {
                            'class': ['econom'],
                            'payment': {
                                'payment_method_id': 'corp',
                                'type': 'corp',
                            },
                            'requirements': {},
                            'route': [
                                {'geopoint': [54.58, 73.23]},
                                {'geopoint': [54.58, 74.0]},
                            ],
                        },
                        'status': 'waiting',
                    },
                ],
                'is_corp_client': False,
            },
        ),
        (
            'q_6',
            200,
            {
                'audio_link': 'q6_default_link',
                'ordersdraft': {
                    'data': {
                        'class': ['econom'],
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {},
                        'route': [
                            {'geopoint': [54.58, 73.23]},
                            {'geopoint': [54.58, 74.0]},
                        ],
                    },
                },
                'orderssearch': [
                    {
                        'data': {
                            'class': ['econom'],
                            'payment': {
                                'payment_method_id': 'corp',
                                'type': 'corp',
                            },
                            'requirements': {},
                            'route': [
                                {'geopoint': [54.58, 73.23]},
                                {'geopoint': [54.58, 74.0]},
                            ],
                        },
                        'status': 'waiting',
                    },
                ],
                'is_corp_client': True,
            },
        ),
        (
            'unexisting_question',
            404,
            {
                'code': 'REQUEST_VALIDATION_ERROR',
                'message': 'Request of unknown question',
            },
        ),
        (
            'real_question',
            200,
            {
                'audio_link': 'real_question_link',
                'orderssearch': [
                    {
                        'data': {
                            'payment': {
                                'payment_method_id': 'cash',
                                'type': 'cash',
                            },
                            'requirements': {},
                            'route': [{'geopoint': [55.753219, 37.62251]}],
                            'class': ['econom'],
                        },
                        'status': 'search',
                    },
                ],
                'is_corp_client': True,
            },
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_get_question(
        web_app_client, pgsql, question_id, resp_code, resp,
):
    is_corp_client = (
        resp['is_corp_client'] if 'is_corp_client' in resp else True
    )
    prepare_database(pgsql, is_corp_client=is_corp_client)

    url = f'/v1/modify_question?question_id={question_id}'

    response = await web_app_client.get(url, headers=HEADERS)

    assert response.status == resp_code
    assert await response.json() == resp


@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_consistence(mock_yamaps, load_json, web_app_client, pgsql):
    @mock_yamaps('/yandsearch')
    async def _handle(request):
        return load_json('yamaps.json')

    request = {
        'question_id': 'lifecycle_question',
        'ordersdraft': {
            'data': {
                'payment': {'payment_method_id': 'cash', 'type': 'cash'},
                'requirements': {'nosmoking': True, 'yellowcarnumber': True},
                'route': [{'geopoint': [54.58, 73.23]}],
                'class': ['econom'],
            },
        },
        'final_action': 'support_call',
        'orderscancel': 1,
        'is_corp_client': False,
        'audio_link': 'link',
    }

    response = await web_app_client.post(
        '/v1/modify_question', json=request, headers=HEADERS,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/modify_question?question_id=lifecycle_question',
        json=request,
        headers=HEADERS,
    )
    assert response.status == 200
    assert not (await response.json())['is_corp_client']

    request['orderssearch'] = [
        {
            'data': {
                'payment': {'payment_method_id': 'corp', 'type': 'corp'},
                'requirements': {},
                'route': [{'geopoint': [54.58, 73.23]}],
                'class': ['econom'],
            },
            'status': 'waiting',
        },
    ]
    request['is_corp_client'] = True
    request['difficulty'] = 'hard'
    response = await web_app_client.put(
        '/v1/modify_question', json=request, headers=HEADERS,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/modify_question?question_id=lifecycle_question',
        json=request,
        headers=HEADERS,
    )
    assert response.status == 200
    resp = await response.json()
    assert resp['is_corp_client']
    additional_fields = [
        'driver',
        'userid',
        'orderid',
        'vehicle',
        'cancel_rules',
        'cancel_disabled',
        'cost_message_details',
    ]
    for field in additional_fields:
        assert field in resp['orderssearch'][0]

    response = await web_app_client.delete(
        '/v1/modify_question?question_id=lifecycle_question',
        json=request,
        headers=HEADERS,
    )
    assert response.status == 200


@pytest.mark.parametrize(
    ['question_id', 'request_data', 'resp_code', 'to_provoke'],
    [
        (
            'new_q',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': False,
                'audio_link': 'link',
                'orderssearch': [
                    {
                        'data': {
                            'payment': {
                                'payment_method_id': 'corp',
                                'type': 'corp',
                            },
                            'requirements': {},
                            'route': [{'geopoint': [54.58, 73.23]}],
                            'class': ['econom'],
                        },
                        'status': 'waiting',
                    },
                ],
            },
            500,
            True,
        ),
        (
            'new_q',
            {
                'ordersdraft': {
                    'data': {
                        'payment': {
                            'payment_method_id': 'cash',
                            'type': 'cash',
                        },
                        'requirements': {
                            'nosmoking': True,
                            'yellowcarnumber': True,
                        },
                        'route': [{'geopoint': [54.58, 73.23]}],
                        'class': ['econom'],
                    },
                },
                'final_action': 'support_call',
                'orderscancel': 1,
                'is_corp_client': False,
                'audio_link': 'link',
                'orderssearch': [
                    {
                        'data': {
                            'payment': {
                                'payment_method_id': 'corp',
                                'type': 'corp',
                            },
                            'requirements': {},
                            'route': [{'geopoint': [54.58, 73.23]}],
                            'class': ['econom'],
                        },
                        'status': 'waiting',
                    },
                ],
            },
            200,
            False,
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_transaction_rollback(
        mock_yamaps,
        load_json,
        web_app_client,
        pgsql,
        question_id,
        request_data,
        resp_code,
        to_provoke,
):
    @mock_yamaps('/yandsearch')
    async def _handle(request):
        return load_json('yamaps.json')

    cursor = pgsql['callcenter_exams'].cursor()

    if to_provoke:
        # Provoking a conflict in the second transaction request
        cursor.execute(
            f'INSERT INTO callcenter_exams.mock_responses '
            f'(question_id, handler, answer, is_default) '
            f'VALUES (\'{question_id}\', \'profile\', '
            f'\'"provoking_response"\'::jsonb, FALSE)',
        )

    test_request = {'question_id': question_id, **request_data}
    url = '/v1/modify_question'

    response = await web_app_client.post(
        url, json=test_request, headers=HEADERS,
    )

    assert response.status == resp_code

    cursor.execute(
        f'SELECT question_id FROM '
        f'callcenter_exams.exam_questions WHERE '
        f'question_id=\'{question_id}\'',
    )

    assert cursor.rowcount == (0 if to_provoke else 1)
