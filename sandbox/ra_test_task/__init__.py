# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
from sandbox.projects.robot_adapter.common.email_utils import (
    send_email, read_email_template, make_attachment, YANDEX_TEAM_EMAIL
)
from sandbox import sdk2


def load_presentation():
    presentation = sdk2.Resource.find(
        attrs=dict(robot_adapter="introduction.pdf")
    ).first()
    if not presentation:
        raise RuntimeError("Presentation resource wasn't found")
    resource_path = str(sdk2.ResourceData(presentation).path)
    logging.info('Resource path: {}'.format(resource_path))
    with open(resource_path, 'rb') as f:
        return f.read()


class RobotAdapterTestTask(sdk2.Task):

    def on_execute(self):
        self.set_info("Sending email")
        presentation = load_presentation()
        send_email(
            subject='Добро пожаловать в Яндекс',
            to_emails=[YANDEX_TEAM_EMAIL.format(login='comradeandrew')],
            html=read_email_template(),
            attachments=[
                make_attachment(presentation, 'Вводная презентация.pdf')
            ]
        )
        self.set_info("Task successfully done.")
