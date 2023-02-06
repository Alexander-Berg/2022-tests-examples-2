import typing as tp

import pytest


@pytest.fixture(name='employer_storage')
def _employer_storage():
    class EmployerStorage:
        def __init__(self) -> None:
            self.registered_employers: tp.Set[str] = {'old_employer'}
            self.employer_was_added = False

        def register_employer(self, employer_code):
            if employer_code not in self.registered_employers:
                self.employer_was_added = True
                self.registered_employers.add(employer_code)
                return True
            return False

    return EmployerStorage()


@pytest.fixture(name='mock_employer')
def _mock_employer(mockserver, employer_storage):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/admin/employer/create',
    )
    def mock_employer_create(request):
        assert request.json.get('auto_registration')
        if employer_storage.register_employer(
                request.json.get('employer_meta').get('corp_client_id'),
        ):
            return {'message': 'OK'}
        return mockserver.make_response(
            status=400,
            json={
                'error': (
                    'employer with the same corp_client_id already exists'
                ),
            },
        )

    class Mock:
        def __init__(self, handler, storage) -> None:
            self.handler = handler
            self.storage = storage

    return Mock(mock_employer_create, employer_storage)


@pytest.fixture(name='mock_ndd_activation')
def _mock_ndd_activation(mockserver):
    @mockserver.json_handler('/corp-clients-uservices/v1/services/cargo')
    def mock_ndd_activation(request):
        return {}

    return mock_ndd_activation


async def test_employer_registration(
        mock_employer, stq_runner, mock_ndd_activation,
):

    _stq = stq_runner.logistic_platform_processing_employer_create
    await _stq.call(
        task_id='id',
        kwargs={
            'employer_code': 'some_employer',
            'inn': 'some_inn',
            'client_id': 'some_client_id',
            'brand_name': 'some_brand_name',
        },
        expect_fail=False,
    )
    assert mock_employer.handler.times_called == 1
    assert mock_employer.storage.registered_employers == {
        'old_employer',
        'some_client_id',
    }
    assert mock_ndd_activation.times_called == 1


async def test_try_register_old_employer(
        mock_employer, stq_runner, mock_ndd_activation,
):
    _stq = stq_runner.logistic_platform_processing_employer_create
    await _stq.call(
        task_id='id',
        kwargs={
            'employer_code': 'some_employer',
            'inn': 'some_inn',
            'client_id': 'old_employer',
            'brand_name': 'some_brand_name',
        },
        expect_fail=False,
    )
    assert mock_employer.handler.times_called == 1
    assert mock_ndd_activation.times_called == 1
    assert mock_employer.storage.registered_employers == {'old_employer'}
    assert not mock_employer.storage.employer_was_added
