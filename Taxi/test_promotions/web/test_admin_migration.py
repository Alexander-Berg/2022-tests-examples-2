import json

from aiohttp import web
import pytest


def _make_service(promotion_type: str) -> str:
    return 'taxi-promotions-' + promotion_type


def _make_settings(promo_id, payload):
    settings = payload['extra_fields'].copy()
    settings['priority'] = payload['priority']

    if promo_id == 'eda_banner_id':
        settings['banner_id'] = 13
    else:
        settings['zones'] = payload['zones']
        settings['screens'] = payload['screens']
        settings['meta_tags'] = payload['meta_tags']
        settings['consumers'] = payload['consumers']
        settings['activate_condition'] = {'screen': payload['screens']}

    return settings


@pytest.mark.parametrize(
    'payload_file,experiment_enabled',
    [
        ('promotion_eda_banner.json', False),
        ('promotion_eda_banner.json', True),
        ('promotion_story.json', False),
        ('promotion_story.json', True),
    ],
)
async def test_create(
        web_app_client, mockserver, load, payload_file, experiment_enabled,
):
    payload = json.loads(load(payload_file))

    @mockserver.json_handler('/experiments3/v1/experiments')
    async def _experiments(request):
        return {
            'items': [
                {
                    'name': 'promotions_migrate',
                    'value': {'enabled': experiment_enabled},
                },
            ],
        }

    @mockserver.json_handler('/feeds-admin/v1/taxi-promotions/create')
    async def _feeds_admin_create(request):
        body = request.json
        assert body['settings'].pop('promotion_id') is not None

        settings = payload['extra_fields'].copy()
        settings['type'] = payload['promotion_type']
        settings['priority'] = payload['priority']

        if payload['name'] == 'Eda Banner':
            assert body['settings'].pop('banner_id') is not None
        else:
            settings['zones'] = payload['zones']
            settings['screens'] = payload['screens']
            settings['meta_tags'] = payload['meta_tags']
            settings['consumers'] = payload['consumers']
            settings['activate_condition'] = {'screen': payload['screens']}

        assert body == {
            'service': _make_service(payload['promotion_type']),
            'name': payload['name'],
            'payload': {
                'type': payload['promotion_type'],
                'pages': payload['pages'],
            },
            'settings': settings,
        }
        return {'id': '100'}

    response = await web_app_client.post(
        '/admin/promotions/create/', json=payload,
    )
    assert response.status == 201
    if experiment_enabled:
        assert _feeds_admin_create.times_called == 1
    else:
        assert _feeds_admin_create.times_called == 0


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin_migration.sql'])
@pytest.mark.parametrize(
    'promo_id,payload_file,experiment_enabled',
    [
        ('eda_banner_id', 'promotion_eda_banner.json', False),
        ('eda_banner_id', 'promotion_eda_banner.json', True),
        ('story_id', 'promotion_story.json', False),
        ('story_id', 'promotion_story.json', True),
    ],
)
async def test_get(
        web_app_client,
        mockserver,
        load,
        promo_id,
        payload_file,
        experiment_enabled,
):
    payload = json.loads(load(payload_file))

    @mockserver.json_handler('/experiments3/v1/experiments')
    async def _experiments(request):
        return {
            'items': [
                {
                    'name': 'promotions_migrate',
                    'value': {'enabled': experiment_enabled},
                },
            ],
        }

    @mockserver.json_handler('/feeds-admin/v1/taxi-promotions/get')
    async def _feeds_admin_get(request):
        assert request.args['id'] == '100'
        assert request.args['service'] == _make_service(
            payload['promotion_type'],
        )
        return {
            'id': request.args['id'],
            'service': request.args['service'],
            'name': payload['name'],
            'created': '2019-07-22T16:51:09+0000',
            'updated': '2019-07-22T16:51:09+0000',
            'author': 'v-belikov',
            'status': 'published',
            'payload': {
                'type': payload['promotion_type'],
                'pages': payload['pages'],
            },
            'settings': {
                'type': payload['promotion_type'],
                'promotion_id': '794d94ee2b9e4b428d5c9f51fe42f6c6',
                'priority': payload['priority'],
                **_make_settings(promo_id, payload),
            },
            'recipients': {
                'experiment': 'exp1',
                'yql_link': 'https://yandex.ru',
            },
            'schedule': {
                'start_at': '2019-07-25T16:51:09',
                'finish_at': '2019-07-26T16:51:09',
            },
        }

    response = await web_app_client.get(
        f'/admin/promotions/?promotion_id={promo_id}',
    )
    assert response.status == 200
    if experiment_enabled:
        assert _feeds_admin_get.times_called == 1

        extra_fields = payload['extra_fields'].copy()
        if payload['name'] == 'Eda Banner':
            extra_fields['banner_id'] = 13

        assert await response.json() == {
            'id': promo_id,
            'name': payload['name'],
            'promotion_type': payload['promotion_type'],
            'status': 'published',
            'experiment': 'exp1',
            'has_yql_data': True,
            'priority': payload['priority'],
            'pages': payload['pages'],
            'extra_fields': extra_fields,
            'yql_data': {'link': 'https://yandex.ru', 'retries': 3},
            'created_at': '2019-07-22T16:51:09',
            'updated_at': '2019-07-22T16:51:09',
            'start_date': '2019-07-25T16:51:09',
            'end_date': '2019-07-26T16:51:09',
            'published_at': '2019-07-22T16:51:09',
            'meta_tags': payload.get('meta_tags'),
            'consumers': payload.get('consumers'),
            'screens': payload.get('screens'),
            'zones': payload.get('zones'),
        }
    else:
        assert _feeds_admin_get.times_called == 0


