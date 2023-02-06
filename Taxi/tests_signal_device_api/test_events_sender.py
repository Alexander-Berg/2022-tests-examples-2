import pytest


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
@pytest.mark.config(
    SIGNAL_DEVICE_API_EVENTS_SENDING_TASK_SETTINGS={
        'enabled': True,
        'task_delay_secs': 0,
        'max_event_at_delay_secs': 157680000,  # 5 years
        'events_sending_batch': 4,
    },
)
@pytest.mark.parametrize(
    'sent_event_ids, need_to_check_event_ids',
    [
        pytest.param(
            [
                ('0ef0466e6e1331b3a7d35c585983076a',),
                ('7faebfa97bfafe293023a41a49250ac3',),
                ('7faebfa97bfafe293023a41a49250ak3',),
            ],
            True,
            marks=[
                pytest.mark.config(
                    SIGNAL_DEVICE_API_EVENTS_TO_CLIENT_URLS=[
                        {
                            'media_types_to_event_types': {
                                'external_video': ['driver_lost'],
                                'internal_image': ['driver_lost'],
                            },
                            'urls_info': [
                                {
                                    'url': {
                                        '$mockserver': '/plotva-ml/signalq_media_handler/v1',  # noqa: E501
                                    },
                                    'service_name': 'plotva-ml',
                                    'timeout': 1000,
                                    'retries': 2,
                                    'are_coordinates_required': False,
                                },
                            ],
                        },
                    ],
                ),
            ],
        ),
        pytest.param(
            [
                ('0ef0466e6e1331b3a7d35c585983076a',),
                ('7faebfa97bfafe293023a41a49250ac3',),
                ('7faebfa97bfafe293023a41a49250ak3',),
                ('9es0466e6e1331b3a7d35c585983076a',),
            ],
            True,
            marks=[
                pytest.mark.config(
                    SIGNAL_DEVICE_API_EVENTS_TO_CLIENT_URLS=[
                        {
                            'media_types_to_event_types': {
                                'external_video': [],
                            },
                            'urls_info': [
                                {
                                    'url': {
                                        '$mockserver': '/plotva-ml/signalq_media_handler/v1',  # noqa: E501
                                    },
                                    'service_name': 'plotva-ml',
                                    'timeout': 1000,
                                    'retries': 2,
                                    'are_coordinates_required': False,
                                },
                            ],
                        },
                    ],
                ),
            ],
        ),
        pytest.param(
            [
                ('0ef0466e6e1331b3a7d35c585983076a',),
                ('7faebfa97bfafe293023a41a49250ak3',),
                ('9es0466e6e1331b3a7d35c585983076a',),
            ],
            True,
            marks=[
                pytest.mark.config(
                    SIGNAL_DEVICE_API_EVENTS_TO_CLIENT_URLS=[
                        {
                            'media_types_to_event_types': {
                                'internal_video': ['driver_lost'],
                                'external_video': [],
                            },
                            'urls_info': [
                                {
                                    'url': {
                                        '$mockserver': '/plotva-ml/signalq_media_handler/v1',  # noqa: E501
                                    },
                                    'service_name': 'plotva-ml',
                                    'timeout': 1000,
                                    'retries': 2,
                                    'are_coordinates_required': False,
                                },
                            ],
                        },
                    ],
                ),
            ],
        ),
        pytest.param(
            [('7faebfa97bfafe293023a41a49250ak3',)],
            False,
            marks=[
                pytest.mark.config(
                    SIGNAL_DEVICE_API_EVENTS_TO_CLIENT_URLS=[
                        {
                            'media_types_to_event_types': {
                                'internal_video': ['driver_lost'],
                                'external_video': [],
                            },
                            'urls_info': [
                                {
                                    'url': {
                                        '$mockserver': '/plotva-ml/signalq_media_handler/v1',  # noqa: E501
                                    },
                                    'service_name': 'plotva-ml',
                                    'timeout': 1000,
                                    'retries': 2,
                                    'are_coordinates_required': True,
                                },
                            ],
                        },
                    ],
                ),
            ],
        ),
    ],
)
async def test_ok(
        testpoint,
        pgsql,
        taxi_signal_device_api,
        mockserver,
        sent_event_ids,
        need_to_check_event_ids,
):
    @mockserver.handler('/plotva-ml/signalq_media_handler/v1')
    # pylint: disable=unused-variable
    def signalq_media_handler(request):
        return mockserver.make_response(status=204)

    @testpoint('events-sender-ok-testpoint')
    def ok_testpoint(arg):
        pass

    async with taxi_signal_device_api.spawn_task('signalq-events-sender'):
        await ok_testpoint.wait_call()
        await ok_testpoint.wait_call()

    assert signalq_media_handler.times_called == len(sent_event_ids)

    if not need_to_check_event_ids:
        return

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT event_id FROM signal_device_api.events '
        'WHERE is_sent_to_ml ORDER BY event_id',
    )
    assert list(db) == sent_event_ids


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['signal_device_api_meta_db.sql'],
)
async def test_disabled(testpoint, pgsql, taxi_signal_device_api):
    @testpoint('events-sender-disabled-testpoint')
    def disabled_testpoint(arg):
        pass

    async with taxi_signal_device_api.spawn_task('signalq-events-sender'):
        await disabled_testpoint.wait_call()

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT COUNT(*) FROM signal_device_api.events ' 'WHERE is_sent_to_ml',
    )
    assert list(db) == [(0,)]
