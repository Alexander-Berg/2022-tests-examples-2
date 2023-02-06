DEFAULT_KWARGS = {
    'personal_phone_id': 'personal_phone_id',
    'yandex_uid': 'yandex_uid',
    'user_id': 'user_id',
    'locale': 'en',
    'wind_user_id': 'wind_user_id',
    'promocode_type': 'free_unlock',
    'promocode': 'xxx',
}


def fetch_entries(pgsql):
    cursor = pgsql['talaria_misc'].cursor()
    cursor.execute(
        f'SELECT wind_user_id, promocode_type, promocode '
        f'FROM talaria_misc.auto_promocodes;',
    )
    return cursor.fetchall()


async def test_happy_path_and_retry(
        mockserver, stq_runner, wind_user_auth_mock, pgsql,
):
    @mockserver.json_handler('/wind/pf/v1/promotionCodes/records')
    def _mock_use_promocode(request):
        return {'result': 0}

    await stq_runner.talaria_misc_auto_promocode_apply.call(
        task_id='operation_id_value', kwargs=DEFAULT_KWARGS,
    )

    assert _mock_use_promocode.times_called == 1
    assert fetch_entries(pgsql) == [('wind_user_id', 'free_unlock', 'xxx')]


async def test_retry(mockserver, stq_runner, wind_user_auth_mock, pgsql):
    @mockserver.json_handler('/wind/pf/v1/promotionCodes/records')
    def _mock_use_promocode(request):
        return {'result': -503}

    await stq_runner.talaria_misc_auto_promocode_apply.call(
        task_id='operation_id_value', kwargs=DEFAULT_KWARGS,
    )
    assert _mock_use_promocode.times_called == 1
    assert fetch_entries(pgsql) == [('wind_user_id', 'free_unlock', 'xxx')]

    await stq_runner.talaria_misc_auto_promocode_apply.call(
        task_id='operation_id_value', kwargs=DEFAULT_KWARGS,
    )
    assert _mock_use_promocode.times_called == 2
    assert fetch_entries(pgsql) == [('wind_user_id', 'free_unlock', 'xxx')]
