import json
import math

from dateutil import parser
import pytest
import pytz

person_tag_table = {
    '11111111111111111111111111111111': [0, 1, 2],
    '22222222222222222222222222222222': [0],
    '33333333333333333333333333333333': [1, 2],
    'unregistered': [0, 1],
}
tag_person_table = {
    0: [
        '11111111111111111111111111111111',
        '22222222222222222222222222222222',
        'unregistered',
    ],
    1: [
        '11111111111111111111111111111111',
        '33333333333333333333333333333333',
        'unregistered',
    ],
    2: [
        '11111111111111111111111111111111',
        '33333333333333333333333333333333',
    ],
    3: [],
}

domain_suffix = '@yandex-team.ru'
domain_suffix_len = len(domain_suffix)
prefix = 'person_'
prefix_len = len(prefix)


@pytest.fixture(name='personal', autouse=True)
def personal_service(mockserver):
    @mockserver.json_handler('/personal/v1/yandex_logins/retrieve')
    def retrieve_handler(request):
        data = request.json
        assert data is not None
        id = data['id']
        assert len(id) == 32
        response = {'id': id, 'value': f'person_{id[0]}{domain_suffix}'}
        return mockserver.make_response(json.dumps(response), status=200)

    @mockserver.json_handler('/personal/v1/yandex_logins/store')
    def retrieve_handler(request):
        data = request.json
        assert data is not None
        value = data['value']
        if (
                len(value) > domain_suffix_len + prefix_len
                and value[-domain_suffix_len:] == domain_suffix
                and value[0:prefix_len] == prefix
        ):
            chr = value[-domain_suffix_len - 1]
            response = {'id': chr * 32, 'value': value}
            return mockserver.make_response(json.dumps(response), status=200)
        return mockserver.make_response(
            json.dumps({'code': '404', 'message': 'not found'}), status=404,
        )

    @mockserver.json_handler('/personal/v1/yandex_logins/bulk_retrieve')
    def retrieve_handler(request):
        data = request.json
        assert data is not None
        items = data['items']
        ids = [item['id'] for item in items]
        result = []
        for id in ids:
            assert len(id) == 32
            item = {'id': id, 'value': f'person_{id[0]}{domain_suffix}'}
            result.append(item)
        return mockserver.make_response(
            json.dumps({'items': result}), status=200,
        )


@pytest.fixture(name='cctv-workers', autouse=True)
def cctv_workers_service(mockserver):
    @mockserver.json_handler('/cctv-workers/v1/person/tags')
    def person_list_tags_handler(request):
        data = request.json
        assert data is not None
        ids = data['person_ids']
        if ids is None:
            return mockserver.make_response(status=400)
        result = []
        for id in ids:
            id_result = []
            if id in person_tag_table:
                for item in person_tag_table[id]:
                    id_result.append({'id': item})
            result.append({'person_id': id, 'tags': id_result})
        response = {'tag_info': result}
        return mockserver.make_response(json.dumps(response), status=200)

    @mockserver.json_handler('/cctv-workers/v1/person/tag/add')
    def person_tag_add_handler(request):
        data = request.json
        assert data is not None
        person_id = data['person_id']
        tag_id = data['tag_id']
        if person_id is None or tag_id is None:
            return mockserver.make_response(status=400)
        if tag_id not in tag_person_table:
            return mockserver.make_response(status=404)
        return mockserver.make_response(json.dumps({}), status=200)

    @mockserver.json_handler('/cctv-workers/v1/person/tag/remove')
    def person_tag_remove_handler(request):
        data = request.json
        assert data is not None
        person_id = data['person_id']
        tag_id = data['tag_id']
        if person_id is None or tag_id is None:
            return mockserver.make_response(status=400)
        if person_id not in person_tag_table:
            return mockserver.make_response(status=404)
        if tag_id not in person_tag_table[person_id]:
            return mockserver.make_response(status=404)
        return mockserver.make_response(json.dumps({}), status=200)

    @mockserver.json_handler('/cctv-workers/v1/tags/list')
    def tags_list_handler(request):
        result = []
        for item in tag_person_table:
            result.append({'id': item})
        response = {'tags': result}
        return mockserver.make_response(json.dumps(response), status=200)

    @mockserver.json_handler('/cctv-workers/v1/tags/add')
    def tags_add_handler(request):
        data = request.json
        assert data is not None
        return mockserver.make_response(json.dumps({'tag_id': 1}), status=200)

    @mockserver.json_handler('/cctv-workers/v1/tags/remove')
    def tags_remove_handler(request):
        data = request.query
        assert data is not None
        id = int(data['tag_id'])
        if id is None:
            return mockserver.make_response(status=400)
        if id not in tag_person_table:
            return mockserver.make_response(status=404)
        return mockserver.make_response(json.dumps({}), status=200)

    @mockserver.json_handler('/cctv-workers/v1/tags/persons')
    def tags_list_persons_handler(request):
        data = request.query
        assert data is not None
        id = int(data['tag_id'])
        if id is None:
            return mockserver.make_response(status=400)
        if id in tag_person_table:
            response = {'persons': tag_person_table[id]}
            return mockserver.make_response(json.dumps(response), status=200)
        response = {'persons': []}
        return mockserver.make_response(json.dumps(response), status=200)


