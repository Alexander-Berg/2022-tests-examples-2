import datetime
import typing as tp

import pytest

from taxi.util import dates

from replication.rule_keeper import deploy as rule_keeper_deploy

NOW = '2020-02-10T00:00:00'
NOW_DT = dates.parse_timestring(NOW, timezone='UTC')
# pylint: disable=protected-access


@pytest.mark.now(NOW)
async def test_rules_reload_handle(
        replication_app, monkeypatch, _patch_collection_update,
):

    test_coll = replication_app.db.replication_rules_deploy
    assert not await test_coll.find().to_list(None)

    rule_deploying_info: rule_keeper_deploy.RuleDeployingManager = (
        rule_keeper_deploy.RuleDeployingManager(
            replication_app.db.replication_rules_deploy,
            replication_app.config,
        )
    )
    await rule_deploying_info.actualize_host_deploy_time()
    docs = await test_coll.find().to_list(None)
    assert len(docs) == 1
    doc = docs[0]
    assert doc
    assert doc == {
        '_id': 'test_host_yandex_net',
        rule_keeper_deploy._LAST_RELEASE_KEY: datetime.datetime.utcnow(),
        rule_keeper_deploy._METADATA_STATUS_FIELD: (
            rule_keeper_deploy.MetadataCronStatuses.WAITING.value
        ),
    }


@pytest.fixture
async def _patch_collection_update(monkeypatch):
    date_to_set = datetime.datetime.utcnow()
    old_get_update = rule_keeper_deploy._get_coll_update

    def patched_get_updates():
        update = old_get_update()
        patched_update = update.copy()
        del patched_update['$currentDate']
        patched_update['$set'][
            rule_keeper_deploy._LAST_RELEASE_KEY
        ] = date_to_set
        return patched_update

    monkeypatch.setattr(
        rule_keeper_deploy, '_get_coll_update', patched_get_updates,
    )


def _validate_and_get_entity(
        release_time, cron_status, entity_factory, empty_entity_factory,
):
    if release_time is None and cron_status is None:
        entity = empty_entity_factory()
    else:
        if release_time and cron_status:
            entity = entity_factory(release_time, cron_status)
        else:
            raise ValueError('Wrong parameters for testcase')
    return entity


def _empty_db_factory():
    return []


def _empty_cache_factory():
    return None


def _make_testcase(
        should_refresh,
        db_release_time=None,
        db_cron_status=None,
        cache_release_time=None,
        cache_cron_status=None,
        expected_cache_release_time=None,
        expected_cache_cron_status=None,
):
    database_state = _validate_and_get_entity(
        db_release_time, db_cron_status, _make_db_state, _empty_db_factory,
    )
    before_cache_state = _validate_and_get_entity(
        cache_release_time,
        cache_cron_status,
        _make_deploy_info,
        _empty_cache_factory,
    )
    after_cache_state = _validate_and_get_entity(
        expected_cache_release_time,
        expected_cache_cron_status,
        _make_deploy_info,
        _empty_cache_factory,
    )
    return (
        database_state,
        before_cache_state,
        after_cache_state,
        should_refresh,
    )


def _make_db_state(release_time, cron_status):
    return [
        {
            '_id': 'test_host_yandex_net',
            rule_keeper_deploy._LAST_RELEASE_KEY: release_time,
            rule_keeper_deploy._METADATA_STATUS_FIELD: cron_status.value,
        },
    ]


def _make_deploy_info(release_time, cron_status):
    return rule_keeper_deploy.RuleDeployInfo(
        hostname='test_host_yandex_net',
        last_release_time=release_time,
        metadata_cron_status=cron_status,
        downloaded_resources=[],
    )


_BACKWARDS_DT = NOW_DT - datetime.timedelta(hours=3)
_ADVANCED_DT = NOW_DT + datetime.timedelta(hours=3)

