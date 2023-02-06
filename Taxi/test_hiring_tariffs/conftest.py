# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import datetime
import json
import typing

import pytest

from taxi.pytest_plugins import core

import hiring_tariffs.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_tariffs.generated.service.pytest_plugins']

SUB_DRAFTS_LIST = 'approvals_list.json'
SUB_FILE_NEW = 'sub_new.json'
SUB_ROUTE_INIT = '/v1/subscriptions/init'
SUB_ROUTE_SHOW = '/v1/subscriptions'


@pytest.fixture
def create_draft(web_app_client):
    """Создание черновика тарифа"""

    async def _wrapper(data, tariff_id: typing.Optional[str] = None) -> str:
        if tariff_id is not None:
            data['tariff_id'] = tariff_id

        response = await web_app_client.post('/v1/tariff/', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def commit_draft(web_app_client):
    """Коммит черновика тарифа"""

    async def _wrapper(tariff_id: str, revision: int) -> str:
        response = await web_app_client.post(
            '/v1/tariff/commit/',
            json={'tariff_id': tariff_id, 'revision': revision},
        )
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def create_tariff(web_app_client):
    """Создание тарифа"""

    async def _wrapper(
            data, labels: typing.Optional[typing.List[str]] = None,
    ) -> str:
        if labels is not None:
            data['labels'] = labels

        response1 = await web_app_client.post('/v1/tariff/', json=data)
        assert response1.status == 200, await response1.text()
        approve = await response1.json()

        response2 = await web_app_client.post(
            '/v1/tariff/commit/',
            json={
                'tariff_id': approve['data']['tariff_id'],
                'revision': approve['data']['revision'],
            },
        )
        assert response2.status == 200, await response2.text()
        return await response2.json()

    return _wrapper


@pytest.fixture
def update_tariff(web_app_client):
    """Обновление тарифа"""

    async def _wrapper(
            tariff_id: str,
            data,
            labels: typing.Optional[typing.List[str]] = None,
    ) -> str:
        data['tariff_id'] = tariff_id

        if labels is not None:
            data['labels'] = labels

        response1 = await web_app_client.post('/v1/tariff/', json=data)
        assert response1.status == 200, await response1.text()
        approve = await response1.json()

        response2 = await web_app_client.post(
            '/v1/tariff/commit/',
            json={
                'tariff_id': approve['data']['tariff_id'],
                'revision': approve['data']['revision'],
            },
        )
        assert response2.status == 200, await response2.text()
        return await response2.json()

    return _wrapper


@pytest.fixture
def get_tariff(web_app_client):
    """Получение тарифа"""

    async def _wrapper(
            tariff_id: str, revision: int = None, time_ts: int = None,
    ) -> str:
        params = {'tariff_id': tariff_id}
        if revision is not None:
            params['revision'] = str(revision)
        if time_ts is not None:
            params['time_ts'] = str(time_ts)

        response = await web_app_client.get('/v1/tariff/', params=params)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def list_tariffs(web_app_client):
    """Получение списка тарифов"""

    async def _wrapper(
            labels: typing.Optional[typing.List[str]] = None,
            time_ts: int = None,
    ) -> str:
        params = {}
        if labels is not None:
            params['labels'] = ','.join(labels)
        if time_ts is not None:
            params['time_ts'] = str(time_ts)

        response = await web_app_client.get('/v1/tariffs/list/', params=params)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def log_tariff(web_app_client):
    """Получение списка ревизий тарифа"""

    async def _wrapper(tariff_id: str) -> str:
        params = {'tariff_id': tariff_id}
        response = await web_app_client.get('/v1/tariff/log/', params=params)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def update_labels_tariff(web_app_client):
    """Обновление меток тарифа"""

    async def _wrapper(
            tariff_id: str, revision: int, labels: typing.List[str],
    ) -> str:
        data = {'tariff_id': tariff_id, 'revision': revision, 'labels': labels}

        response = await web_app_client.post('/v1/tariff/labels/', json=data)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def list_labels(web_app_client):
    """Получение списка меток"""

    async def _wrapper(time_ts: int = None) -> str:
        params = {}
        if time_ts is not None:
            params['time_ts'] = str(time_ts)

        response = await web_app_client.get('/v1/labels/list/', params=params)
        assert response.status == 200, await response.text()
        return await response.json()

    return _wrapper


@pytest.fixture
def mock_territories_api(mockserver):
    @mockserver.json_handler('/territories/v1/countries/list')
    async def _territories(request, **kwargs):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
            ],
        }


@pytest.fixture
def mock_personal_api(mockserver):
    @mockserver.json_handler('/personal/v1/phones/store')
    def _store_phone(request):
        return {
            'id': 'fd835ed6a95f44b598cfca688c710c84',
            'value': request.json['value'],
        }

    @mockserver.json_handler('/personal/v1/yandex_logins/store')
    def _store_yandex_login(request):
        return {
            'id': '14139b62ad34493eb2a87ed19863cccc',
            'value': request.json['value'],
        }


@pytest.fixture
def make_tariffs_request(
        taxi_hiring_tariffs_web, mock_personal_api, mock_territories_api,
):
    async def func(
            route,
            *,
            method='post',
            data=None,
            params=None,
            headers=None,
            status_code=200,
            response_body=None,
    ):
        response: core.Response
        method = getattr(taxi_hiring_tariffs_web, method)
        response = await method(
            route, json=data, params=params, headers=headers,
        )
        assert response.status == status_code
        body = await response.json()
        if response_body:
            assert body == response_body
        return body

    return func


