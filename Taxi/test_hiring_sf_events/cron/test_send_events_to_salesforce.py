# pylint: disable=redefined-outer-name,
# pylint: disable=unused-variable
import pytest

from hiring_sf_events.generated.cron import run_cron as run_cron_module
from test_hiring_sf_events import conftest

CRON_ADDRESS = 'hiring_sf_events.crontasks.send_events_to_salesforce'


async def run_cron():
    return await run_cron_module.main([CRON_ADDRESS, '-t', '0'])


@conftest.main_configuration
@pytest.mark.usefixtures('fill_initial_data')  # noqa: F405
async def test_send_events_to_salesforce(mockserver, get_all_events):
    first_failed = False

    # pylint: disable=unused-variable
    @mockserver.json_handler(
        r'/salesforce/services/data/v50.0/sobjects/Task/(?P<task_id>\w+)',
        regex=True,
    )
    async def salesforce_create_task_handler(request, task_id):
        nonlocal first_failed
        if first_failed:
            response = mockserver.make_response(status=204)
        else:
            response = mockserver.make_response(
                json=[{'message': 'some', 'errorCode': 'some'}], status=400,
            )

        first_failed = True
        return response

    events = get_all_events()
    assert len(events.not_processed) == len(events) == conftest.DOCUMENTS_COUNT

    await run_cron()

    events = get_all_events()
    assert len(events.ignored) == 1
    assert len(events.failures) == 1
    assert not events.not_processed


@conftest.main_configuration
async def test_gaps(generate_documents, post_document, get_all_events):
    document = next(generate_documents())

    before = None
    after = []
    for i, status in enumerate(conftest.STATUSES):
        document = document.copy()
        document['status'] = status
        if i == 1:
            before = document
        else:
            after.append(document)

    await post_document(before)
    await run_cron()

    for doc in after:
        await post_document(doc)
    await run_cron()

    events = get_all_events()
    assert len(events) == len(conftest.STATUSES)
    assert not events.not_processed
    assert len(events.sent) == len(conftest.STATUSES) - 1
    assert len(events.ignored) == 1


@conftest.main_configuration
async def test_many_events(
        generate_documents, post_document, get_all_events, salesforce_auth,
):
    document = next(generate_documents())

    for i, status in enumerate(conftest.STATUSES):
        document['status'] = status
        await post_document(document)

    await run_cron()

    document['lead_id'] = 'test'
    await post_document(document)
    await run_cron()

    events = get_all_events()
    assert len(events) == len(conftest.STATUSES) + 1
    assert not events.not_processed
    assert len(events.sent) == len(conftest.STATUSES) + 1
    assert not events.ignored
    # check, that we only logged in once for each cron run
    assert salesforce_auth.times_called == 2


@pytest.mark.config(HIRING_SF_EVENTS_SEND_CALLRESULTS=False)  # noqa: F405
@conftest.main_configuration
async def test_disabled(generate_documents, post_document, cron_runner):
    with pytest.raises(RuntimeError):
        document = next(generate_documents())
        await post_document(document)
        await cron_runner.send_events_to_salesforce()


@pytest.mark.parametrize('response', ['404', '400', '500'])
@conftest.main_configuration
async def test_salesforce_fail_responses_handling(
        mockserver,
        generate_documents,
        post_document,
        load_json,
        get_all_events,
        response,
):
    response = load_json('salesforce_responses.json')[response]

    # pylint: disable=unused-variable
    @mockserver.json_handler(
        r'/salesforce/services/data/v50.0/sobjects/Task/(?P<task_id>\w+)',
        regex=True,
    )
    async def salesforce_create_task_handler(request, task_id):
        return mockserver.make_response(**response)

    doc = next(generate_documents())
    await post_document(doc)
    await run_cron()
    events = get_all_events()
    assert len(events.ignored) == 1
    assert len(events.failures) == 1
    assert not events.not_processed
