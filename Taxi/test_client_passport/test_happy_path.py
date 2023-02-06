from typing import Optional

import pytest


@pytest.fixture(name='mock_blackbox')
def _mock_blackbox(mockserver):
    def mock_maker(
            method: str = 'userinfo',
            response: Optional[dict] = None,
            expected_request_args: Optional[dict] = None,
    ):
        if expected_request_args is None:
            expected_request_args = {}
        if response is None:
            response = {'users': []}

        @mockserver.json_handler('/blackbox', prefix=True)
        def _handle(request):
            default_expected_args = {
                'method': method,
                'dbfields': 'subscription.suid.669',
                'aliases': '1,10,16',
                'format': 'json',
            }

            assert request.method == 'GET'
            assert request.path == '/blackbox/blackbox'

            assert request.args == {
                **default_expected_args,
                **expected_request_args,
            }

            return response

        return _handle

    return mock_maker


async def test_passport(library_context, mockserver, mock_blackbox):
    mock_blackbox(
        expected_request_args={
            'userip': '127.0.0.1',
            'dbfields': 'subscription.suid.669',
            'aliases': '1,10,16',
            'login': 'seanchaidh',
        },
        response={'users': [{'uid': {'value': 'azaz'}}]},
    )
    result = await library_context.client_passport.get_info_by_login(
        'seanchaidh', '127.0.0.1',
    )

    assert result == {'uid': 'azaz'}


async def test_uid_info_attributes(library_context, mock_blackbox):
    uid = '123456'

    mock_blackbox(
        expected_request_args={
            'uid': uid,
            'attributes': '1015,1007',
            'userip': '127.0.0.1',
        },
        response={
            'users': [
                {
                    'uid': {'value': uid},
                    'attributes': {'1015': 1, '1007': 'ФИО'},
                    'login': 'danielkono',
                },
            ],
        },
    )

    result = await library_context.client_passport.get_info_by_uid(
        uid, '127.0.0.1', attributes=['1015', '1007'],
    )

    assert result == {
        'uid': uid,
        'attributes': {'1015': 1, '1007': 'ФИО'},
        'login': 'danielkono',
    }


@pytest.mark.parametrize('expected_has_plus', [False, True])
async def test_user_has_plus(
        library_context, mock_blackbox, expected_has_plus,
):
    uid = '123456'

    mock_blackbox(
        expected_request_args={
            'uid': uid,
            'attributes': '1015',
            'userip': '127.0.0.1',
        },
        response={
            'users': [
                {
                    'uid': {'value': uid},
                    'attributes': {'1015': 1 if expected_has_plus else 0},
                    'login': 'danielkono',
                },
            ],
        },
    )

    has_plus = await library_context.client_passport.user_has_plus(uid)
    assert has_plus == expected_has_plus
