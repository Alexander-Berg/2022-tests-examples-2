import typing
from unittest import mock

import pytest

from achievements_py3 import consts
from achievements_py3 import models
from achievements_py3.components import rewards_db
from achievements_py3.generated.cron import run_cron


ALL_UDIDS = ['udid1', 'udid2', 'udid3']


async def get_driver_rewards(
        udids, db: rewards_db.Component,
) -> typing.Dict[str, list]:
    result: typing.Dict[str, list] = {}
    for udid in udids:
        driver_rewards = await db.get_driver_rewards(udid)
        if driver_rewards:
            result[udid] = [(dr.code, dr.level) for dr in driver_rewards]
    return result


async def get_driver_progresses(
        udids, db: rewards_db.Component,
) -> typing.Dict[str, list]:
    result: typing.Dict[str, list] = {}
    for udid in udids:
        driver_progresses = await db.get_driver_progresses(udid)
        if driver_progresses:
            result[udid] = [(dp.code, dp.progress) for dp in driver_progresses]
    return result


@pytest.mark.parametrize(
    'reward_code, is_leveled, expect_error, expect_status',
    [
        ('star', False, 'yql-error', consts.Status.ERROR),
        ('star', False, 'no-column', consts.Status.ERROR),
        ('star', False, None, consts.Status.PENDING),
        ('driver_years', True, 'yql-error', consts.Status.ERROR),
        ('driver_years', True, 'no-column', consts.Status.ERROR),
        ('driver_years', True, None, consts.Status.PENDING),
    ],
)
async def test_yql_running(
        monkeypatch,
        cron_context,
        reward_code,
        is_leveled,
        expect_error,
        expect_status,
):

    yql = 'Text YQL'
    upload_type = consts.UploadType.SET_UNLOCKED

    db: rewards_db.Component = cron_context.rewards_db

    upload_id = await db.create_upload(
        reward_code=reward_code, upload_type=upload_type, yql=yql, author=None,
    )

    assert upload_id

    new_upload: models.UploadTask = await db.fetch_upload_by_id(upload_id)
    assert new_upload
    assert new_upload.upload_id == upload_id
    assert new_upload.upload_type == upload_type
    assert new_upload.reward_code == reward_code
    assert new_upload.status == consts.Status.NEW
    assert new_upload.yql == yql
    assert new_upload.results is None

    operation_id = 'operation_id'
    share_url = 'share_url'

    errors = ['errors-from-yql']

    def get_results(*args, **kwargs):
        acc = mock.MagicMock()

        if not expect_error:
            acc.status = 'RUNNING'
        elif expect_error == 'no-column':
            acc = mock.MagicMock()
            acc.status = 'COMPLETED'
            if not is_leveled:
                acc.table.column_names = [
                    'column',
                ]  # actually we expect single column 'udid'
            else:
                acc.table.column_names = [
                    'udid',
                    'bar',
                ]  # actually we expect columns 'udid' and 'progress'
        elif expect_error == 'yql-error':
            acc.status = 'ERROR'
            acc.errors = errors
        return acc

    monkeypatch.setattr(
        'yql.client.operation.YqlSqlOperationRequest.operation_id',
        property(lambda _: operation_id),
    )
    monkeypatch.setattr(
        'yql.client.operation.YqlSqlOperationRequest.share_url',
        property(lambda _: share_url),
    )
    monkeypatch.setattr(
        'yql.client.operation.YqlSqlOperationRequest.run', lambda _: None,
    )

    monkeypatch.setattr(
        'yql.client.operation.YqlOperationResultsRequest.run', lambda _: None,
    )
    monkeypatch.setattr(
        'yql.client.operation.YqlOperationResultsRequest.get_results',
        get_results,
    )

    # crontask
    await run_cron.main(['achievements_py3.crontasks.yql_upload', '-t', '0'])

    found_upload: models.UploadTask = await db.fetch_upload_by_id(upload_id)
    assert found_upload
    assert found_upload.upload_id == upload_id
    assert found_upload.upload_type == upload_type
    assert found_upload.reward_code == reward_code
    assert found_upload.status == expect_status

    assert found_upload.yql == yql
    assert found_upload.results
    results = found_upload.results

    if expect_status != consts.Status.CANCEL:
        assert results['operation_id'] == operation_id
        assert results['share_url'] == share_url

    if expect_error:
        if expect_error == 'no-column':
            if is_leveled:  # leveled reward
                errors = ['result has no progress column']
            else:  # non-leveled reward
                errors = ['result has no udid column']

        assert results['errors'] == errors
    else:
        assert 'errors' not in results