@pytest.fixture
def create_subs(make_tariffs_request, load_json):
    async def create_sub(case: str):
        data = load_json(SUB_FILE_NEW)['valid'][case]
        subs = []
        for task in data:
            response = await make_tariffs_request(
                SUB_ROUTE_INIT, method='post', data=task['request'],
            )
            subs.extend(response['subscriptions'])
        return subs

    return create_sub


@pytest.fixture
def find_subs(make_tariffs_request):
    async def _wrapper(empty: bool = False):
        real_subs = await make_tariffs_request(SUB_ROUTE_SHOW, method='get')
        if not empty:
            assert real_subs['subscriptions']
        return real_subs['subscriptions']

    return _wrapper


@pytest.fixture
def sub_suggests_fill(pgsql):
    with pgsql['hiring_misc'].cursor() as cursor:
        cursor.execute(
            'INSERT INTO'
            '   "hiring_tariffs"."suggests" ("name", "value")'
            'VALUES'
            '   (\'status\', \'active\'),'
            '   (\'status\', \'processing\'),'
            '   (\'status\', \'draft\'),'
            '   (\'status\', \'initiated\'),'
            '   (\'status\', \'completed\'),'
            '   (\'status\', \'deactivated\'),'
            '   (\'status\', \'rejected\'),'
            '   (\'status\', \'created\')',
        )


@pytest.fixture
def mock_approvals(mockserver, load_json, pgsql):
    @mockserver.json_handler('/taxi_approvals/drafts/list/')
    async def _return_drafts(request):
        if int(request.json['offset']):
            return []
        with pgsql['hiring_misc'].cursor() as cursor:
            cursor.execute(
                'SELECT "id", "subscriber_id" '
                'FROM "hiring_tariffs"."subscriptions"',
            )
            existing_subs = {
                item[0]: {'subscriber_id': item[1], 'id': item[0]}
                for item in cursor.fetchall()
            }
            cursor.execute(
                'SELECT "id", "subscription_id" '
                'FROM "hiring_tariffs"."subscriptions_periods"',
            )
            for row in cursor.fetchall():
                existing_subs[row[1]]['period_id'] = int(row[0])
        existing_subs = list(existing_subs.values())
        data = load_json(SUB_DRAFTS_LIST)
        _generate_approvals_data(data, existing_subs)
        return data

    @mockserver.json_handler('/taxi_approvals/drafts/ID1/finish/')
    def _finish_draft_1(request):
        return {}

    @mockserver.json_handler('/taxi_approvals/drafts/ID2/finish/')
    def _finish_draft_2(request):
        return {}

    @mockserver.json_handler('/taxi_approvals/drafts/ID3/finish/')
    def _finish_draft_3(request):
        return {}

    @mockserver.json_handler('/taxi_approvals/drafts/ID4/finish/')
    def _finish_draft_4(request):
        return {}

    @mockserver.json_handler('/taxi_approvals/drafts/ID5/finish/')
    def _finish_draft_5(request):
        return {}

    @mockserver.json_handler('/taxi_approvals/drafts/create/')
    def _create_draft(request):
        body = json.loads(request.json['data'].get('data', '{}'))
        if 'status' in body:
            assert body['status'] in ['draft', 'deactivated']
        elif 'autoprolong' in body:
            assert body['autoprolong'] is False
        elif 'starts_at' in body:
            assert datetime.datetime.strptime(
                body['starts_at'], '%Y-%m-%d',
            ) > datetime.datetime(1970, 1, 1)
        return {'id': 1}


def _generate_approvals_data(data, existing_subs):
    exclude_subscriber_ids = ['CLID4', 'CLID5']
    for item in data:
        if item['data']['type'] == 'update':
            if item['status'] == 'rejected':
                sub_id = _find_sub_for_approvals_mock(
                    existing_subs, ('CLID5',),
                )['id']
            else:
                sub_id = _find_sub_for_approvals_mock(
                    existing_subs, ('CLID4',),
                )['id']
        else:
            sub = _find_sub_for_approvals_mock(
                existing_subs, exclude_subscriber_ids, invert=True,
            )
            sub_id = sub['id']
            exclude_subscriber_ids.append(sub['subscriber_id'])
            item['data']['period_id'] = sub['period_id']
        item['data']['subscription_id'] = sub_id


def _find_sub_for_approvals_mock(existing_subs, subscriber_ids, invert=False):
    if invert:
        return next(
            (
                item
                for item in existing_subs
                if item['subscriber_id'] not in subscriber_ids
            ),
        )
    return next(
        (
            item
            for item in existing_subs
            if item['subscriber_id'] in subscriber_ids
        ),
    )


@pytest.fixture
def mock_parks_replica(mockserver):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    async def _return_billing_client_id(request):
        return {'billing_client_id': '1'}


@pytest.fixture
def mock_billing_replication(mockserver):
    @mockserver.json_handler('/billing-replication/v1/active-contracts/')
    async def _return_billing_client_id(request):
        return [{'ID': '1'}, {'ID': '2'}]
