# coding: utf-8
import pytest
from pprint import pformat

from nile.api.v1 import MockCluster
from nile.api.v1.local import StreamSource, ListSink

from taxi_etl.layer.yt.dds.dim_branding.attr_car_hist.impl import build_increment

from .impl import record

@pytest.mark.parametrize(
    'source_events, expected_increment',
    [
        pytest.param(
            [
                record(
                    utc_event_dt='2019-08-10',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_event_dt='2019-08-19',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_event_dt='2019-08-28',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),

            ],
            [
                record(
                    utc_effective_from_dt='2019-08-12',
                    utc_effective_to_dt='2019-08-18',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_effective_from_dt='2019-08-19',
                    utc_effective_to_dt='2019-08-27',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=True
                )
            ],
            id='Regular constant branding'
        ),
        pytest.param(
            [
                record(
                    utc_event_dt='2019-08-10',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_event_dt='2019-08-19',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_event_dt='2019-08-28',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=False
                ),

            ],
            [
                record(
                    utc_effective_from_dt='2019-08-12',
                    utc_effective_to_dt='2019-08-18',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_effective_from_dt='2019-08-19',
                    utc_effective_to_dt='2019-08-27',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                )
            ],
            id='Regular non-constant branding'
        ),
        pytest.param(
            [
                record(
                    utc_event_dt='2019-08-19',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_event_dt='2019-08-28',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),

            ],
            [
                record(
                    utc_effective_from_dt='2019-08-19',
                    utc_effective_to_dt='2019-08-27',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                )
            ],
            id='Gap on increment period start'
        ),
        pytest.param(
            [
                record(
                    utc_event_dt='2019-08-12',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                )
            ],
            [
                record(
                    utc_effective_from_dt='2019-08-12',
                    utc_effective_to_dt='2019-08-22',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                )
            ],
            id='Gap on increment period end'
        ),
        pytest.param(
            [
                record(
                    utc_event_dt='2019-08-12',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_event_dt='2019-08-26',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                )
            ],
            [
                record(
                    utc_effective_from_dt='2019-08-12',
                    utc_effective_to_dt='2019-08-22',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_effective_from_dt='2019-08-26',
                    utc_effective_to_dt='2019-08-27',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                )
            ],
            id='Gap on increment period middle'
        ),
        pytest.param(
            [
                record(
                    utc_event_dt='2019-08-09',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_event_dt='2019-08-10',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_event_dt='2019-08-13',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_event_dt='2019-08-23',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                )
            ],
            [
                record(
                    utc_effective_from_dt='2019-08-12',
                    utc_effective_to_dt='2019-08-12',
                    lightbox_status='uber',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_effective_from_dt='2019-08-13',
                    utc_effective_to_dt='2019-08-22',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
                record(
                    utc_effective_from_dt='2019-08-23',
                    utc_effective_to_dt='2019-08-27',
                    lightbox_status='yandex',
                    sticker_status='uber',
                    back_window_phone_flg=True
                ),
            ],
            id='Several events before period'
        ),
        pytest.param(
            [
                record(
                    utc_event_dt='2019-08-09',
                    lightbox_status='_missing_',
                    sticker_status='_missing_',
                    back_window_phone_flg=False
                ),
                record(
                    utc_event_dt='2019-08-12',
                    lightbox_status='_missing_',
                    sticker_status='_missing_',
                    back_window_phone_flg=False
                )
            ],
            [
                record(
                    utc_effective_from_dt='2019-08-12',
                    utc_effective_to_dt='2019-08-22',
                    lightbox_status='_missing_',
                    sticker_status='_missing_',
                    back_window_phone_flg=False
                )
            ],
            id='No brand'
        )
    ]
)
def test_increment_build(source_events, expected_increment):
    start_dt = '2019-08-12'
    end_dt = '2019-08-27'

    cluster = MockCluster()
    job = cluster.job('test_session_build')
    actual_increment = []
    job.table('stub') \
        .label('source_events') \
        .call(build_increment, start_dt, end_dt) \
        .label('actual_increment')
    job.local_run(
        sources={'source_events': StreamSource(source_events)},
        sinks={'actual_increment': ListSink(actual_increment)}
    )

    actual_increment = sorted(actual_increment, key=lambda rec: (rec.get('user_id'), rec.get('utc_session_start')))

    assert expected_increment == actual_increment, \
        'Expected increment is different from actual:\nexpected\n{},\nactual\n{}'.format(
            pformat(expected_increment), pformat(actual_increment)
        )
