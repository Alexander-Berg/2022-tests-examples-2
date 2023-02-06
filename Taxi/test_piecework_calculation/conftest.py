# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import piecework_calculation.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['piecework_calculation.generated.service.pytest_plugins']


@pytest.fixture()
def mock_uuid4(patch):
    @patch('uuid.uuid4')
    class _Uuid4:
        hex = 'some_uuid'

    return _Uuid4


@pytest.fixture()
def mock_base_rule_processor_run(patch):
    @patch('piecework_calculation.calculation_rules.BaseRulesProcessor.run')
    async def _func(*args, **kwargs):
        pass

    return _func


@pytest.fixture
def mock_uuid4_list(patch):
    def _do_mock():
        @patch('uuid.uuid4')
        def uuid4():
            uuid4.index += 1

            class _uuid4:
                hex = 'uuid_{}'.format(uuid4.index)

            return _uuid4()

        uuid4.index = 0

    return _do_mock


@pytest.fixture
def mock_oebs_holidays(mockserver):
    def _wrap(response):
        @mockserver.json_handler('/oebs/rest/holiday')
        def _holiday(request):
            return response

        return _holiday

    return _wrap


@pytest.fixture
def mock_oebs_payments(mockserver):
    @mockserver.json_handler('/oebs/rest/loadSdelNonstd')
    def _load_sdel_nonstd(request):
        return {'status': 'OK'}

    return _load_sdel_nonstd


@pytest.fixture
def mock_oebs_dismissal_payments(mockserver):
    @mockserver.json_handler('/oebs/rest/loadSdelTerm')
    def _load_sdel_term(request):
        return {'status': 'OK'}

    return _load_sdel_term


@pytest.fixture
def mock_oebs_get_sdel_term(mockserver):
    def _wrap(response):
        @mockserver.json_handler('oebs/rest/getSdelTerm')
        def _load_sdel_term(request):
            return response

        return _load_sdel_term

    return _wrap


@pytest.fixture
def mock_cmpd_employees(mockserver):
    def _wrap(response):
        @mockserver.json_handler('/compendium/api/v2/piecework_employees')
        def _cmpd_employees(request):
            return response

        return _cmpd_employees

    return _wrap


@pytest.fixture
def mock_agent_employees(mockserver):
    def _wrap(response):
        @mockserver.json_handler('/agent/piecework/employee')
        def _piecework_employees(request):
            return response

        return _piecework_employees

    return _wrap


@pytest.fixture
def mock_agent_employees_by_project(mockserver):
    def _wrap(response_mapping):
        @mockserver.json_handler('/agent/piecework/employee')
        def _piecework_employees(request):
            data = request.json
            return response_mapping[data['project'] + '_' + data['country']]

        return _piecework_employees

    return _wrap


@pytest.fixture
def mock_create_draft(mockserver):
    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    def _create(request):
        return {'id': 1, 'version': 1, 'tickets': ['SOMEQUEUE-1']}

    return _create


@pytest.fixture
def mock_finish_draft(mockserver):
    @mockserver.json_handler(
        r'/taxi-approvals/drafts/(?P<draft_id>\w+)/finish/', regex=True,
    )
    def _finish(request, draft_id):
        return {'id': int(draft_id)}

    return _finish


@pytest.fixture
def mock_payday_upload(mockserver):
    def _wrap(data, login=None, status=None):
        @mockserver.json_handler('/oebs_payday/payday/upload')
        def _mock_payday_upload(request):
            if data.get('people'):
                if login:
                    data['people'][0]['login'] = login
                elif data['people'][0]['login'] and status:
                    return {'status': status}
                else:
                    data['people'][0]['login'] = 'test_' + str(
                        len(request.json['people']),
                    )
            return data

        return _mock_payday_upload

    return _wrap


@pytest.fixture
def mock_yandex_calendar(mockserver):
    def _wrap(holidays):
        @mockserver.json_handler('/yandex-calendar/internal/get-holidays')
        def _dummy_internal_get_holidays(request):
            return holidays[
                '{}+{}'.format(request.args['to'], request.args['for'])
            ]

        return _dummy_internal_get_holidays

    return _wrap
