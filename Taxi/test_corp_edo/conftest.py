# pylint: disable=redefined-outer-name
import pytest

import corp_edo.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['corp_edo.generated.service.pytest_plugins']


# NOTE: yandex_test in url paths actually is a parameter of request
@pytest.fixture
def mock_uzedo(mockserver, load_json):
    class MockUzedo:

        """
        Mapped by hand because uzedo invitation data structure
        does not contain inn, but is still retrieved by inn (and not id).

        Mock is shared between cron/web tests, so json files with uzedo
        responses must be identical in
        web/static/default and cron/static/default
        """

        create_invitations = load_json(
            'uzedo_create_invitation_responses.json',
        )
        create_invitations_by_inn = {'1503009020': create_invitations[0]}

        get_invitations = load_json('uzedo_get_invitation_responses.json')
        get_invitations_by_inn = {
            '1558904566': get_invitations[0],
            '1427991070': get_invitations[1],
            '1225672864': get_invitations[2],
        }

        reinvite_invitations = load_json('uzedo_reinvite_responses.json')
        reinvte_invitations_by_inn = {'1912187970': reinvite_invitations[0]}

        @staticmethod
        @mockserver.json_handler('/uzedo/yandex_test/client_api/yandex/invite')
        async def mock_invite(request):
            if request.method == 'POST':
                inn = request.json['inn']
                invitation = MockUzedo.create_invitations_by_inn.get(inn)
                if invitation:
                    return mockserver.make_response(
                        json={'data': invitation}, status=200,
                    )
                return mockserver.make_response(status=500)
            if request.method == 'GET':
                inn = request.query['inn']
                invitation = MockUzedo.get_invitations_by_inn.get(inn)
                return mockserver.make_response(json=invitation, status=200)
            return mockserver.make_response(status=500)

        @staticmethod
        @mockserver.json_handler(
            '/uzedo/yandex_test/client_api/yandex/reInvite',
        )
        async def mock_reinvite(request):
            inn = request.json['inn']
            invitation = MockUzedo.reinvte_invitations_by_inn.get(inn)
            if invitation:
                return mockserver.make_response(
                    json={'data': invitation}, status=200,
                )
            return mockserver.make_response(status=500)

        @staticmethod
        @mockserver.json_handler(
            '/uzedo/yandex_test/client_api/yandex/invite/updateStatus',
        )
        async def mock_update_status_yandex_test(request):
            return mockserver.make_response(
                json={'totalInvites': 2, 'updatedInvites': 1}, status=200,
            )

        @staticmethod
        @mockserver.json_handler(
            '/uzedo/yandex/client_api/yandex/invite/updateStatus',
        )
        async def mock_update_status_yandex(request):
            return mockserver.make_response(
                json={'totalInvites': 2, 'updatedInvites': 1}, status=200,
            )

        @staticmethod
        @mockserver.json_handler(
            '/uzedo/taxi/client_api/yandex/invite/updateStatus',
        )
        async def mock_update_status_taxi(request):
            return mockserver.make_response(
                json={'totalInvites': 2, 'updatedInvites': 1}, status=200,
            )

    return MockUzedo()