cron_statuses: tp.Type[
    rule_keeper_deploy.MetadataCronStatuses
] = rule_keeper_deploy.MetadataCronStatuses


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'database_state, before_deploy, expected_after_deploy, should_refresh',
    [
        _make_testcase(should_refresh=False),
        _make_testcase(
            should_refresh=False,
            cache_release_time=NOW_DT,
            cache_cron_status=cron_statuses.DONE,
        ),
        _make_testcase(
            should_refresh=False,
            db_release_time=_ADVANCED_DT,
            db_cron_status=cron_statuses.WAITING,
            expected_cache_release_time=_ADVANCED_DT,
            expected_cache_cron_status=cron_statuses.WAITING,
        ),
        _make_testcase(
            should_refresh=False,
            db_release_time=_ADVANCED_DT,
            db_cron_status=cron_statuses.WAITING,
            cache_release_time=NOW_DT,
            cache_cron_status=cron_statuses.WAITING,
            expected_cache_release_time=_ADVANCED_DT,
            expected_cache_cron_status=cron_statuses.WAITING,
        ),
        _make_testcase(
            should_refresh=True,
            db_release_time=_ADVANCED_DT,
            db_cron_status=cron_statuses.DONE,
            cache_release_time=NOW_DT,
            cache_cron_status=cron_statuses.WAITING,
            expected_cache_release_time=_ADVANCED_DT,
            expected_cache_cron_status=cron_statuses.DONE,
        ),
        _make_testcase(
            should_refresh=True,
            db_release_time=_ADVANCED_DT,
            db_cron_status=cron_statuses.DONE,
            cache_release_time=NOW_DT,
            cache_cron_status=cron_statuses.DONE,
            expected_cache_release_time=_ADVANCED_DT,
            expected_cache_cron_status=cron_statuses.DONE,
        ),
        _make_testcase(
            should_refresh=True,
            db_release_time=_ADVANCED_DT,
            db_cron_status=cron_statuses.UPDATED,
            cache_release_time=NOW_DT,
            cache_cron_status=cron_statuses.UPDATED,
            expected_cache_release_time=_ADVANCED_DT,
            expected_cache_cron_status=cron_statuses.UPDATED,
        ),
        _make_testcase(
            should_refresh=False,
            db_release_time=_ADVANCED_DT,
            db_cron_status=cron_statuses.WAITING,
            cache_release_time=NOW_DT,
            cache_cron_status=cron_statuses.UPDATED,
            expected_cache_release_time=_ADVANCED_DT,
            expected_cache_cron_status=cron_statuses.WAITING,
        ),
        _make_testcase(
            should_refresh=True,
            db_release_time=_ADVANCED_DT,
            db_cron_status=cron_statuses.DONE,
            cache_release_time=NOW_DT,
            cache_cron_status=cron_statuses.UPDATED,
            expected_cache_release_time=_ADVANCED_DT,
            expected_cache_cron_status=cron_statuses.DONE,
        ),
        _make_testcase(
            should_refresh=False,
            db_release_time=_ADVANCED_DT,
            db_cron_status=cron_statuses.DONE,
            cache_release_time=_ADVANCED_DT,
            cache_cron_status=cron_statuses.DONE,
            expected_cache_release_time=_ADVANCED_DT,
            expected_cache_cron_status=cron_statuses.DONE,
        ),
        _make_testcase(
            should_refresh=True,
            db_release_time=_ADVANCED_DT,
            db_cron_status=cron_statuses.UPDATED,
            cache_release_time=_ADVANCED_DT,
            cache_cron_status=cron_statuses.DONE,
            expected_cache_release_time=_ADVANCED_DT,
            expected_cache_cron_status=cron_statuses.UPDATED,
        ),
    ],
)
async def test_rule_keeper_reloader(
        monkeypatch,
        replication_app,
        database_state,
        before_deploy,
        expected_after_deploy,
        should_refresh,
):
    if database_state:
        await replication_app.db.replication_rules_deploy.insert_many(
            database_state,
        )
    rule_reloader = replication_app.rule_keeper_reloader
    rule_reloader._rule_deploying_info = before_deploy
    old_rule_keeper = replication_app.rule_keeper
    if not should_refresh:
        await rule_reloader.refresh_cache()
        assert replication_app.rule_keeper is old_rule_keeper
        assert rule_reloader._rule_deploying_info == expected_after_deploy
        return
    await rule_reloader.refresh_cache()
    assert replication_app.rule_keeper is not old_rule_keeper
    assert rule_reloader._rule_deploying_info == expected_after_deploy
