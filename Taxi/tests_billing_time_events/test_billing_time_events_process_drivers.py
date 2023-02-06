import pytest

_NOW = '2020-08-14T00:00:00.00001+00:00'
_TEST_MODE_PREFIX = 'dry/'


def _enumerate_calls(func):
    n_call = 0

    def wrapper(request):
        nonlocal n_call
        n_call += 1
        return func(request, n_call)

    return wrapper


def _get_accounts_id_maker():
    accounts = {}

    def wrapper(acc):
        nonlocal accounts
        acc_key = (
            acc['agreement_id'],
            acc['currency'],
            acc['entity_external_id'],
            acc['sub_account'],
        )
        accounts.setdefault(acc_key, len(accounts) + 1)
        return accounts.get(acc_key)

    return wrapper


@pytest.mark.parametrize('test_data_json', ['test_all_the_way.json'])
@pytest.mark.pgsql('billing_time_events@1', files=['events.sql'])
@pytest.mark.now(_NOW)
@pytest.mark.config(
    BILLING_TIME_EVENTS_DRIVERS_PROCESSING_SETTINGS={
        'create-journal-doc': True,
        'create-shift-ended-doc': True,
        'schedule-shift-ended-processing': True,
    },
)
async def test_all_the_way(
        test_data_json, *, load_json, mockserver, stq_runner,
):
    test_data = load_json(test_data_json)

    @mockserver.json_handler('/billing-docs/v1/docs/search')
    def _docs_search(request):
        assert request.json == test_data['docs_search_request'], request.json
        return test_data['docs_search_response']

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        expected = test_data['rules_select_request']
        assert expected == request.json, request.json
        return test_data['rules_select_response']

    @mockserver.json_handler('/billing-accounts/v1/entities/search')
    def _entities_search(request):
        expected = test_data['entities_search_request']
        assert expected == request.json
        return mockserver.make_response(json=[], status=200)

    @mockserver.json_handler('/billing-accounts/v1/entities/create')
    def _entities_create(request):
        expected = test_data['entities_create_request']
        assert expected == request.json
        request.json.update(created=_NOW)
        return request.json

    @mockserver.json_handler('/billing-accounts/v1/accounts/search')
    @_enumerate_calls
    def _accounts_search(request, n_call):
        if n_call == 1:
            expected = test_data['accounts_search_guarantee_request']
            assert expected == request.json
            return []
        if n_call == 2:
            expected = test_data['accounts_search_free_minutes_request']
            assert expected == request.json
            return []
        if n_call == 3:
            expected = test_data['accounts_search_unfit_free_minutes_request']
            assert expected == request.json
            return []
        raise ValueError('Invalid call number')

    @mockserver.json_handler('/billing-accounts/v1/accounts/create')
    @_enumerate_calls
    def _accounts_create(request, n_call):
        if n_call == 1:
            expected = test_data['accounts_create_guarantee_request']
            assert expected == request.json
        elif n_call == 2:
            expected = test_data['accounts_create_free_minutes_request']
            assert expected == request.json
        elif n_call == 3:
            expected = test_data['accounts_create_unfit_free_minutes_request']
            assert expected == request.json
        else:
            raise ValueError('Invalid call number')
        request.json.update(account_id=n_call, opened=_NOW)
        return request.json

    @mockserver.json_handler('/billing-docs/v2/docs/execute')
    def _docs_execute(request):
        assert request.json == test_data['docs_execute_request']
        return {'docs': []}

    @mockserver.json_handler('/billing_subventions/v1/shifts/open')
    def _shifts_open(request):
        expected = test_data['shifts_open_request']
        assert expected == request.json, request.json
        return {'doc_id': 1}

    await stq_runner.billing_time_events_process_drivers.call(
        task_id='sample_task', args=test_data['stq_args'],
    )

    assert _docs_search.times_called == 1
    assert _rules_select.times_called == 1
    assert _entities_search.times_called == 1
    assert _entities_create.times_called == 1
    assert _accounts_search.times_called == 2
    assert _accounts_create.times_called == 2
    assert _docs_execute.times_called == 1
    assert _shifts_open.times_called == 1


@pytest.mark.parametrize('test_data_json', ['test_all_the_way.json'])
@pytest.mark.config(
    BILLING_TIME_EVENTS_DRIVERS_PROCESSING_SETTINGS={'is-enabled': False},
)
async def test_task_can_be_disabled(stq_runner, load_json, test_data_json):
    test_data = load_json(test_data_json)
    await stq_runner.billing_time_events_process_drivers.call(
        task_id='sample_task', args=test_data['stq_args'],
    )


