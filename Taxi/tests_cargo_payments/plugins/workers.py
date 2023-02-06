import pytest


@pytest.fixture(name='run_operations_executor')
def _run_operations_executor(run_task_once, autorun_stq):
    async def _wrapper():
        result = await run_task_once('cargo-payments-operation-executor')
        await autorun_stq('cargo_payments_process_operation')
        return result

    return _wrapper


@pytest.fixture(name='run_transactions_scanner')
def _run_transactions_scanner(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-payments-transactions-scanner')

    return _wrapper


@pytest.fixture(name='run_metrics_collector')
def _run_metrics_collector(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-payments-metrics-collector')

    return _wrapper


@pytest.fixture(name='run_billing_tasks_checker')
def _run_billing_tasks_checker(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-payments-billing-tasks-checker')

    return _wrapper


@pytest.fixture(name='run_tid_deactivator')
def _run_tid_deactivator(run_task_once):
    async def _wrapper():
        return await run_task_once('cargo-payments-tid-deactivator')

    return _wrapper


@pytest.fixture(name='run_task_once')
def _run_task_once(taxi_cargo_payments, testpoint):
    async def _wrapper(task_name):
        await taxi_cargo_payments.run_task(task_name)

    return _wrapper


@pytest.fixture(name='get_worker_state')
async def _get_worker_state(pgsql):
    def wrapper(worker_name: str):
        cursor = pgsql['cargo_payments'].cursor()
        cursor.execute(
            'SELECT details FROM cargo_payments.worker_state WHERE name=\'%s\''
            % worker_name,
        )
        return list(row[0] for row in cursor)

    return wrapper
