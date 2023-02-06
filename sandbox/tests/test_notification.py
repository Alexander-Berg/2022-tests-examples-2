import logging
from mock import MagicMock
from sandbox.projects.yabs.release.tasks.YabsServerNotifyReleaseTicketChanged import YabsServerNotifyReleaseTicketChanged


ST_TICKET = 'BSRELEASE-254987'


def test_notification_template():
    task = YabsServerNotifyReleaseTicketChanged(None)
    task.delete()

    notification_template = task._YabsServerNotifyReleaseTicketChanged__get_notification_template()

    logging.info(notification_template)

    msg_tlg = notification_template.render({'release_ticket': ST_TICKET,
                                            'release_ticket_link' : "http://st.yandex-team.ru/{}".format(ST_TICKET),
                                            'transport': 'telegram',
                                            'ticket_filed': 'status.key',
                                            'ticket_filed_value': 'readyToDeploy',
                                            'on_duty_users': ['user_1', 'user_2']})

    msg_ych = notification_template.render({'release_ticket': ST_TICKET,
                                            'release_ticket_link' : "http://st.yandex-team.ru/{}".format(ST_TICKET),
                                            'transport': 'yachats',
                                            'ticket_filed': 'status.name',
                                            'ticket_filed_value': 'Ready to Deploy',
                                            'on_duty_users': ['user_1', 'user_2']})

    logging.info(msg_tlg)
    logging.info(msg_ych)

    return msg_tlg, msg_ych


def test_get_attribute_value():
    task = YabsServerNotifyReleaseTicketChanged(None)
    task.delete()

    status = MagicMock()
    status.name = 'Ready to Deploy'
    status.key = 'readyToDeploy'

    issue = MagicMock()
    issue.status = status
    issue.errorName = 'Error Name'

    assert task._YabsServerNotifyReleaseTicketChanged__get_attribute_value(issue, 'status.name') == 'Ready to Deploy'
    assert task._YabsServerNotifyReleaseTicketChanged__get_attribute_value(issue, 'status.key') == 'readyToDeploy'
    assert task._YabsServerNotifyReleaseTicketChanged__get_attribute_value(issue, 'errorName') == 'Error Name'
