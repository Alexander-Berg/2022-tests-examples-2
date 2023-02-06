import base64
import hashlib
import hmac

import pytest

from taxi.core import async
from taxi.core import db
from taxi.external import personal
from taxi.internal import dbh


@pytest.mark.config(PERSONAL_SERVICE_ENABLED=False)
@pytest.inline_callbacks
def test_create_simple():
    new_phone = yield dbh.user_phones.Doc.create('+72222222222')
    db_phone = yield db.user_phones.find_one({'phone': '+72222222222'})
    assert new_phone == db_phone
    assert 'personal_phone_id' not in new_phone
    assert db_phone['phone_hash'] is not None
    assert db_phone['phone_salt'] is not None
    assert db_phone['phone_hash'] == hmac.new(
        base64.b64decode(db_phone['phone_salt']) + 'secdist_salt',
        db_phone['phone'], hashlib.sha256
    ).hexdigest()


@pytest.mark.config(PERSONAL_SERVICE_ENABLED=False)
@pytest.inline_callbacks
def test_create_duplicate():
    new_phone = yield dbh.user_phones.Doc.create('+71111111111')
    db_phone = yield db.user_phones.find_one({'phone': '+71111111111'})
    assert new_phone == db_phone
    assert 'personal_phone_id' not in new_phone
    assert 'phone_hash' not in db_phone
    assert 'phone_salt' not in db_phone


@pytest.inline_callbacks
def test_create_personal_success(patch):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_phones_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        assert value == '+72222222222'
        yield
        async.return_value({'id': 'phone_id', 'phone': '+72222222222'})

    new_phone = yield dbh.user_phones.Doc.create('+72222222222')
    db_phone = yield db.user_phones.find_one({'phone': '+72222222222'})
    assert new_phone == db_phone
    assert new_phone['personal_phone_id'] == 'phone_id'
    assert db_phone['phone_hash'] is not None
    assert db_phone['phone_salt'] is not None
    assert db_phone['phone_hash'] == hmac.new(
        base64.b64decode(db_phone['phone_salt']) + 'secdist_salt',
        db_phone['phone'], hashlib.sha256
    ).hexdigest()


@pytest.mark.parametrize('personal_error', [
    personal.BaseError,
    personal.BadRequestError,
    personal.NotFoundError,
    personal.PersonalDisabledError,
])
@pytest.inline_callbacks
def test_create_personal_fail(patch, personal_error):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_phones_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        yield
        raise personal_error

    new_phone = yield dbh.user_phones.Doc.create('+72222222222')
    db_phone = yield db.user_phones.find_one({'phone': '+72222222222'})
    assert new_phone == db_phone
    assert 'personal_phone_id' not in new_phone
    assert db_phone['phone_hash'] is not None
    assert db_phone['phone_salt'] is not None
    assert db_phone['phone_hash'] == hmac.new(
        base64.b64decode(db_phone['phone_salt']) + 'secdist_salt',
        db_phone['phone'], hashlib.sha256
    ).hexdigest()


@pytest.inline_callbacks
def test_create_personal_duplicate(patch):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_phones_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'phones'
        assert value == '+71111111111'
        yield
        async.return_value({'id': 'phone_id', 'phone': '+71111111111'})

    new_phone = yield dbh.user_phones.Doc.create('+71111111111')
    db_phone = yield db.user_phones.find_one({'phone': '+71111111111'})
    assert new_phone == db_phone
    assert 'personal_phone_id' not in new_phone
    assert 'phone_hash' not in db_phone
    assert 'phone_salt' not in db_phone
