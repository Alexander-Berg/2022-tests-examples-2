import copy
import uuid

import pytest

from test_hiring_sf_events import conftest


@conftest.main_configuration
@pytest.mark.usefixtures('fill_initial_data')  # noqa: F405
async def test_initial(get_all_events):
    events = get_all_events()
    assert len(events) == conftest.DOCUMENTS_COUNT


@conftest.main_configuration
async def test_send_event(post_document, generate_documents, get_all_events):
    document = next(generate_documents())

    # Checking idempotence
    for _ in range(5):
        await post_document(document)

    # Check broken post request
    invalid_document = copy.deepcopy(document)
    invalid_document['payload']['new_extremely_important_field'] = '10/10'
    res = await post_document(invalid_document, status=200)
    assert res['code'] == 'OK'

    # Check if doc in DB
    all_documents = get_all_events()
    assert len(all_documents) == 2
    assert len(all_documents.not_processed) == 2
    db_document = all_documents.not_processed[0]
    assert uuid.UUID(hex=db_document.task_id) == uuid.UUID(
        hex=document['task_id'],
    )
    assert db_document.status == document['status']


@pytest.mark.config(HIRING_SF_EVENTS_API_ENABLED=False)  # noqa: F405
@conftest.main_configuration
async def test_disabled(generate_documents, post_document, get_all_events):
    document = next(generate_documents())
    response = await post_document(document, status=400)
    assert response['code'] == 'FUNCTIONALITY_DISABLED'
