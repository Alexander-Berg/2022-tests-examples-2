# pylint: disable=invalid-name

import pytest


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_RECEIVE_START_DELAY=9999999,
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_SKIP_BEFORE_DATETIME='2000-01-01 00:00:00',
)
async def test_base(
        simple_secdist,
        hiring_st_mockserver_oplog,
        hiring_st_mockserver_ticket_update,
        mock_infranaim_api_superjob,
        mock_infranaim_api_zarplataru,
        mock_infranaim_api_rabotaru,
        call_st_handler,
        load_json,
        build_update_ticket,
):
    data = load_json('oplog.json')

    handler_st_oplog = hiring_st_mockserver_oplog(
        response_builder=lambda request: data,
    )
    handler_st_ticket_update = hiring_st_mockserver_ticket_update(
        response_builder=build_update_ticket,
    )

    handler_superjob = mock_infranaim_api_superjob()
    handler_zarplataru = mock_infranaim_api_zarplataru()
    handler_rabotaru = mock_infranaim_api_rabotaru()

    assert await call_st_handler()

    assert handler_st_oplog.has_calls
    assert handler_st_ticket_update.times_called == len(data['log'])

    assert handler_superjob.has_calls
    assert handler_zarplataru.has_calls
    assert handler_rabotaru.has_calls


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_RECEIVE_START_DELAY=9999999,
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_SKIP_BEFORE_DATETIME='2000-01-01 00:00:00',
)
async def test_infranaim_duplicates(
        simple_secdist,
        hiring_st_mockserver_oplog,
        hiring_st_mockserver_ticket_update,
        mock_infranaim_api_superjob,
        mock_infranaim_api_zarplataru,
        mock_infranaim_api_rabotaru,
        call_st_handler,
        load_json,
        build_update_ticket,
):
    """Отправка дублей валидна и просто пропускается"""
    data = load_json('oplog.json')

    handler_st_oplog = hiring_st_mockserver_oplog(
        response_builder=lambda request: data,
    )
    handler_st_ticket_update = hiring_st_mockserver_ticket_update(
        response_builder=build_update_ticket,
    )

    handler_superjob = mock_infranaim_api_superjob(response_code=409)
    handler_zarplataru = mock_infranaim_api_zarplataru(response_code=409)
    handler_rabotaru = mock_infranaim_api_rabotaru(response_code=409)

    assert await call_st_handler()

    assert handler_st_oplog.has_calls
    assert handler_st_ticket_update.times_called == len(data['log'])

    assert handler_superjob.has_calls
    assert handler_zarplataru.has_calls
    assert handler_rabotaru.has_calls


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_RECEIVE_START_DELAY=9999999,
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_SKIP_BEFORE_DATETIME='2000-01-01 00:00:00',
    HIRING_TRIGGER_ZEND_STATUS_START='new',
)
async def test_skip_done(
        simple_secdist,
        hiring_st_mockserver_oplog,
        hiring_st_mockserver_ticket_update,
        mock_infranaim_api_superjob,
        mock_infranaim_api_zarplataru,
        mock_infranaim_api_rabotaru,
        call_st_handler,
        load_json,
        build_update_ticket,
):
    data = load_json('oplog_done.json')

    handler_st_oplog = hiring_st_mockserver_oplog(
        response_builder=lambda request: data,
    )
    handler_st_ticket_update = hiring_st_mockserver_ticket_update(
        response_builder=build_update_ticket,
    )

    handler_superjob = mock_infranaim_api_superjob()
    handler_zarplataru = mock_infranaim_api_zarplataru()
    handler_rabotaru = mock_infranaim_api_rabotaru()

    assert await call_st_handler()

    assert handler_st_oplog.has_calls
    assert not handler_st_ticket_update.has_calls

    assert not handler_superjob.has_calls
    assert not handler_zarplataru.has_calls
    assert not handler_rabotaru.has_calls


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_RECEIVE_START_DELAY=9999999,
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_SKIP_BEFORE_DATETIME='4000-01-01 00:00:00',
    HIRING_TRIGGER_ZEND_STATUS_START='new',
)
async def test_skip_old(
        simple_secdist,
        hiring_st_mockserver_oplog,
        hiring_st_mockserver_ticket_update,
        mock_infranaim_api_superjob,
        mock_infranaim_api_zarplataru,
        mock_infranaim_api_rabotaru,
        call_st_handler,
        load_json,
        build_update_ticket,
):
    data = load_json('oplog.json')

    handler_st_oplog = hiring_st_mockserver_oplog(
        response_builder=lambda request: data,
    )
    handler_st_ticket_update = hiring_st_mockserver_ticket_update(
        response_builder=build_update_ticket,
    )

    handler_superjob = mock_infranaim_api_superjob()
    handler_zarplataru = mock_infranaim_api_zarplataru()
    handler_rabotaru = mock_infranaim_api_rabotaru()

    assert await call_st_handler()

    assert handler_st_oplog.has_calls
    assert not handler_st_ticket_update.has_calls

    assert not handler_superjob.has_calls
    assert not handler_zarplataru.has_calls
    assert not handler_rabotaru.has_calls


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_RECEIVE_START_DELAY=9999999,
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_SKIP_BEFORE_DATETIME='2000-01-01 00:00:00',
)
async def test_st_fail_oplog(
        mock_infranaim_api_superjob,
        mock_infranaim_api_zarplataru,
        mock_infranaim_api_rabotaru,
        call_st_handler,
        load_json,
        build_update_ticket,
):
    """Сервер hiring-st не доступен для оплога"""
    handler_superjob = mock_infranaim_api_superjob()
    handler_zarplataru = mock_infranaim_api_zarplataru()
    handler_rabotaru = mock_infranaim_api_rabotaru()

    assert not await call_st_handler()

    assert not handler_superjob.has_calls
    assert not handler_zarplataru.has_calls
    assert not handler_rabotaru.has_calls


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_RECEIVE_START_DELAY=9999999,
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_SKIP_BEFORE_DATETIME='2000-01-01 00:00:00',
)
async def test_st_fail_ticket_update(
        hiring_st_mockserver_oplog,
        mock_infranaim_api_superjob,
        mock_infranaim_api_zarplataru,
        mock_infranaim_api_rabotaru,
        call_st_handler,
        load_json,
        build_update_ticket,
):
    """Сервер hiring-st не доступен для обновления тикета"""
    handler_st_oplog = hiring_st_mockserver_oplog(
        response_builder=lambda request: load_json('oplog.json'),
    )
    handler_superjob = mock_infranaim_api_superjob()
    handler_zarplataru = mock_infranaim_api_zarplataru()
    handler_rabotaru = mock_infranaim_api_rabotaru()

    assert not await call_st_handler()

    assert handler_st_oplog.has_calls
    assert handler_superjob.has_calls, 'Первый запрос выполнялся'
    assert not handler_zarplataru.has_calls, 'Остальные уже не исполнялись'
    assert not handler_rabotaru.has_calls, 'Остальные уже не исполнялись'


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_RECEIVE_START_DELAY=9999999,
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_SKIP_BEFORE_DATETIME='2000-01-01 00:00:00',
)
async def test_st_ticket_already_done(
        hiring_st_mockserver_oplog,
        hiring_st_mockserver_ticket_update,
        mock_infranaim_api_superjob,
        mock_infranaim_api_zarplataru,
        mock_infranaim_api_rabotaru,
        call_st_handler,
        load_json,
        build_update_ticket_status_transition_error,
):
    """Тикет уже обновил статус до конечного"""

    data = load_json('oplog.json')

    handler_st_oplog = hiring_st_mockserver_oplog(
        response_builder=lambda request: data,
    )
    handler_st_ticket_update = hiring_st_mockserver_ticket_update(
        response_builder=build_update_ticket_status_transition_error,
    )

    handler_superjob = mock_infranaim_api_superjob()
    handler_zarplataru = mock_infranaim_api_zarplataru()
    handler_rabotaru = mock_infranaim_api_rabotaru()

    assert await call_st_handler()

    assert handler_st_oplog.has_calls
    assert handler_st_ticket_update.times_called == len(data['log'])

    assert handler_superjob.has_calls
    assert handler_zarplataru.has_calls
    assert handler_rabotaru.has_calls


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_RECEIVE_START_DELAY=9999999,
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_SKIP_BEFORE_DATETIME='2000-01-01 00:00:00',
)
async def test_infrazendesk_fail(
        hiring_st_mockserver_oplog,
        hiring_st_mockserver_ticket_update,
        call_st_handler,
        load_json,
        build_update_ticket,
):
    """Сервер infrazendesk не доступен"""
    handler_st_oplog = hiring_st_mockserver_oplog(
        response_builder=lambda request: load_json('oplog.json'),
    )
    handler_st_ticket_update = hiring_st_mockserver_ticket_update(
        response_builder=build_update_ticket,
    )

    assert not await call_st_handler()

    assert handler_st_oplog.has_calls
    assert not handler_st_ticket_update.has_calls
