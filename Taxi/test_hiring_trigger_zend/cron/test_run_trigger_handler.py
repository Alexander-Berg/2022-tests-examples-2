# pylint: disable=redefined-outer-name
import pytest

from hiring_trigger_zend.generated.cron import run_cron


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_FROM_BACKGROUND_TASKS_TO_CRON=True,
)
async def test_run_trigger_handler_use(
        hiring_st_mockserver_oplog,
        hiring_st_mockserver_ticket_update,
        mock_infranaim_api_superjob,
        mock_infranaim_api_zarplataru,
        mock_infranaim_api_rabotaru,
        load_json,
        build_update_ticket,
):
    data = load_json('oplog.json')
    handler_st_oplog = hiring_st_mockserver_oplog(
        response_builder=lambda request: data,
    )
    hiring_st_mockserver_ticket_update(response_builder=build_update_ticket)

    mock_infranaim_api_superjob()
    mock_infranaim_api_zarplataru()
    mock_infranaim_api_rabotaru()

    await run_cron.main(
        ['hiring_trigger_zend.crontasks.run_trigger_handler', '-t', '0'],
    )

    assert handler_st_oplog.has_calls


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_FROM_BACKGROUND_TASKS_TO_CRON=False,
    HIRING_TRIGGER_ZEND_RECIVE_START_DELAY=9999999,
)
async def test_run_trigger_handler_not_use(
        hiring_st_mockserver_oplog,
        hiring_st_mockserver_ticket_update,
        mock_infranaim_api_superjob,
        mock_infranaim_api_zarplataru,
        mock_infranaim_api_rabotaru,
        load_json,
        build_update_ticket,
):
    data = load_json('oplog.json')
    handler_st_oplog = hiring_st_mockserver_oplog(
        response_builder=lambda request: data,
    )
    hiring_st_mockserver_ticket_update(response_builder=build_update_ticket)

    mock_infranaim_api_superjob()
    mock_infranaim_api_zarplataru()
    mock_infranaim_api_rabotaru()

    await run_cron.main(
        ['hiring_trigger_zend.crontasks.run_trigger_handler', '-t', '0'],
    )

    assert not handler_st_oplog.has_calls


@pytest.mark.config(
    HIRING_TRIGGER_ZEND_QUEUE_ID='TEST',
    HIRING_TRIGGER_ZEND_FROM_BACKGROUND_TASKS_TO_CRON=True,
    HIRING_TRIGGER_ZEND_ENABLE_HIRING_API=True,
    HIRING_TRIGGER_ZEND_SKIP_BEFORE_DATETIME='2019-01-01 00:00:00',
)
@pytest.mark.usefixtures('mock_hiring_api_bulk_create')
async def test_send_to_hiring_api(
        hiring_st_mockserver_oplog,
        hiring_st_mockserver_ticket_update,
        load_json,
        build_update_ticket,
):
    data = load_json('oplog.json')
    hiring_st_mockserver_oplog(response_builder=lambda request: data)
    hiring_st_mockserver_ticket_update(response_builder=build_update_ticket)

    await run_cron.main(
        ['hiring_trigger_zend.crontasks.run_trigger_handler', '-t', '0'],
    )
