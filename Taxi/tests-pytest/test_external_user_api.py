import json

import bson
import pytest

from taxi.conf import settings
from taxi.core import arequests
from taxi.core import async
from taxi.external import tvm
from taxi.external import userapi


@pytest.mark.config(
    TVM_RULES=[{'src': 'test-service', 'dst': 'user-api'}],
    TVM_ENABLED=True,
)
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_user_api_create_user_phone(patch, monkeypatch):
    phone = '+79991234567'
    phone_type = 'yandex'
    phone_id = str(bson.ObjectId())
    personal_id = 'personal_id'
    tvm_src_service = 'test-service'
    tvm_ticket = 'tvm_ticket'

    @patch('taxi.core.arequests.request')
    @async.inline_callbacks
    def request(method, url, **kwargs):
        assert method == 'POST'
        assert url == '{}/{}'.format(
            settings.USER_API_BASE_URL, 'user_phones',
        )

        headers = kwargs['headers']
        assert headers['X-Ya-Service-Ticket'] == tvm_ticket

        assert kwargs['json'] == {
            'phone': phone,
            'type': phone_type,
        }

        yield async.return_value(
            arequests.Response(
                status_code=200, content=json.dumps(
                    {
                        'id': phone_id,
                        'phone': phone,
                        'type': phone_type,
                        'personal_phone_id': personal_id,
                        'created': '2019-02-01T13:00:00+0000',
                        'updated': '2019-02-01T13:00:00+0000',
                        'stat': {
                            'big_first_discounts': 0,
                            'complete': 0,
                            'complete_card': 0,
                            'complete_apple': 0,
                            'complete_google': 0
                        },
                        'is_loyal': False,
                        'is_yandex_staff': False,
                        'is_taxi_staff': False,
                    },
                ),
            ),
        )

    monkeypatch.setattr(settings, 'TVM_SRC_SERVICE', tvm_src_service)

    @async.inline_callbacks
    def get_ticket(src_service_name, dst_service_name, log_extra=None):
        assert src_service_name == tvm_src_service
        assert dst_service_name == 'user-api'
        yield async.return_value(tvm_ticket)

    monkeypatch.setattr(
        tvm, 'get_ticket', get_ticket
    )

    new_phone = yield userapi.create_user_phone(
        phone=phone, phone_type=phone_type,
    )

    assert new_phone == {
        'id': phone_id,
        'phone': phone,
        'type': phone_type,
        'personal_phone_id': personal_id,
        'created': '2019-02-01T13:00:00+0000',
        'updated': '2019-02-01T13:00:00+0000',
        'stat': {
            'big_first_discounts': 0,
            'complete': 0,
            'complete_card': 0,
            'complete_apple': 0,
            'complete_google': 0
        },
        'is_loyal': False,
        'is_yandex_staff': False,
        'is_taxi_staff': False,
    }
