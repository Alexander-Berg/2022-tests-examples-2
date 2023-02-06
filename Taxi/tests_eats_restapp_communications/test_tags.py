# flake8: noqa

# Feel free to provide your custom implementation to override generated tests.

import datetime
import pytest
import json
import base64

# pylint: disable=import-error,wildcard-import
from eats_restapp_communications_plugins.generated_tests import *


async def request_proxy_internal_tags(
        taxi_eats_restapp_communications, data, place_id,
):
    url = '/internal/communications/v1/tags?place_id={}'.format(place_id)

    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}

    return await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )


async def test_notification_tags(taxi_eats_restapp_communications, pgsql):
    name = 'city'
    value = 'Москва'
    place_id = 1
    data = {'tags': [{'name': name, 'value': value}]}

    response = await request_proxy_internal_tags(
        taxi_eats_restapp_communications, data, place_id,
    )
    assert response.status_code == 200

    cursor = pgsql['eats_restapp_communications'].cursor()
    cursor.execute(
        'SELECT tag_name, tag_value FROM eats_restapp_communications.tags WHERE place_id = {}'.format(
            place_id,
        ),
    )
    tag = list(cursor)[0]
    assert tag[0] == name
    assert tag[1] == value
