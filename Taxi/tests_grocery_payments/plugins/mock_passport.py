# pylint: disable=import-error
import dataclasses
import typing

from grocery_mocks.utils.handle_context import HandleContext
import pytest


@dataclasses.dataclass
class User:
    uid: str
    staff_login: typing.Optional[str] = None
    staff_flag: bool = False

    def to_dict(self):
        result = {'uid': {'value': self.uid}}
        if self.staff_login is not None:
            result['aliases'] = {'13': self.staff_login}
        if self.staff_flag:
            result['dbfields'] = {'subscription.suid.669': '1'}
        return result


@pytest.fixture(name='passport', autouse=True)
def mock_passport(mockserver):
    class Context:
        def __init__(self):
            self.blackbox = HandleContext()
            self.check_blackbox_data = None
            self.user = None

    context = Context()

    @mockserver.json_handler('/blackbox')
    def _mock_blackbox(request):
        context.blackbox.process(request.args)

        user = context.user.to_dict() if context.user else {}
        return {'users': [user]}

    return context