@pytest.mark.now('2020-03-17T12:29:04.667466+03:00')
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin_migration.sql'])
@pytest.mark.parametrize(
    'promo_id,payload_file',
    [
        ('eda_banner_id', 'promotion_eda_banner.json'),
        ('story_id', 'promotion_story.json'),
    ],
)
async def test_update(
        web_app_client, mockserver, load, promo_id, payload_file,
):
    payload = json.loads(load(payload_file))
    payload['name'] = 'New Name'

    if promo_id == 'eda_banner_id':
        payload['extra_fields']['banner_id'] = 13

    @mockserver.json_handler('/feeds-admin/v1/taxi-promotions/update')
    async def _feeds_admin_update(request):
        assert request.json == {
            'id': '100',
            'name': 'New Name',
            'service': _make_service(payload['promotion_type']),
            'payload': {
                'type': payload['promotion_type'],
                'pages': payload['pages'],
            },
            'settings': {
                'type': payload['promotion_type'],
                'priority': payload['priority'],
                'promotion_id': promo_id,
                **_make_settings(promo_id, payload),
            },
        }
        return {'id': '100'}

    response = await web_app_client.put(
        f'/admin/promotions/{promo_id}/', json=payload,
    )
    assert response.status == 200
    assert _feeds_admin_update.times_called == 1


@pytest.mark.now('2020-03-17T12:29:04.667466+03:00')
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin_migration.sql'])
@pytest.mark.parametrize(
    'promo_id,promo_type',
    [('eda_banner_id', 'eda_banner'), ('story_id', 'story')],
)
async def test_publish_unpublish(
        web_app_client, promo_id, promo_type, mockserver,
):
    @mockserver.json_handler('/experiments3/v1/experiments')
    async def _experiments(request):
        return {'items': [{'name': 'promotions_migrate', 'value': True}]}

    @mockserver.json_handler('/feeds-admin/v1/taxi-promotions/publish')
    async def _feeds_admin_publish(request):
        assert request.json == {
            'id': '100',
            'service': _make_service(promo_type),
            'schedule': {
                'start_at': '2019-07-22T19:51:09+0300',
                'finish_at': '2019-07-24T20:53:10+0300',
            },
            'recipients': {'experiment': 'pub_exp'},
        }
        return {}

    @mockserver.json_handler('/feeds-admin/v1/taxi-promotions/unpublish')
    async def _feeds_admin_unpublish(request):
        assert request.json == {
            'id': '100',
            'service': _make_service(promo_type),
        }
        return {}

    # Publish
    response = await web_app_client.post(
        '/admin/promotions/publish/',
        json={
            'promotion_id': promo_id,
            'start_date': '2019-07-22T16:51:09.000Z',
            'end_date': '2019-07-24T17:53:10.000Z',
            'experiment': 'pub_exp',
            'ticket': 'TAXI-123',
        },
    )
    assert response.status == 200
    assert _feeds_admin_publish.times_called == 1

    # Unpublish
    response = await web_app_client.post(
        '/admin/promotions/unpublish/', json={'promotion_id': promo_id},
    )
    assert response.status == 200
    assert _feeds_admin_unpublish.times_called == 1


