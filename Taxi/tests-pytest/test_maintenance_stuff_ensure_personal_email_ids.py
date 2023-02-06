import pytest

from taxi.core import async
from taxi.core import db
from taxi_maintenance.stuff import ensure_personal_email_ids


@pytest.mark.config(ENSURE_PERSONAL_EMAILS_IDS_SETTINGS={
    'enabled': True,
    'chunk_size': 1000,
    'sleep_time': 5,
})
@pytest.mark.now('2018-05-22T11:00:00')
@pytest.inline_callbacks
def test_do_stuff(patch):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        assert data_type == 'emails'
        assert values == ['email_2@yandex.ru']
        yield
        async.return_value([
            {'id': 'personal_email_id_2', 'email': 'email_2@yandex.ru'}
        ])

    yield ensure_personal_email_ids.do_stuff()
    user_emails = yield db.user_emails.find({}).run()
    assert len(user_emails) == 2
    for user_email in user_emails:
        assert user_email['personal_email_id'] is not None


@pytest.mark.now('2018-05-22T11:00:00')
@pytest.inline_callbacks
def test_do_stuff_disabled(patch):
    @patch('taxi.external.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, values, validate=True, log_extra=None):
        yield
        assert False

    yield ensure_personal_email_ids.do_stuff()
    user_email = yield db.user_emails.find_one({'_id': 'user_email_id_2'})
    assert 'personal_email_id' not in user_email
