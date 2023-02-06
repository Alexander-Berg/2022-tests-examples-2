import pytest


@pytest.fixture(name='acquire_ticket_lock')
def _acquire_ticket_lock(taxi_cargo_crm):
    async def wrapper(uid, ticket_id):
        url = '/functions/ticket-acquire-lock-by-uid'
        reqbody = {'yandex_uid': uid, 'ticket_id': ticket_id}
        return await _do_request(taxi_cargo_crm, url, reqbody)

    return wrapper


@pytest.fixture(name='find_ticket_lock')
def _find_ticket_lock(taxi_cargo_crm):
    async def wrapper(uid):
        url = '/functions/ticket-find-lock-by-uid'
        reqbody = {'yandex_uid': uid}
        return await _do_request(taxi_cargo_crm, url, reqbody)

    return wrapper


@pytest.fixture(name='release_ticket_lock')
def _release_ticket_lock(taxi_cargo_crm):
    async def wrapper(ticket_id):
        url = '/functions/ticket-release-lock-by-id'
        reqbody = {'ticket_id': ticket_id}
        return await _do_request(taxi_cargo_crm, url, reqbody)

    return wrapper


async def _do_request(taxi_cargo_crm, url, request_body):
    response = await taxi_cargo_crm.post(url, json=request_body)
    assert response.status_code == 200
    return response.json()
