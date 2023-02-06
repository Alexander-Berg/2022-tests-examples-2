# flake8: noqa

# Feel free to provide your custom implementation to override generated tests.

import datetime
import pytest
import json
import base64

# pylint: disable=import-error,wildcard-import
from eats_restapp_communications_plugins.generated_tests import *


async def request_proxy_log_status(
        taxi_eats_restapp_communications, data, partner_id,
):
    url = '/4.0/restapp-front/communications/v1/log-status'

    headers = {
        'X-YaEda-PartnerId': str(partner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )


async def test_log_status_200(
        taxi_eats_restapp_communications, mock_feeds_log_status,
):
    partner_id = 1
    data = {
        'id': '7429ad7d21994f298f3685e8f5b50770',
        'service': 'notification',
        'channel': 'partner_id:{}'.format(partner_id),
    }
    response = await request_proxy_log_status(
        taxi_eats_restapp_communications, data, partner_id,
    )
    assert response.status_code == 200


async def test_log_status_404(
        taxi_eats_restapp_communications, mock_feeds_log_status,
):
    partner_id = 1
    data = {
        'id': '7429ad7d21994f298f3685e8f5b50771',
        'service': 'notification',
        'channel': 'partner_id:{}'.format(partner_id),
    }
    response = await request_proxy_log_status(
        taxi_eats_restapp_communications, data, partner_id,
    )
    assert response.status_code == 404
