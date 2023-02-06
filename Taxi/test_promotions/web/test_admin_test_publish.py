import copy

import aiohttp
import aiohttp.web
import pytest


DEFAULT_JSON = {
    'promotion_id': 'id4',
    'phones': ['+79991234567', '+79993215476'],
}
DEFAULT_EXPERIMENT = {
    'name': 'promotions_test_publish',
    'last_modified_at': 123,
    'clauses': [],
}
URL = 'admin/promotions/test_publish/'


@pytest.mark.now('2020-03-17T09:30:00.000000Z')
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_publish_ok(web_app_client, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        return DEFAULT_EXPERIMENT

    response = await web_app_client.post(URL, json=DEFAULT_JSON)
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={DEFAULT_JSON.get("promotion_id")}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'published'
    assert 'published_at' in promotion
    assert promotion['experiment'] == DEFAULT_EXPERIMENT['name']
    assert promotion['start_date'] == '2020-03-17T09:30:00.000000Z'
    assert promotion['end_date'] == '2020-03-17T10:30:00.000000Z'
    assert promotion['revision_history'] == [
        {
            'revision': 'some_revision2',
            'created_at': '2019-07-22T16:51:10.000000Z',
        },
        {
            'revision': 'some_revision3',
            'created_at': '2019-07-22T16:51:11.000000Z',
        },
        {
            'revision': 'some_revision4',
            'created_at': '2019-07-22T16:51:12.000000Z',
        },
        {
            'revision': 'some_revision5',
            'created_at': '2019-07-22T16:51:13.000000Z',
        },
        {
            'revision': promotion['revision'],
            'created_at': '2020-03-17T09:30:00.000000Z',
        },
    ]


@pytest.mark.now('2020-03-17T09:30:00.000000Z')
@pytest.mark.pgsql('promotions', files=['pg_promotions_promo_on_map.sql'])
async def test_publish_promo_on_map_ok(web_app_client, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        return DEFAULT_EXPERIMENT

    request = {
        'promotion_id': 'promo_on_map_id',
        'phones': ['+79991234567', '+79993215476'],
    }

    response = await web_app_client.post(URL, json=request)
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promo_on_map/?promotion_id=promo_on_map_id',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'published'
    assert 'published_at' in promotion
    assert promotion['experiment'] == DEFAULT_EXPERIMENT['name']
    assert promotion['start_date'] == '2020-03-17T12:30:00+03:00'
    assert promotion['end_date'] == '2020-03-17T13:30:00+03:00'


@pytest.mark.now('2020-03-17T09:30:00.000000Z')
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_publish_yql_data(web_app_client, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        return DEFAULT_EXPERIMENT

    request = copy.deepcopy(DEFAULT_JSON)
    request['yql_link'] = 'yql_link'
    response = await web_app_client.post(URL, json=request)
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}

    response = await web_app_client.get(
        f'admin/promotions/?promotion_id={request.get("promotion_id")}',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'publishing'
    assert promotion['has_yql_data']
    assert promotion['yql_data'] == {'link': 'yql_link', 'retries': 0}


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_not_found(web_app_client, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        return DEFAULT_EXPERIMENT

    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data['promotion_id'] = 'not_exists'
    response = await web_app_client.post(URL, json=req_data)
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'not_found',
        'message': 'Коммуникация не найдена',
    }


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_admin_publish_already_published(web_app_client, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        return DEFAULT_EXPERIMENT

    req_data = copy.deepcopy(DEFAULT_JSON)
    req_data['promotion_id'] = 'id1'
    response = await web_app_client.post(URL, json=req_data)
    resp_data = await response.json()
    assert response.status == 409
    assert resp_data == {
        'code': 'already_published',
        'message': 'Коммуникация уже опубликована',
    }


@pytest.mark.config(PROMOTIONS_TEST_PUBLISH_ENABLED=False)
async def test_feature_disabled(web_app_client, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        return DEFAULT_EXPERIMENT

    response = await web_app_client.post(URL, json=DEFAULT_JSON)
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'test_publish_disabled',
        'message': 'Тестовая публикация отключена конфигом',
    }


@pytest.mark.now('2020-03-17T12:29:04.667466+03:00')
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin.sql'])
async def test_phones_rewrite(web_app_client, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        if request.method == 'PUT':
            assert request.json['last_modified_at'] == 123
            assert request.json['clauses'][0]['title'] == '+79991234567'
            assert (
                request.json['clauses'][0]['predicate']['init']['set'][0]
                == '+79991234567'
            )
            assert request.json['clauses'][1]['title'] == '+79993215476'
            assert (
                request.json['clauses'][1]['predicate']['init']['set'][0]
                == '+79993215476'
            )
            return DEFAULT_EXPERIMENT

        resp = copy.deepcopy(DEFAULT_EXPERIMENT)
        resp['clauses'].append(
            {
                'title': 'id4',
                'value': {'enabled': True},
                'predicate': {
                    'type': 'in_set',
                    'init': {
                        'arg_name': 'phone_id',
                        'set': ['another_phone'],
                        'set_elem_type': 'string',
                        'transform': 'replace_phone_to_phone_id',
                        'phone_type': 'yandex',
                    },
                },
            },
        )
        return resp

    response = await web_app_client.post(URL, json=DEFAULT_JSON)
    resp_data = await response.json()
    assert response.status == 200
    assert resp_data == {}


@pytest.mark.parametrize('error_code', [404, 409])
async def test_taxi_exp_4xx_exceptions(web_app_client, mockserver, error_code):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        return mockserver.make_response(
            status=error_code,
            json={'code': 'ERROR_CODE', 'message': 'Error message'},
        )

    response = await web_app_client.post(URL, json=DEFAULT_JSON)
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'taxi_exp_request_error',
        'message': 'Ошибка в запросе в сервис экспериментов',
        'details': {
            'reason': (
                f'Request to taxi_exp failed: (response_code={error_code}): '
                '{"code": "ERROR_CODE", "message": "Error message"}'
            ),
        },
    }


async def test_exp_error_500(web_app_client, mockserver):
    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _experiments(request):
        return aiohttp.web.HTTPInternalServerError()

    response = await web_app_client.post(URL, json=DEFAULT_JSON)
    resp_data = await response.json()
    assert response.status == 400
    assert resp_data == {
        'code': 'taxi_exp_remote_error',
        'message': 'Ошибка сервиса экспериментов',
    }
