from unittest import mock

import pytest

from taxi.robowarehouse.lib.config.base import QueueWorkerSettings
from taxi.robowarehouse.lib.queue import app


@pytest.mark.parametrize('override_settings_values', [
    [('queue.workers', [])],
], indirect=True)
@mock.patch.object(app, 'Observer')
@pytest.mark.asyncio
def test_app_0_item(mock_observer, override_settings_values):
    result = app.run()

    mock_observer.assert_called_once_with()
    mock_observer.return_value.spawn_actor.assert_has_calls([])

    mock_observer.return_value.watch_actors.assert_called_once_with()

    assert result is None


@pytest.mark.parametrize('override_settings_values', [
    [('queue.workers', [QueueWorkerSettings(type='tuya', instances=1, spec={'a': 3})])],
], indirect=True)
@mock.patch.object(app, 'Observer')
@pytest.mark.asyncio
def test_app_1_item_1_instances(mock_observer, override_settings_values):
    result = app.run()

    mock_observer.assert_called_once_with()
    mock_observer.return_value.spawn_actor.assert_has_calls([
        mock.call(
            name='tuya_0_0',
            worker_type='tuya',
            worker_spec={'a': 3},
        ),
    ])

    mock_observer.return_value.watch_actors.assert_called_once_with()

    assert result is None


@pytest.mark.parametrize('override_settings_values', [
    [('queue.workers', [QueueWorkerSettings(type='tuya', instances=2, spec={'a': 3})])],
], indirect=True)
@mock.patch.object(app, 'Observer')
@pytest.mark.asyncio
def test_app_1_item_2_instances(mock_observer, override_settings_values):
    result = app.run()

    mock_observer.assert_called_once_with()
    mock_observer.return_value.spawn_actor.assert_has_calls([
        mock.call(
            name='tuya_0_0',
            worker_type='tuya',
            worker_spec={'a': 3},
        ),
        mock.call(
            name='tuya_0_1',
            worker_type='tuya',
            worker_spec={'a': 3},
        ),
    ])

    mock_observer.return_value.watch_actors.assert_called_once_with()

    assert result is None


@pytest.mark.parametrize('override_settings_values', [
    [('queue.workers', [QueueWorkerSettings(type='tuya', instances=2, spec={'a': 3}),
                        QueueWorkerSettings(type='tuya', instances=1, spec={'b': 2})])],
], indirect=True)
@mock.patch.object(app, 'Observer')
@pytest.mark.asyncio
def test_app_2_item_3_instances(mock_observer, override_settings_values):
    result = app.run()

    mock_observer.assert_called_once_with()
    mock_observer.return_value.spawn_actor.assert_has_calls([
        mock.call(
            name='tuya_0_0',
            worker_type='tuya',
            worker_spec={'a': 3},
        ),
        mock.call(
            name='tuya_0_1',
            worker_type='tuya',
            worker_spec={'a': 3},
        ),
        mock.call(
            name='tuya_1_0',
            worker_type='tuya',
            worker_spec={'b': 2},
        ),
    ])

    mock_observer.return_value.watch_actors.assert_called_once_with()

    assert result is None
