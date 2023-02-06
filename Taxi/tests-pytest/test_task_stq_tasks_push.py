import pytest

from taxi.core import async
from taxi_stq.tasks import push


@pytest.inline_callbacks
def test_yandex_user_communication(patch):
    @patch('taxi.external.communications.send_user_push_bulk')
    @async.inline_callbacks
    def send_user_push_bulk(
            users, data, tvm_src_service_name, intent=None,
            confirm=False, log_extra=None
    ):
        assert len(users) == 2
        yield
        async.return_value([(True, {})])

    yield push.task('push_id_1')
