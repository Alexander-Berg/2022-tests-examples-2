import pytest

from taxi.core import async
from taxi.core import db
from taxi.internal import banner_manager
from taxi.internal import distlock

TEST_BANNER_NAME = 'test_banner'


@pytest.inline_callbacks
def test_deploy_banner():
    yield banner_manager.deploy_banner(
        TEST_BANNER_NAME, global_banner=True, users_list=[], send_push=False,
        log_extra=None
    )
    banner = yield db.fullscreen_banners.find_one({
        'name': TEST_BANNER_NAME
    })
    assert 'deploy_status' not in banner


@pytest.inline_callbacks
def test_deploy_user_banner(monkeypatch, patch):
    users_list = ['user%d' % i for i in xrange(93)]

    @patch('taxi.core.async.sleep')
    @async.inline_callbacks
    def sleep(timeout):
        yield

    @patch('taxi.internal.banner_manager._remove_deployed_banners')
    @async.inline_callbacks
    def remove_deployed_banners(banner_name, log_extra=None):
        yield

    monkeypatch.setattr(banner_manager, '_USER_ID_BATCH_SIZE', 10)

    yield distlock.acquire(
        banner_manager.LOCK_NAME, banner_manager.LOCK_TIME,
        owner=TEST_BANNER_NAME
    )
    yield banner_manager._deploy_user_banner(
        TEST_BANNER_NAME, users_list, log_extra=None
    )
    total_slept = sum(i['args'][0] for i in sleep.calls)
    assert total_slept == 9

    assert remove_deployed_banners.calls == [
        {
            'args': ('test_banner',),
            'kwargs': {'log_extra': None},
        }
    ]
    user_banners = yield _fetch_user_banners()

    assert len(user_banners) == 93
    deployed_for = set(
        key for key, value in user_banners.iteritems()
        if TEST_BANNER_NAME in value
    )
    assert deployed_for == set(users_list)


@pytest.inline_callbacks
def test_remove_deployed_banners(monkeypatch, patch):
    monkeypatch.setattr(banner_manager, '_USER_ID_BATCH_SIZE', 10)

    @patch('taxi.core.async.sleep')
    @async.inline_callbacks
    def sleep(timeout):
        yield

    user_banners_initial = yield _fetch_user_banners()

    # populate test banner users
    bulk = db.user_fsbanners.initialize_unordered_bulk_op()
    for i in xrange(1000):
        bulk.find({'_id': 'user%d' % i}).upsert().update({
            '$addToSet': {'banners_enabled': TEST_BANNER_NAME}
        })
    bulk.execute()

    yield distlock.acquire(
        banner_manager.LOCK_NAME, banner_manager.LOCK_TIME,
        owner=TEST_BANNER_NAME
    )
    yield banner_manager._remove_deployed_banners(
        TEST_BANNER_NAME, log_extra=None
    )
    total_slept = sum(i['args'][0] for i in sleep.calls)
    assert total_slept == 100

    user_banners_final = yield _fetch_user_banners()

    assert user_banners_initial == user_banners_final


@async.inline_callbacks
def _fetch_user_banners():
    docs = yield db.user_fsbanners.find().run()
    result = {}
    for doc in docs:
        banners_enabled = sorted(doc.get('banners_enabled', []))
        if banners_enabled:
            result[doc['_id']] = banners_enabled
    async.return_value(result)