@pytest.mark.config(ACHIEVEMENTS_JOB_CLIENT_EVENTS_UPDATES_ENABLE=True)
@pytest.mark.parametrize(
    'reward_code, is_leveled, expect_rewards, expect_progress',
    [
        pytest.param(
            'star',
            False,
            {
                'udid1': [('star', 1)],
                'udid2': [('star', 1)],
                'udid3': [('star', 1)],
            },
            {},
            id='star',
        ),
        pytest.param(
            'driver_years',
            True,
            {
                'udid1': [('driver_years', 1)],
                'udid2': [('driver_years', 1), ('driver_years', 2)],
                'udid3': [
                    ('driver_years', 1),
                    ('driver_years', 2),
                    ('driver_years', 3),
                ],
            },
            {},
            id='driver_years',
        ),
        pytest.param(
            '5_stars',
            True,
            {
                'udid1': [('5_stars', 100)],
                'udid2': [('5_stars', 100), ('5_stars', 300)],
                'udid3': [
                    ('5_stars', 100),
                    ('5_stars', 300),
                    ('5_stars', 500),
                ],
            },
            {
                'udid1': [('5_stars', 199)],
                'udid2': [('5_stars', 301)],
                'udid3': [('5_stars', 501)],
            },
            id='5_stars',
        ),
    ],
)
async def test_yql_add_driver_rewards(
        monkeypatch,
        cron_context,
        client_events_mocker,
        reward_code,
        is_leveled,
        expect_rewards,
        expect_progress,
):
    upload_type = consts.UploadType.SET_UNLOCKED
    yql = 'Text YQL'

    db: rewards_db.Component = cron_context.rewards_db

    upload_id = await db.create_upload(
        reward_code=reward_code, upload_type=upload_type, yql=yql, author=None,
    )

    assert upload_id

    new_upload: models.UploadTask = await db.fetch_upload_by_id(upload_id)
    assert new_upload
    assert new_upload.upload_id == upload_id
    assert new_upload.upload_type == upload_type
    assert new_upload.reward_code == reward_code
    assert new_upload.status == consts.Status.NEW
    assert new_upload.yql == yql
    assert new_upload.results is None

    operation_id = 'operation_id'
    share_url = 'share_url'

    def get_results(*args, **kwargs):
        acc = mock.MagicMock()
        acc.status = 'COMPLETED'
        record_set = mock.MagicMock()
        if is_leveled:
            acc.table.column_names = ['udid', 'progress']
            if reward_code == '5_stars':
                record_set.rows = [
                    ('udid1', 199),
                    ('udid2', 301),
                    ('udid3', 501),
                ]
            else:
                record_set.rows = [('udid1', 1), ('udid2', 2), ('udid3', 99)]
        else:
            acc.table.column_names = ['udid']
            record_set.rows = [(udid,) for udid in ALL_UDIDS]
        acc.__iter__ = lambda _: iter([record_set])
        return acc

    monkeypatch.setattr(
        'yql.client.operation.YqlSqlOperationRequest.operation_id',
        property(lambda _: operation_id),
    )
    monkeypatch.setattr(
        'yql.client.operation.YqlSqlOperationRequest.share_url',
        property(lambda _: share_url),
    )
    monkeypatch.setattr(
        'yql.client.operation.YqlSqlOperationRequest.run', lambda _: None,
    )

    monkeypatch.setattr(
        'yql.client.operation.YqlOperationResultsRequest.run', lambda _: None,
    )
    monkeypatch.setattr(
        'yql.client.operation.YqlOperationResultsRequest.get_results',
        get_results,
    )

    ce_mock = client_events_mocker(
        expect_event='achievements_state', expect_udids=set(ALL_UDIDS),
    )

    # crontask
    await run_cron.main(['achievements_py3.crontasks.yql_upload', '-t', '0'])

    found_upload: models.UploadTask = await db.fetch_upload_by_id(upload_id)
    assert found_upload
    assert found_upload.upload_id == upload_id
    assert found_upload.upload_type == upload_type
    assert found_upload.reward_code == reward_code
    assert found_upload.status == consts.Status.COMPLETE
    assert found_upload.yql == yql
    assert found_upload.results
    results = found_upload.results
    assert results['operation_id'] == operation_id
    assert results['share_url'] == share_url

    all_driver_rewards = await get_driver_rewards(ALL_UDIDS, db)
    assert all_driver_rewards == expect_rewards

    all_driver_progresses = await get_driver_progresses(ALL_UDIDS, db)
    assert all_driver_progresses == expect_progress

    assert ce_mock.pro_bulk_push.times_called == 1
    ce_mock.pro_bulk_push.flush()

    # Prepare the same upload again
    upload_id2 = await db.create_upload(
        reward_code=reward_code, upload_type=upload_type, yql=yql, author=None,
    )
    assert upload_id2
    assert upload_id2 > upload_id

    # crontask: YQL will return the same set of driver rewards,
    # therefore table should be left unchanged
    await run_cron.main(['achievements_py3.crontasks.yql_upload', '-t', '0'])

    assert ce_mock.pro_bulk_push.times_called == 0

    all_driver_rewards2 = await get_driver_rewards(ALL_UDIDS, db)
    assert all_driver_rewards2 == expect_rewards

    all_driver_progresses2 = await get_driver_progresses(ALL_UDIDS, db)
    assert all_driver_progresses2 == expect_progress
