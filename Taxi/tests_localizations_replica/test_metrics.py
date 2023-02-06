import datetime

import pytest

PREFIX = 'update-tanker-cache'
FIELD_NAME = 'time-since-last-fully-succeeded-update-ms'


@pytest.mark.now('2019-08-01T11:00:00+00:00')
async def test_metrics_timestring_format(
        taxi_localizations_replica,
        taxi_localizations_replica_monitor,
        mocked_time,
):
    db_time = datetime.datetime.strptime(
        '2019-08-01T10:00:00.000+0000', '%Y-%m-%dT%H:%M:%S.%f%z',
    )
    now = mocked_time.now().replace(tzinfo=datetime.timezone.utc)

    # required to set mocked time before requesting metrics
    await taxi_localizations_replica.update_server_state()

    json = await taxi_localizations_replica_monitor.get_metric(PREFIX)
    interval_since_last_update = datetime.timedelta(
        milliseconds=json[FIELD_NAME],
    )

    assert interval_since_last_update == now - db_time
