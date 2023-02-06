import pytest
import json

from hamcrest import assert_that, has_entries, has_property, equal_to, contains

import metrika.admin.python.cms.frontend.cms.helpers as helpers

pytestmark = pytest.mark.django_db(transaction=True)


def test_create(client):
    valid_post_data = {
        "id": "hello",
        "type": "manual",
        "issuer": "robert",
        "action": "reboot",
        "hosts": [
            "mtdev05e.yandex.ru",
        ],
        "comment": "awesome-comment",
        "extra": {},
    }

    post_data = json.dumps(valid_post_data)
    response = client.post(
        '/api/v1/walle/v14/tasks',
        post_data,
        content_type='application/json',
    )

    assert_that(response, has_property("status_code", equal_to(200)))

    items = helpers.get_judge_queue().list()

    assert_that(items, contains(
        has_entries(
            payload=has_entries(
                walle_id="hello"))))
