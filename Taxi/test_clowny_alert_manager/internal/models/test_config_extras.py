# pylint: disable=protected-access

from clowny_alert_manager.internal.models import _config_extras
from clowny_alert_manager.internal.models import notification_option as no


def test_convert_notification_opts():
    result = _config_extras.LinkedTemplates._convert_notification_opts(None)
    assert result == []

    result = _config_extras.LinkedTemplates._convert_notification_opts('')
    assert result == []

    result = _config_extras.LinkedTemplates._convert_notification_opts([])
    assert result == []

    result = _config_extras.LinkedTemplates._convert_notification_opts('a')
    assert result == [('a', no.NotificationType.telegram)]

    result = _config_extras.LinkedTemplates._convert_notification_opts(
        ['a', 'b'],
    )
    assert result == [
        ('a', no.NotificationType.telegram),
        ('b', no.NotificationType.telegram),
    ]
