import aiohttp.web
import pytest


def personal_phone_id(request):
    assert request.method == 'POST'

    if request.json['value'] == '+70002455613':
        return {
            'id': 'd1206262dea04cca9da5525c176c1b90',
            'value': '+70002455613',
        }

    return {}


def personal_phone(request):
    assert request.method == 'POST'

    if request.json['id'] == 'd1206262dea04cca9da5525c176c1b90':
        return {
            'id': 'd1206262dea04cca9da5525c176c1b90',
            'value': '+70002455613',
        }

    return {}


def _personal_retrieve_id(request):
    assert request.method == 'POST'

    if request.json['id'].find('pd_id_') == 0:
        return 200, {'id': request.json['id'], 'value': request.json['id'][6:]}

    return 404, {'code': '404', 'message': 'No document with such id'}


def _personal_find_id(request):
    assert request.method == 'POST'

    return (
        200,
        {
            'id': f'pd_id_{request.json["value"]}',
            'value': request.json['value'],
        },
    )


def personal_bulk_retrieve_ids(request):
    assert request.method == 'POST'

    retrieved_items = []
    for item in request.json['items']:
        if item['id'].find('pd_id_') == 0:
            retrieved_items.append({'id': item['id'], 'value': item['id'][6:]})

    return 200, {'items': retrieved_items}


def personal_bulk_store_ids(request):
    assert request.method == 'POST'

    stored_items = []
    for item in request.json['items']:
        stored_items.append(
            {'id': 'pd_id_' + item['value'], 'value': item['value']},
        )

    return 200, {'items': stored_items}


def personal_tg_id(request):
    return _personal_retrieve_id(request)


def personal_find_pd_tg_id(request):
    return _personal_find_id(request)


def personal_tg_login(request):
    return _personal_retrieve_id(request)


@pytest.fixture
def scooter_accumulator_bot_personal_mocks(
        mock_personal,
):  # pylint: disable=C0103
    @mock_personal('/v1/phones/find')
    async def _phones_find(request):
        return aiohttp.web.json_response(personal_phone_id(request))

    @mock_personal('/v1/phones/retrieve')
    async def _phones_retrieve(request):
        return aiohttp.web.json_response(personal_phone(request))

    @mock_personal('/v1/telegram_ids/retrieve')
    async def _tg_id_retrieve(request):
        code, json = personal_tg_id(request)
        return aiohttp.web.json_response(json, status=code)

    @mock_personal('/v1/telegram_ids/find')
    async def _tg_id_find(request):
        code, json = personal_find_pd_tg_id(request)
        return aiohttp.web.json_response(json, status=code)

    @mock_personal('/v1/telegram_logins/retrieve')
    async def _tg_login_retrieve(request):
        code, json = personal_tg_login(request)
        return aiohttp.web.json_response(json, status=code)

    @mock_personal('/v1/telegram_ids/bulk_retrieve')
    async def _tg_id_bulk_retrieve(request):
        code, json = personal_bulk_retrieve_ids(request)
        return aiohttp.web.json_response(json, status=code)

    @mock_personal('/v1/telegram_logins/bulk_retrieve')
    async def _tg_login_bulk_retrieve(request):
        code, json = personal_bulk_retrieve_ids(request)
        return aiohttp.web.json_response(json, status=code)

    @mock_personal('/v1/telegram_ids/bulk_store')
    async def _tg_id_bulk_store(request):
        code, json = personal_bulk_store_ids(request)
        return aiohttp.web.json_response(json, status=code)

    @mock_personal('/v1/telegram_logins/bulk_store')
    async def _tg_login_bulk_store(request):
        code, json = personal_bulk_store_ids(request)
        return aiohttp.web.json_response(json, status=code)

    json_handlers = {}

    json_handlers['/v1/phones/find'] = _phones_find
    json_handlers['/v1/phones/retrieve'] = _phones_retrieve
    json_handlers['/v1/telegram_ids/retrieve'] = _tg_id_retrieve
    json_handlers['/v1/telegram_ids/find'] = _tg_id_find
    json_handlers['/v1/telegram_logins/retrieve'] = _tg_login_retrieve
    json_handlers['/v1/telegram_ids/bulk_retrieve'] = _tg_id_bulk_retrieve
    json_handlers[
        '/v1/telegram_logins/bulk_retrieve'
    ] = _tg_login_bulk_retrieve
    json_handlers['/v1/telegram_ids/bulk_store'] = _tg_id_bulk_store
    json_handlers['/v1/telegram_logins/bulk_store'] = _tg_login_bulk_store

    return json_handlers
