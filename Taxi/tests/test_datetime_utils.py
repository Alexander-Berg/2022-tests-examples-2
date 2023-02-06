import datetime

import dateutil.tz
import freezegun

from taxi.robowarehouse.lib.misc import datetime_utils


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
def test_get_now():
    result = datetime_utils.get_now()

    assert result == datetime.datetime(2020, 1, 2, 0, 4, 5, tzinfo=datetime.timezone.utc)
    assert result.tzinfo == dateutil.tz.UTC


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
def test_get_now_custom_tz():
    result = datetime_utils.get_now(tz=dateutil.tz.gettz('Asia/Yekaterinburg'))

    assert result == datetime.datetime(2020, 1, 2, 0, 4, 5, tzinfo=datetime.timezone.utc)
    assert result.tzinfo == dateutil.tz.gettz('Asia/Yekaterinburg')
