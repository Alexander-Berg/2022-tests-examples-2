import datetime

import freezegun

import pytest

from infranaim.models.configs import external_config


FILE_ZENDESK_RESPONSE = 'zendesk_response.json'
FILE_JOBS = 'zendesk_jobs_pending.json'


@pytest.mark.parametrize('store_personal', [1, 0])
@pytest.mark.parametrize(
    'doc_name, personal_response',
    [
        ('personal_and_values', 'valid'),
        ('personal_and_values', 'invalid'),
        ('only_values', 'valid'),
        ('only_values', 'invalid'),
        ('only_personal', 'valid'),
        ('only_personal', 'invalid'),
        ('failure_personal_and_values', 'valid'),
        ('failure_personal_and_values', 'invalid'),
        ('failure_only_values', 'valid'),
        ('failure_only_values', 'invalid'),
        ('failure_only_personal', 'valid'),
        ('failure_only_personal', 'invalid'),
        ('troubled_personal_and_values', 'valid'),
        ('troubled_personal_and_values', 'invalid'),
        ('troubled_only_values', 'valid'),
        ('troubled_only_values', 'invalid'),
        ('troubled_only_personal', 'valid'),
        ('troubled_only_personal', 'invalid'),
    ]
)
def test_zendesk_jobs_success_ensurer(
        run_zendesk_jobs_success_ensurer, get_mongo,
        patch, check_troubled, check_creates_or_updates, load_json, personal,
        check_failures, check_events, store_personal, doc_name,
        personal_response,
):
    @patch('daemons.zendesk_jobs_success_ensurer._get_job_result')
    def _job(doc, log_extra):
        job_id = doc['job_status']['id']
        return {
            'job_status': load_json(FILE_ZENDESK_RESPONSE)[job_id]
        }

    @patch('infranaim.clients.personal.PreparedRequestMain.'
           '_generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal(personal_response, *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    external_config.INFRANAIM_PERSONAL.update({'store_mongo': store_personal})

    db = get_mongo
    insert_jobs = load_json(FILE_JOBS)[doc_name]
    db.zendesk_jobs_pending.insert_many(insert_jobs)
    assert db.zendesk_jobs_pending.count_documents({})
    assert not db.zendesk_tickets_to_create.count_documents({})
    assert not db.zendesk_tickets_to_update.count_documents({})
    assert not db.zendesk_jobs_failures.count_documents({})
    assert not db.statistics_events.count_documents({})

    troubles = db.zendesk_updates_troubled_tickets.count_documents({})

    run_zendesk_jobs_success_ensurer(db)

    new_troubles = db.zendesk_updates_troubled_tickets.count_documents({})

    assert not db.zendesk_jobs_pending.count_documents({})
    creations = list(db.zendesk_tickets_to_create.find())
    updates = list(db.zendesk_tickets_to_update.find())
    failures = list(db.zendesk_jobs_failures.find())
    events = list(db.statistics_events.find())

    if not doc_name.startswith('failure'):
        assert not creations
        assert not failures
        if not doc_name.startswith('troubled'):
            assert new_troubles == troubles
            assert not updates
            assert events
            check_events(
                events, store_personal, personal_response, doc_name,
            )
        else:
            assert new_troubles - 1 == troubles
            troubled = list(db.zendesk_updates_troubled_tickets.find())
            check_troubled(
                troubled, store_personal, personal_response, doc_name,
            )
            assert updates
            check_creates_or_updates(
                updates, store_personal, personal_response,
                doc_name, ticket_type='update'
            )

    else:
        assert creations
        check_creates_or_updates(
            creations, store_personal, personal_response,
            doc_name, ticket_type='create'
        )
        assert failures
        check_failures(
            failures, store_personal, personal_response, doc_name,
        )
        assert updates
        check_creates_or_updates(
            updates, store_personal, personal_response,
            doc_name, ticket_type='update'
        )
        assert new_troubles == troubles
        assert not events


@freezegun.freeze_time('2020-1-1T12:00:00')
def test_check_empty_jobs(
        run_zendesk_jobs_success_ensurer,
        get_mongo,
        patch,
        check_troubled,
        check_creates_or_updates,
        load_json,
        personal,
        check_failures,
        check_events,
):
    external_config.INFRANAIM_PERSONAL.update({'store_mongo': 1})
    @patch('daemons.zendesk_jobs_success_ensurer._get_job_result')
    def _job(doc, log_extra):
        job_id = doc['job_status']['id']
        return {
            'job_status': load_json(FILE_ZENDESK_RESPONSE)[job_id]
        }

    @patch('infranaim.clients.personal.PreparedRequestMain.'
           '_generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal('valid', *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    db = get_mongo
    insert_jobs = load_json(FILE_JOBS)['empty_rotten_jobs']
    db.zendesk_jobs_pending.insert_many(insert_jobs)

    run_zendesk_jobs_success_ensurer(db)

    left_ids = [
        item['_id']
        for item in db.zendesk_jobs_pending.find()
    ]
    assert left_ids
    for doc in insert_jobs:
        if not doc.get('created_at'):
            assert doc['_id'] in left_ids
        elif (
                datetime.datetime.utcnow() - doc['created_at'].replace(
                tzinfo=None
            )
        ).seconds > 120 and 'tickets' in doc:
            assert doc['_id'] in left_ids


@freezegun.freeze_time('2020-1-1T12:00:00')
def test_check_hung_jobs(
        run_zendesk_jobs_success_ensurer,
        get_mongo,
        patch,
        check_troubled,
        check_creates_or_updates,
        load_json,
        personal,
        check_failures,
        check_events,
):
    external_config.INFRANAIM_PERSONAL.update({'store_mongo': 1})
    @patch('daemons.zendesk_jobs_success_ensurer._get_job_result')
    def _job(doc, log_extra):
        job_id = doc['job_status']['id']
        return {
            'job_status': load_json(FILE_ZENDESK_RESPONSE)[job_id]
        }

    @patch('infranaim.clients.personal.PreparedRequestMain.'
           '_generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal('valid', *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    db = get_mongo
    insert_jobs = load_json(FILE_JOBS)['hung_jobs']
    db.zendesk_jobs_pending.insert_many(insert_jobs)

    assert not db.zendesk_tickets_to_create.count_documents({})
    run_zendesk_jobs_success_ensurer(db)

    ticket_tags = {
        item['data']['tags'][0]
        for item in db.zendesk_tickets_to_create.find()
    }
    assert ticket_tags
    assert db.zendesk_jobs_failures.count_documents({})
    left_ids = [
        item['_id']
        for item in db.zendesk_jobs_pending.find()
    ]
    assert left_ids
    for doc in insert_jobs:
        if (
            datetime.datetime.utcnow() - doc['progressed_at'].replace(
                tzinfo=None
            )
        ).seconds <= 300:
            assert doc['_id'] in left_ids
        else:
            assert doc['_id'] not in left_ids

    response = load_json(FILE_ZENDESK_RESPONSE)
    tags_reinserted = set()
    for failed_job in db.zendesk_jobs_failures.find():
        failed_response = response[failed_job['job_status']['id']]
        progress = failed_response['progress']
        reinserted = [
            ticket['tags'][0]
            for ticket in failed_job['tickets'][progress-1:]
        ]
        assert len(set(reinserted)) == len(reinserted)
        tags_reinserted.update(set(reinserted))
    assert ticket_tags - tags_reinserted == set()


@pytest.fixture
def check_events(check_personal_dict):
    def _do_it(events, store_personal, personal_response, doc_name):
        for event in events:
            if event['type'] == 'create_ticket':
                data = event['doc']
            else:
                data = event['doc']['data']
            check_personal_dict(
                data, store_personal, personal_response, doc_name)
    return _do_it


@pytest.fixture
def check_failures(check_custom_fields):
    def _do_it(failures, store_personal, personal_response, doc_name):
        for failure in failures:
            tickets = failure['tickets']
            resent_tickets = failure['resent_tickets']
            for ticket in tickets:
                check_custom_fields(
                    ticket, store_personal, personal_response, doc_name,
                )
            for resent_ticket in resent_tickets:
                check_custom_fields(
                    resent_ticket, store_personal,
                    personal_response, doc_name,
                )
    return _do_it


@pytest.fixture
def check_troubled(check_custom_fields):
    def _do_it(troubled, store_personal, personal_response, doc_name):
        for trouble in troubled:
            ticket = trouble['ticket']
            check_custom_fields(
                ticket, store_personal, personal_response, doc_name,
            )
    return _do_it
