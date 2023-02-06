from __future__ import unicode_literals

import pytest

from taxi.core import db
from taxi_maintenance.stuff import cleanup_user_chats


@pytest.mark.now('2018-01-03T00:00:00')
@pytest.mark.config(CLOSE_VISIBLE_CHATS_LEGACY_MODE=False)
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_cleanup_after_day():
    yield cleanup_user_chats.do_stuff()

    must_be_closed_after_one_day = yield db.user_chat_messages.find_one(
            {'_id': 'must_be_closed_after_one_day'}
    )

    must_be_closed_after_7_days = yield db.user_chat_messages.find_one(
            {'_id': 'must_be_closed_after_7_days'}
    )

    must_not_be_closed = yield db.user_chat_messages.find_one(
            {'_id': 'must_not_be_closed'}
    )

    assert must_be_closed_after_7_days['open']
    assert not must_be_closed_after_7_days['close_ticket']

    assert not must_be_closed_after_one_day['open']
    assert must_be_closed_after_one_day['close_ticket']

    assert must_not_be_closed['open']
    assert not must_not_be_closed['close_ticket']


@pytest.mark.now('2018-01-10T00:00:00')
@pytest.mark.config(CLOSE_VISIBLE_CHATS_LEGACY_MODE=False)
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_cleanup_after_7_days():
    yield cleanup_user_chats.do_stuff()

    must_be_closed_after_one_day = yield db.user_chat_messages.find_one(
            {'_id': 'must_be_closed_after_one_day'}
    )

    must_be_closed_after_7_days = yield db.user_chat_messages.find_one(
            {'_id': 'must_be_closed_after_7_days'}
    )

    must_not_be_closed = yield db.user_chat_messages.find_one(
            {'_id': 'must_not_be_closed'}
    )

    assert not must_be_closed_after_7_days['open']
    assert must_be_closed_after_7_days['close_ticket']

    assert not must_be_closed_after_one_day['open']
    assert must_be_closed_after_one_day['close_ticket']

    assert must_not_be_closed['open']
    assert not must_not_be_closed['close_ticket']


@pytest.mark.now('2018-01-10T00:00:00')
@pytest.mark.config(CLOSE_VISIBLE_CHATS_LEGACY_MODE=True)
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_legacy_cleanup():
    yield cleanup_user_chats.do_stuff()

    must_be_closed_in_legacy_mode = yield db.user_chat_messages.find_one(
        {'_id': 'must_be_closed_in_legacy_mode'}
    )

    assert not must_be_closed_in_legacy_mode['open']
    assert must_be_closed_in_legacy_mode['close_ticket']


@pytest.mark.config(CLOSE_VISIBLE_CHATS_IN_PY2=False)
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_no_cleanup():
    chats = yield db.user_chat_messages.find().sort([('_id', db.ASC)]).run()

    yield cleanup_user_chats.do_stuff()

    cleaned_chats = yield db.user_chat_messages.find().sort([('_id', db.ASC)]).run()

    assert chats == cleaned_chats