@pytest.mark.now('2020-03-17T12:29:04.667466+03:00')
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin_migration.sql'])
async def test_publication_failed(web_app_client, mockserver):
    @mockserver.json_handler('/experiments3/v1/experiments')
    async def _experiments(request):
        return {
            'items': [
                {'name': 'promotions_migrate', 'value': {'enabled': True}},
            ],
        }

    @mockserver.json_handler('/feeds-admin/v1/taxi-promotions/publish/')
    async def _feeds_admin_publish(request):
        return web.json_response(data={}, status=400)

    response = await web_app_client.post(
        '/admin/promotions/publish/',
        json={
            'promotion_id': 'eda_banner_id',
            'start_date': '2019-07-22T16:51:09.000Z',
            'end_date': '2019-07-24T17:53:10.000Z',
            'experiment': 'pub_exp',
            'ticket': 'TAXI-123',
        },
    )
    assert response.status == 502
    response = await web_app_client.get(
        f'admin/promotions/?promotion_id=eda_banner_id',
    )
    promotion = await response.json()
    assert response.status == 200
    assert promotion['status'] == 'created'


@pytest.mark.pgsql('promotions', files=['pg_promotions_admin_migration.sql'])
@pytest.mark.parametrize('experiment', [{'enabled': False}, {'enabled': True}])
async def test_list(web_app_client, mockserver, experiment):
    @mockserver.json_handler('/experiments3/v1/experiments')
    async def _experiments(request):
        return {'items': [{'name': 'promotions_migrate', 'value': experiment}]}

    @mockserver.json_handler('/feeds-admin/v1/taxi-promotions/list')
    async def _feeds_admin_list(request):
        assert request.json == {
            'service': _make_service('story'),
            'name': 'Story',
            'status': 'created',
            'offset': 1,
            'limit': 12,
        }
        return {
            'service': _make_service('story'),
            'offset': 1,
            'limit': 12,
            'total': 10,
            'items': [
                {'id': '100', 'name': 'Story 1', 'promotion_id': 'id1'},
                {'id': '101', 'name': 'Story 2', 'promotion_id': 'id2'},
            ],
        }

    response = await web_app_client.get(
        '/admin/promotions/list/',
        params={
            'type': 'story',
            'status': 'created',
            'name': 'Story',
            'offset': 1,
            'limit': 12,
        },
    )
    assert response.status == 200
    if experiment['enabled']:
        assert _feeds_admin_list.times_called == 1
        assert await response.json() == {
            'offset': 1,
            'limit': 12,
            'total': 10,
            'items': [
                {'id': 'id1', 'name': 'Story 1'},
                {'id': 'id2', 'name': 'Story 2'},
            ],
        }
    else:
        assert _feeds_admin_list.times_called == 0


@pytest.mark.now('2020-03-17T12:29:04.667466+03:00')
@pytest.mark.pgsql('promotions', files=['pg_promotions_admin_migration.sql'])
async def test_archive(web_app_client, mockserver):
    @mockserver.json_handler('/feeds-admin/v1/taxi-promotions/archive')
    async def _feeds_admin_archive(request):
        assert request.json == {'id': '100', 'service': _make_service('story')}
        return {}

    response = await web_app_client.post(
        '/admin/promotions/archive/', json={'promotion_id': 'story_id'},
    )
    assert response.status == 200
    assert _feeds_admin_archive.times_called == 1
