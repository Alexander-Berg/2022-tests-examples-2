import collections.abc
import inspect
import json

import mock
from passport.backend.tvm_keyring.tvm import TVM


def tvm_ticket_response(dst_to_ticket, dst_to_error=None) -> bytes:
    result = {
        str(dst): {'ticket': ticket}
        for dst, ticket in dst_to_ticket.items()
    }
    if dst_to_error is not None:
        result.update({
            str(dst): {'error': error}
            for dst, error in dst_to_error.items()
        })
    return json.dumps(result).encode('utf8')


def _is_exception_instance_or_type(object):
    """
    Проверить, что объект является инстансом или типом исключения.
    """
    return (
        isinstance(object, Exception) or
        (inspect.isclass(object) and issubclass(object, Exception))
    )


class FakeTVM(object):
    def __init__(self):
        self._mock = mock.Mock()
        self._patch = mock.patch.object(
            TVM,
            '_request',
            self._mock,
        )

    def start(self):
        self._patch.start()

    def stop(self):
        self._patch.stop()

    def set_response_value(self, value, status=200):
        self._mock.return_value = mock.Mock(content=value, status_code=status)
        self._mock.side_effect = None

    def set_response_side_effect(self, side_effect):
        if isinstance(side_effect, collections.abc.Iterable):
            side_effect = [
                item if (
                    hasattr(item, 'content') or
                    _is_exception_instance_or_type(item)
                )
                else mock.Mock(content=item, status_code=200)
                for item in side_effect
            ]
        self._mock.side_effect = side_effect
        self._mock.return_value = None