@pytest.mark.parametrize(
    'test_data_json,',
    [
        'test_journal_is_saved_if_two_driver_modes_in_interval.json',
        'test_journal_is_saved_if_two_shifts_in_interval.json',
        'test_journal_is_saved_if_two_rules_in_interval.json',
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                BILLING_TIME_EVENTS_DRIVERS_PROCESSING_SETTINGS={
                    'create-journal-doc': True,
                    'create-shift-ended-doc': False,
                    'schedule-shift-ended-processing': False,
                },
                BILLING_TIME_EVENTS_HONOR_DST='yes',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_TIME_EVENTS_DRIVERS_PROCESSING_SETTINGS={
                    'create-journal-doc': True,
                    'create-shift-ended-doc': False,
                    'schedule-shift-ended-processing': False,
                },
                BILLING_TIME_EVENTS_HONOR_DST='no',
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                BILLING_TIME_EVENTS_DRIVERS_PROCESSING_SETTINGS={
                    'create-journal-doc': True,
                    'create-shift-ended-doc': False,
                    'schedule-shift-ended-processing': False,
                },
                BILLING_TIME_EVENTS_HONOR_DST='test',
            ),
        ),
    ],
)
@pytest.mark.pgsql('billing_time_events@1', files=['events.sql'])
@pytest.mark.now(_NOW)
async def test_journals_is_saved(
        test_data_json, *, load_json, mockserver, stq_runner,
):
    test_data = load_json(test_data_json)

    @mockserver.json_handler('/billing-docs/v1/docs/search')
    def _docs_search(request):
        return test_data['docs_search_response']

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    @_enumerate_calls
    def _rules_select(request, n_call):
        resp_name_by_call = f'rules_select_response_{n_call}'
        if resp_name_by_call in test_data:
            return test_data[resp_name_by_call]
        return test_data['rules_select_response']

    @mockserver.json_handler('/billing-accounts/v1/entities/search')
    def _entities_search(request):
        request.json.update(created=_NOW, kind='driver')
        return [request.json]

    accounts_id_maker = _get_accounts_id_maker()

    @mockserver.json_handler('/billing-accounts/v1/accounts/search')
    def _accounts_search(request):
        account_id = accounts_id_maker(request.json)
        request.json.update(account_id=account_id, opened=_NOW, expired=_NOW)
        return [request.json]

    @mockserver.json_handler('/billing-docs/v2/docs/execute')
    def _docs_execute(request):
        assert request.json == test_data['docs_execute_request']
        return {'docs': []}

    await stq_runner.billing_time_events_process_drivers.call(
        task_id='sample_task', args=test_data['stq_args'],
    )

    assert _docs_execute.times_called == 1


@pytest.mark.parametrize(
    'test_data_json, is_test_mode',
    [
        pytest.param(
            'test_test_mode.json',
            False,
            marks=pytest.mark.config(
                BILLING_TIME_EVENTS_DRIVERS_PROCESSING_SETTINGS={
                    'create-journal-doc': True,
                    'is-test-mode': False,
                },
            ),
        ),
        pytest.param(
            'test_test_mode.json',
            True,
            marks=pytest.mark.config(
                BILLING_TIME_EVENTS_DRIVERS_PROCESSING_SETTINGS={
                    'create-journal-doc': True,
                    'is-test-mode': True,
                },
            ),
        ),
    ],
)
@pytest.mark.pgsql('billing_time_events@1', files=['events.sql'])
@pytest.mark.now(_NOW)
async def test_test_mode(
        test_data_json, is_test_mode, *, load_json, mockserver, stq_runner,
):
    test_data = load_json(test_data_json)

    @mockserver.json_handler('/billing-docs/v1/docs/search')
    def _docs_search(request):
        return test_data['docs_search_response']

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        return test_data['rules_select_response']

    @mockserver.json_handler('/billing-accounts/v1/entities/search')
    def _entities_search(request):
        request.json.update(created=_NOW, kind='driver')
        return [request.json]

    @mockserver.json_handler('/billing-accounts/v1/accounts/search')
    @_enumerate_calls
    def _accounts_search(request, n_call):
        if is_test_mode:
            assert request.json['sub_account'].startswith(_TEST_MODE_PREFIX)
        else:
            assert not request.json['sub_account'].startswith(
                _TEST_MODE_PREFIX,
            )
        request.json.update(account_id=n_call, opened=_NOW, expired=_NOW)
        return [request.json]

    @mockserver.json_handler('/billing-docs/v2/docs/execute')
    def _docs_execute(request):
        for doc in request.json['docs']:
            if is_test_mode:
                assert doc['topic'].startswith(_TEST_MODE_PREFIX)
            else:
                assert not doc['topic'].startswith(_TEST_MODE_PREFIX)
        return {'docs': []}

    await stq_runner.billing_time_events_process_drivers.call(
        task_id='sample_task', args=test_data['stq_args'],
    )

    assert _accounts_search.times_called == 2
    assert _docs_execute.times_called == 1


@pytest.mark.parametrize(
    'test_data_json', ['test_additional_journal_splitting.json'],
)
@pytest.mark.config(
    BILLING_TIME_EVENTS_DRIVERS_PROCESSING_SETTINGS={
        'create-journal-doc': True,
        'create-shift-ended-doc': False,
        'schedule-shift-ended-processing': False,
    },
)
@pytest.mark.pgsql(
    'billing_time_events@1',
    files=['events_for_test_additional_journal_splitting.sql'],
)
@pytest.mark.now(_NOW)
async def test_additional_journal_splitting(
        test_data_json, *, load_json, mockserver, stq_runner,
):
    test_data = load_json(test_data_json)

    @mockserver.json_handler('/billing-docs/v1/docs/search')
    def _docs_search(request):
        return test_data['docs_search_response']

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        return test_data['rules_select_response']

    @mockserver.json_handler('/billing-accounts/v1/entities/search')
    def _entities_search(request):
        request.json.update(created=_NOW, kind='driver')
        return [request.json]

    accounts_id_maker = _get_accounts_id_maker()

    @mockserver.json_handler('/billing-accounts/v1/accounts/search')
    def _accounts_search(request):
        account_id = accounts_id_maker(request.json)
        request.json.update(account_id=account_id, opened=_NOW, expired=_NOW)
        return [request.json]

    @mockserver.json_handler('/billing-docs/v2/docs/execute')
    def _docs_execute(request):
        assert request.json == test_data['docs_execute_request']
        return {'docs': []}

    await stq_runner.billing_time_events_process_drivers.call(
        task_id='sample_task', args=test_data['stq_args'],
    )

    assert _docs_execute.times_called == 1
