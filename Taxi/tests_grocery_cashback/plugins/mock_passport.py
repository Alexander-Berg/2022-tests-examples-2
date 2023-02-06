import pytest


@pytest.fixture(name='passport')
def mock_passport(mockserver):
    class Context:
        def __init__(self):
            self.has_plus = False

        def set_has_plus(self, has_plus):
            self.has_plus = has_plus

        def times_called(self):
            return _mock_blackbox.times_called

    context = Context()

    @mockserver.json_handler('/blackbox')
    def _mock_blackbox(json_request):
        uid = json_request.args['uid']
        return {
            'users': [
                {
                    'uid': {'value': uid},
                    'attributes': {'1015': '1' if context.has_plus else '0'},
                },
            ],
        }

    return context
