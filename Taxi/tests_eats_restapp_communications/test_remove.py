# flake8: noqa

# Feel free to provide your custom implementation to override generated tests.

import datetime
import pytest
import json
import base64

# pylint: disable=import-error,wildcard-import
from eats_restapp_communications_plugins.generated_tests import *


async def request_proxy_notify_remove(
        taxi_eats_restapp_communications, data, patner_id,
):
    url = '/4.0/restapp-front/communications/v1/remove'
    headers = {
        'X-YaEda-PartnerId': str(patner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )


async def test_remove_notification(
        taxi_eats_restapp_communications, mock_feeds_remove_200,
):
    partner_id = 1
    data = {
        'id': 'cc609ff0e8954f7695520af4a38c79a1',
        'service': 'eats-restaurants-notification',
        'channels': ['partner_id:{}'.format(partner_id)],
    }
    response = await request_proxy_notify_remove(
        taxi_eats_restapp_communications, data, partner_id,
    )
    assert response.status_code == 200


async def test_remove_notification_404(
        taxi_eats_restapp_communications, mock_feeds_remove_404,
):
    partner_id = 1
    data = {
        'id': 'cc609ff0e8954f7695520af4a38c79a2',
        'service': 'eats-restaurants-notification',
        'channels': ['partner_id:{}'.format(partner_id)],
    }
    response = await request_proxy_notify_remove(
        taxi_eats_restapp_communications, data, partner_id,
    )
    assert response.status_code == 404
