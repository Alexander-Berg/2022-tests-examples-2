# flake8: noqa
# pylint: disable=unused-variable
import pytest


@pytest.fixture
def mongodb_collections():
    return ['admin_confirmations']


def test_not_requested_collection_are_missing_in_mongodb(mongodb):
    can_be_accessed = mongodb.admin_confirmations
    with pytest.raises(AttributeError):
        cannot_be_accessed1 = mongodb.accepted_eulas
    with pytest.raises(AttributeError):
        cannot_be_accessed2 = mongodb.adjust_users


def test_not_requested_collection_are_missing_in_db(db):
    can_be_accessed = db.admin_confirmations
    with pytest.raises(AttributeError):
        cannot_be_accessed1 = db.accepted_eulas
    with pytest.raises(AttributeError):
        cannot_be_accessed2 = db.adjust_users


@pytest.mark.mongodb_collections('accepted_eulas')
def test_mark_enables_access_to_collection_in_mongodb(mongodb):
    can_be_accessed1 = mongodb.admin_confirmations
    can_be_accessed2 = mongodb.accepted_eulas
    with pytest.raises(AttributeError):
        cannot_be_accessed = mongodb.adjust_users


@pytest.mark.mongodb_collections('accepted_eulas')
def test_mark_enables_access_to_collection_in_db(db):
    can_be_accessed1 = db.admin_confirmations
    can_be_accessed2 = db.accepted_eulas
    with pytest.raises(AttributeError):
        cannot_be_accessed = db.adjust_users
