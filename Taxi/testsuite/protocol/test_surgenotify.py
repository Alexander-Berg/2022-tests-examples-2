import csv
import os
import shutil
import time

import pytest


@pytest.fixture(scope='module')
def _surgenotify_dir(worker_id):
    worker_suffix = '_' + worker_id if worker_id != 'master' else ''
    surgenotify_dir = os.path.abspath('surgenotify_test' + worker_suffix)
    try:
        yield surgenotify_dir
    finally:
        shutil.rmtree(surgenotify_dir)


@pytest.mark.parametrize(
    'user_id,enabled,tariff_class,expected_code,ua',
    [
        (
            'b300bda7d41b4bae8d58dfa93221ef16',
            True,
            'econom',
            200,
            'ru.yandex.taxi.inhouse/3.98.8966 '
            '(iPhone; iPhone7,1; iOS 10.3.3; Darwin)',
        ),
        (
            'b300bda7d41b4bae8d58dfa93221ef16',
            False,
            'econom',
            200,
            'yandex-taxi/3.29.0.8857 Android/7.0 (samsung; SM-G930F)',
        ),
        (
            'b300bda7d41b4bae8d58dfa93221ef17',
            True,
            'econom',
            401,
            'yandex-taxi/3.29.0.8857 Android/7.0 (samsung; SM-G930F)',
        ),
        (
            'b300bda7d41b4bae8d58dfa93221ef16',
            0,
            'econom',
            200,
            'yandex-taxi/3.29.0.8857 Android/7.0 (samsung; SM-G930F)',
        ),
        (
            'b300bda7d41b4bae8d58dfa93221ef16',
            1,
            'econom',
            200,
            'yandex-taxi/3.29.0.8857 Android/7.0 (samsung; SM-G930F)',
        ),
    ],
)
@pytest.mark.user_experiments('surge_notify_available')
def test_simple(
        taxi_protocol,
        user_id,
        enabled,
        tariff_class,
        expected_code,
        ua,
        _surgenotify_dir,
):
    body = {'id': user_id, 'enabled': enabled, 'tariff_class': tariff_class}

    response = taxi_protocol.post(
        '3.0/surgenotify',
        json=body,
        headers={'Accept-Language': 'ru', 'User-Agent': ua},
    )

    # Writer is async, so we need to wait for it to flush before we read it
    time.sleep(2)

    assert response.status_code == expected_code

    if expected_code == 200:
        last_row = {}
        with open(os.path.join(_surgenotify_dir, 'surge_notify')) as f:
            for row in csv.reader(f, delimiter='\t'):
                last_row = dict(item.split('=') for item in row)

        assert (last_row['enabled'] == 'true') == enabled
        assert last_row['tariff_class'] == tariff_class
        assert last_row['user_id'] == user_id
        assert last_row['user_agent'] == ua


def test_noexperiment(taxi_protocol):
    body = {
        'id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'enabled': True,
        'tariff_class': 'econom',
    }
    response = taxi_protocol.post(
        '3.0/surgenotify', json=body, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 404
