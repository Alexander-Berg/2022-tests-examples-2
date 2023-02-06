import pytest

from tests_cargo_corp import utils


@pytest.fixture(name='run_task_once')
def _run_task_once(taxi_cargo_corp, testpoint):
    async def _wrapper(task_name):
        @testpoint('%s::result' % task_name)
        def task_result(result):
            pass

        await taxi_cargo_corp.run_task(task_name)
        args = await task_result.wait_call()
        assert not task_result.has_calls

        return args['result']

    return _wrapper


@pytest.fixture(name='run_employee_index_sync')
def _run_employee_index_sync(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-corp-employee-index-sync')

    return _wrapper


@pytest.fixture(name='run_employee_phone_pd_id_sync')
def _run_employee_phone_pd_id_sync(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-corp-employee-phone-pd-id-sync')

    return _wrapper


@pytest.fixture(name='make_client_balance_upsert_request')
def _make_client_balance_upsert_request(taxi_cargo_corp):
    async def wrapper(client_id=utils.CORP_CLIENT_ID, json=None):
        response = await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/balance/upsert',
            headers={'X-B2B-Client-Id': client_id},
            json=json or {},
        )
        return response

    return wrapper


@pytest.fixture(name='make_client_traits_request')
def _make_client_traits_request(taxi_cargo_corp):
    async def wrapper(client_id):
        response = await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/traits',
            headers={'X-B2B-Client-Id': client_id},
        )
        return response

    return wrapper


@pytest.fixture(name='call_internal_employee_upsert')
def _call_internal_employee_upsert(taxi_cargo_corp):
    """
        Call /internal/cargo-corp/v1/client/employee/upsert
    """

    async def wrapper(
            *, request, corp_client_id=utils.CORP_CLIENT_ID, expected_code=200,
    ):
        response = await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/employee/upsert',
            headers={'X-B2B-Client-Id': corp_client_id},
            json=request,
        )

        assert response.status_code == expected_code

        return response.json()

    return wrapper


@pytest.fixture(name='call_internal_employee_list_request')
def _call_internal_employee_list_request(taxi_cargo_corp):
    async def wrapper(
            *,
            corp_client_id=utils.CORP_CLIENT_ID,
            yandex_uid=utils.YANDEX_UID,
            request_mode='b2b',
            params=None,
    ):
        response = await taxi_cargo_corp.post(
            '/internal/cargo-corp/v1/client/employee/list',
            headers={
                'X-B2B-Client-Id': corp_client_id,
                'X-Yandex-Uid': yandex_uid,
                'X-Request-Mode': request_mode,
            },
            params=params or {},
            json={},
        )

        assert response.status_code == 200

        return response.json()

    return wrapper
