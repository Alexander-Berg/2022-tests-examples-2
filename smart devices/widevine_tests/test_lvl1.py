import os
import time

import click
import pytest

from contextlib import contextmanager

from adbutils import adb


@contextmanager
def video_player(adb_device):
    def play(content_url, license_url):
        print('>>>> Playing %s / %s' % (content_url, license_url))

        adb_device.shell(
            ' '.join(
                [
                    'am',
                    'start',
                    '-a',
                    'com.google.android.exoplayer.demo.action.VIEW_LIST',
                    '--es',
                    'drm_scheme_0',
                    'widevine',
                    '--es',
                    'uri_0',
                    '"%s"' % content_url,
                    '--es',
                    'drm_license_url_0',
                    '"%s"' % license_url,  # TODO: a nicer quoting, maybe?
                ]
            )
        )

    try:
        adb_device.shell('kill $(busybox pgrep exoplayer2)')  # kill old player

        # FIXME: sleeps are no way for synchronization!
        time.sleep(2)

        yield play
    finally:
        adb_device.shell('kill $(busybox pgrep exoplayer2)')  # kill our player

        # FIXME: sleeps are no way for synchronization!
        time.sleep(2)


def ask_result(prompt):
    return click.confirm(prompt, default=True)


@pytest.fixture(scope='module')
def exoplayer_demo(pytestconfig, device):
    device.install(os.path.abspath(pytestconfig.getoption('exoplayer_demo')))


@pytest.fixture(scope='session')
def device():
    # TODO: add more selectors for device!
    return adb.device()


def test_play(device, exoplayer_demo, wv_case):
    with video_player(device) as play:
        play(content_url=wv_case.content_url, license_url=wv_case.license_url)

        print('>>>> Expected output is:\n%s' % wv_case.expected)

        assert ask_result('>>>> Does it look like expected?')
