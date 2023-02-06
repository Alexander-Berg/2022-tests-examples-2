from daemons import deaf_morpheus
from daemons import email_sender
from daemons import SUPER_CREATOR
from daemons import SUPER_UPDATER
from daemons import synch_taxiparks_zendesk_taximeter
from daemons import zendesk2mongo
from daemons import zendesk_jobs_success_ensurer

from infranaim.conftest import *


@pytest.fixture
def run_deaf_morpheus():
    def _run(db_mongo):
        result = deaf_morpheus.do_iteration(
            db_=db_mongo,
        )
        return result
    return _run


@pytest.fixture
def run_email_sender():
    def _run(db_mongo):
        result = email_sender.do_iteration(
            db=db_mongo,
        )
        return result
    return _run


@pytest.fixture
def run_creator():
    def _run(db_mongo):
        result = SUPER_CREATOR.do_iteration(db_mongo)
        return result
    return _run


@pytest.fixture
def run_updater():
    def _run(db_mongo):
        result = SUPER_UPDATER.do_iteration(db_mongo)
        return result
    return _run


@pytest.fixture
def run_synch_parks():
    def _run(db_mongo):
        result = synch_taxiparks_zendesk_taximeter.do_iteration(
            db_mongo,
        )
        return result
    return _run


@pytest.fixture
def run_zendesk2mongo():
    def _run(db_mongo):
        result = zendesk2mongo.do_iteration(db_mongo, 1000)
        return result
    return _run


@pytest.fixture
def run_zendesk_jobs_success_ensurer():
    def _run(db_mongo):
        result = zendesk_jobs_success_ensurer.do_iteration(db_mongo)
        return result
    return _run


@pytest.fixture
def check_jobs():
    def _do_it(
            mongo_, store_personal, personal_response,
            doc_name, ticket_type
    ):
        if ticket_type == 'create':
            docs = list(mongo_.zendesk_tickets_to_create.find())
        else:
            docs = list(mongo_.zendesk_tickets_to_update.find())
        jobs = list(mongo_.zendesk_jobs_pending.find())
        if personal_response != 'valid' and doc_name == 'only_personal':
            assert len(docs) == 1
            assert not jobs
        else:
            assert not docs
            assert len(jobs) == 1

            tickets = jobs[0]['tickets']
            assert len(tickets) == 1
            ticket = tickets[0]
            fields = {
                item['id']: item
                for item in ticket['custom_fields']
            }
            phone = fields.get(30557445)
            pd_phone = fields.get(360005536320)
            driver_license = fields.get(30148269)
            pd_license = fields.get(360005536340)
            yandex_login = fields.get(360013749839)
            pd_yandex_login = fields.get(360013719259)
            if personal_response == 'valid':
                for field in (pd_phone, pd_license, pd_yandex_login):
                    assert field['value']
                if store_personal:
                    for field in (phone, driver_license, yandex_login):
                        assert field['value']
            else:
                if not store_personal and doc_name != 'only_personal':
                    for field in (phone, driver_license, yandex_login):
                        assert field['value']
    return _do_it
