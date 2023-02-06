import json


async def test_insert_lb(stq_runner, get_personal_accounts):
    data = json.dumps(
        {
            'classname': 'PersonalAccount',
            'obj': {
                'contract_id': 0,
                'external_id': 'ЛСТ-1',
                'id': 0,
                'service_code': 'YANDEX_SERVICE',
            },
            'version': 0,
        },
    )

    accounts = get_personal_accounts()
    assert accounts == []

    await stq_runner.balance_replica_personal_accounts.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'error_msg': 'Field \'obj.id\' is missing',
            'raw_data': data,
            'source': 'lb',
        },
    )

    accounts = get_personal_accounts()
    assert accounts == [
        {
            'contract_id': 0,
            'external_id': 'ЛСТ-1',
            'id': 0,
            'service_code': 'YANDEX_SERVICE',
            'version': 0,
        },
    ]


async def test_error_lb(stq_runner, get_personal_accounts):
    data = json.dumps(
        {'classname': 'PersonalAccount', 'obj': None, 'version': 0},
    )

    accounts = get_personal_accounts()
    assert accounts == []

    await stq_runner.balance_replica_personal_accounts.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'error_msg': 'Field \'obj.id\' is missing',
            'raw_data': data,
            'source': 'lb',
        },
        expect_fail=True,
    )

    accounts = get_personal_accounts()
    assert accounts == []


async def test_insert_yt(stq_runner, get_personal_accounts):
    data = json.dumps(
        {
            'pa.obj': {
                'external_id': 'ЛСТ-1',
                'service_code': 'YANDEX_SERVICE',
            },
            'pa.id': 0,
            'pa.contract_id': 0,
            'pa.version': 0,
        },
    )

    accounts = get_personal_accounts()
    assert accounts == []

    await stq_runner.balance_replica_personal_accounts.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'error_msg': (
                'Field \'/\' is of a wrong type. '
                'Expected: uintValue, actual: nullValue'
            ),
            'raw_data': data,
            'source': 'yt',
        },
    )

    accounts = get_personal_accounts()
    assert accounts == [
        {
            'contract_id': 0,
            'external_id': 'ЛСТ-1',
            'id': 0,
            'service_code': 'YANDEX_SERVICE',
            'version': 0,
        },
    ]


async def test_error_yt(stq_runner, get_personal_accounts):
    data = json.dumps(
        {'pa.obj': None, 'pa.id': 0, 'pa.contract_id': None, 'pa.version': 0},
    )

    accounts = get_personal_accounts()
    assert accounts == []

    await stq_runner.balance_replica_personal_accounts.call(
        task_id='sample_task',
        args=[],
        kwargs={
            'error_msg': (
                'Field \'/\' is of a wrong type. '
                'Expected: uintValue, actual: nullValue'
            ),
            'raw_data': data,
            'source': 'yt',
        },
        expect_fail=True,
    )

    accounts = get_personal_accounts()
    assert accounts == []