async def test_tags_list(taxi_cctv_admin):
    response = await taxi_cctv_admin.get('/v1/tags/list')
    assert response.status_code == 200
    tags = [item['id'] for item in response.json()['tags']]
    tags.sort()
    assert tags == list(tag_person_table.keys())


@pytest.mark.parametrize(
    'input, status_code',
    [
        pytest.param({'description': 'test'}, 200, id='with description'),
        pytest.param({}, 200, id='without description'),
    ],
)
async def test_tags_add(taxi_cctv_admin, input, status_code):
    response = await taxi_cctv_admin.post('/v1/tags/add', json=input)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'input, status_code',
    [
        pytest.param({'tag_id': 0}, 200, id='correct request'),
        pytest.param({'tag_id': 100}, 404, id='no such tag'),
        pytest.param({}, 400, id='incorrect request'),
    ],
)
async def test_tags_remove(taxi_cctv_admin, input, status_code):
    response = await taxi_cctv_admin.post('/v1/tags/remove', params=input)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'input, status_code, result',
    [
        pytest.param(
            {'tag_id': 0}, 200, tag_person_table[0], id='correct request',
        ),
        pytest.param({'tag_id': 100}, 200, [], id='nonexistent tag'),
        pytest.param({}, 400, [], id='incorrect request'),
    ],
)
async def test_tags_persons(taxi_cctv_admin, input, status_code, result):
    response = await taxi_cctv_admin.get('/v1/tags/persons', params=input)
    assert response.status_code == status_code
    if status_code == 200:
        expected = []
        for item in result:
            if len(item) == 32:
                expected.append(f'person_{item[0]}{domain_suffix}')
            else:
                expected.append(item)
        assert response.json()['persons'] == expected


@pytest.mark.parametrize(
    'input, status_code, result',
    [
        pytest.param(
            {'person_id': 'person_1@yandex-team.ru'},
            200,
            [
                {'id': item}
                for item in person_tag_table[
                    '11111111111111111111111111111111'
                ]
            ],
            id='correct request 1',
        ),
        pytest.param(
            {'person_id': 'unregistered'},
            200,
            [{'id': item} for item in person_tag_table['unregistered']],
            id='correct request 2',
        ),
        pytest.param(
            {'person_id': 'person_100@yandex-team.ru'},
            200,
            [],
            id='non info on person',
        ),
        pytest.param({}, 400, [], id='incorrect request'),
    ],
)
async def test_person_tags(taxi_cctv_admin, input, status_code, result):
    response = await taxi_cctv_admin.get('/v1/person/tags', params=input)
    assert response.status_code == status_code
    if status_code == 200:
        assert response.json()['tags'] == result


@pytest.mark.parametrize(
    'input, status_code',
    [
        pytest.param(
            {'tag_id': 0, 'person_id': 'person_1@yandex-team.ru'},
            200,
            id='existing binding 1',
        ),
        pytest.param(
            {'tag_id': 0, 'person_id': 'unregistered'},
            200,
            id='existing binding 2',
        ),
        pytest.param(
            {'tag_id': 0, 'person_id': 'person_100@yandex-team.ru'},
            200,
            id='new binding',
        ),
        pytest.param(
            {'tag_id': 100, 'person_id': 'person_100@yandex-team.ru'},
            404,
            id='no such tag',
        ),
        pytest.param({'tag_id': 0}, 400, id='incorrect request 1'),
        pytest.param(
            {'person_id': 'person_100@yandex-team.ru'},
            400,
            id='incorrect request 2',
        ),
        pytest.param({}, 400, id='incorrect request 3'),
    ],
)
async def test_person_tags_add(taxi_cctv_admin, input, status_code):
    response = await taxi_cctv_admin.post('/v1/person/tag/add', json=input)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'input, status_code',
    [
        pytest.param(
            {'tag_id': 0, 'person_id': 'person_1@yandex-team.ru'},
            200,
            id='existing binding 1',
        ),
        pytest.param(
            {'tag_id': 0, 'person_id': 'unregistered'},
            200,
            id='existing binding 2',
        ),
        pytest.param(
            {'tag_id': 3, 'person_id': 'person_1@yandex-team.ru'},
            404,
            id='nonexistent binding',
        ),
        pytest.param(
            {'tag_id': 100, 'person_id': 'person_1@yandex-team.ru'},
            404,
            id='no such tag',
        ),
        pytest.param({'tag_id': 0}, 400, id='incorrect request 1'),
        pytest.param(
            {'person_id': 'person_100@yandex-team.ru'},
            400,
            id='incorrect request 2',
        ),
        pytest.param({}, 400, id='incorrect request 3'),
    ],
)
async def test_person_tags_remove(taxi_cctv_admin, input, status_code):
    response = await taxi_cctv_admin.post('/v1/person/tag/remove', json=input)
    assert response.status_code == status_code
