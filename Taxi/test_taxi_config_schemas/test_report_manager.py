from taxi_config_schemas import report_manager
from taxi_config_schemas.report_manager import comment_tickets
from taxi_config_schemas.report_manager import common

DATA = [
    (
        'Aleksandr Piskarev',
        'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        'feat conf: fix startreck extra ticket',
        'Relates: TAXI-123',
    ),
    (
        'Natalia Dunaeva',
        'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        'feat configs: add Startreck Extra Ticket',
        'Relates: TAXI-124',
    ),
    (
        'Aleksandr Piskarev',
        'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        'feat conf: fix startreck extra ticket',
        'Relates: TAXI-123',
    ),
    (
        'Natalia Dunaeva',
        'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES',
        'feat configs: add Startreck Extra Ticket',
        'Relates: TAXI-124',
    ),
    (
        'Maksim Moisiuk',
        'DEVICENOTIFY_USER_TTL',
        'add device-notify config',
        'Relates: TAXI-125',
    ),
    (
        'Maksim Moisiuk',
        'DEVICENOTIFY_USER_TTL',
        'add device-notify config',
        'Relates: TAXI-125',
    ),
    (
        'Daniil Efimov',
        'DRIVER_DISPATCHER_ENABLED_REGISTERING_PIN_IN_DISPATCH',
        'feat dd: change config',
        'Relates: TAXI-126',
    ),
    (
        'Daniil Efimov',
        'DRIVER_DISPATCHER_ENABLED_REGISTERING_PIN_IN_DISPATCH',
        'feat dd: change config',
        'Relates: TAXI-126',
    ),
]


async def test_collect_comments(web_context):
    rt_manager = common.ReportManager(client=web_context.client_startrek)

    for _, config_name, _, raw_relates in DATA:
        rt_manager.add_comments('author', config_name, raw_relates)

    assert rt_manager.comments_by_ticket == {
        'TAXI-123': {
            'New schema for config '
            '"((https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
            'dev/configs/edit/STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES '
            'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES))" '
            'was applied in admin by @author',
        },
        'TAXI-124': {
            'New schema for config '
            '"((https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
            'dev/configs/edit/STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES '
            'STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES))" '
            'was applied in admin by @author',
        },
        'TAXI-125': {
            'New schema for config '
            '"((https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
            'dev/configs/edit/DEVICENOTIFY_USER_TTL '
            'DEVICENOTIFY_USER_TTL))" '
            'was applied in admin by @author',
        },
        'TAXI-126': {
            'New schema for config '
            '"((https://tariff-editor-unstable.taxi.tst.yandex-team.ru/'
            'dev/configs/edit/'
            'DRIVER_DISPATCHER_ENABLED_REGISTERING_PIN_IN_DISPATCH '
            'DRIVER_DISPATCHER_ENABLED_REGISTERING_PIN_IN_DISPATCH))" '
            'was applied in admin by @author',
        },
    }


async def test_select_report_method(web_context):
    config = {
        'report_method': 'add_to_tickets',
        'report_collect_ticket': 'TAXIBACKEND-404',
    }
    instance = report_manager.select_report_manager(
        config=config, client=web_context.client_startrek,
    )
    assert isinstance(instance, comment_tickets.AddComments)
    assert instance.collect_ticket == 'TAXIBACKEND-404'
