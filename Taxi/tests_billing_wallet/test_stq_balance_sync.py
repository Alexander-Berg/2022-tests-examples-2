import copy
import datetime
import json

import pytest
import pytz


_KWARGS = {
    'yandex_uid': 'some_uid',
    'wallet_id': 'w/12345',
    'currency': 'RUB',
    'sub_account': 'deposit',
    'account_id': 9999999990001,
    'journal_doc_id': 9999999990002,
}
_NOW = datetime.datetime(2020, 12, 21, tzinfo=pytz.utc)


async def test_disabled(stq_runner, stq):
    task_id = 'task_id'
    await stq_runner.billing_wallet_balance_sync.call(
        task_id=task_id, args=(), kwargs=_KWARGS,
    )
    assert not stq.billing_wallet_balance_sync.times_called


@pytest.mark.parametrize(
    'data_path',
    [
        'no_cached_balances.json',
        'empty_cached_balances.json',
        'cached_balances_with_other_wallets.json',
        'older_cached_balances.json',
        'older_cached_balances_with_other_wallets.json',
        'younger_cached_balances.json',
    ],
)
@pytest.mark.config(BILLING_WALLET_ENABLE_BALANCE_SYNC=True)
async def test_balance_updated(
        stq_runner,
        stq,
        mongodb,
        load,
        mock_journal_search,
        mock_balances_select,
        data_path,
):
    test_case = json.loads(load(data_path))
    mock_journal_search(
        entries=[
            {
                'doc_id': 9999999990002,
                'account_id': 9999999990001,
                'amount': '123.0000',
                'event_at': '2020-12-04T12:44:00.000000+03:00',
                'journal_entry_id': 8888888880002,
                'reason': 'SIKE',
                'details': {},
            },
        ],
    )
    mock_balances_select(
        [
            {
                'account': {
                    'account_id': 9999999990001,
                    'entity_external_id': 'wallet_id/some_uid',
                    'agreement_id': 'w/12345',
                    'currency': 'RUB',
                    'sub_account': 'deposit',
                },
                'balances': [
                    {
                        'balance': '100500.0000',
                        'last_entry_id': 8888888880003,
                        'accrued_at': '2020-12-04T12:44:00.000000+03:00',
                        'last_created': '2020-12-04T12:44:00.000000+03:00',
                    },
                ],
            },
        ],
    )
    kwargs = dict(_KWARGS)
    kwargs['yandex_uid'] = test_case['yandex_uid']
    await stq_runner.billing_wallet_balance_sync.call(
        task_id='task_id', args=(), kwargs=kwargs,
    )
    assert stq.billing_wallet_balance_sync.times_called == 0
    balances = mongodb.wallet_balances.find_one(
        {'_id': test_case['yandex_uid']},
    )
    assert balances
    # I'm lazy and don't want to write hooks to deserialize time from json
    del balances['updated_at']
    assert balances == test_case['expected_balances']


@pytest.mark.config(BILLING_WALLET_ENABLE_BALANCE_SYNC=True)
async def test_initial_balance(stq_runner, stq, mongodb):
    yandex_uid = 'some-yandex-uid-without-cached-balances-i-swear'
    kwargs = dict(_KWARGS)
    kwargs['yandex_uid'] = yandex_uid
    del kwargs['journal_doc_id']
    await stq_runner.billing_wallet_balance_sync.call(
        task_id='task_id', args=(), kwargs=kwargs,
    )
    assert stq.billing_wallet_balance_sync.times_called == 0
    balances = mongodb.wallet_balances.find_one({'_id': yandex_uid})
    del balances['updated_at']
    assert balances == {
        '_id': yandex_uid,
        'balances': [
            {
                'amount': '0.0000',
                'currency': 'RUB',
                'last_entry_id': 0,
                'sub_account': 'deposit',
                'wallet_id': 'w/12345',
            },
        ],
        'version': 1,
    }


@pytest.mark.parametrize(
    'data_path',
    [
        # Our doc is not present in v2/journal/search answer
        'journal_doc_not_found.json',
        # Our doc is present in v2/journal/search answer and has an entry for
        # our account, but it has no journal_entry_id yet
        'no_journal_entry_id_yet.json',
        # Our doc is present in v2/journal/search answer but does not have an
        # entry for our account
        'no_journal_entry_for_our_account_id.json',
        # Our doc is present in v2/journal/search answer but there are no
        # accounts in balances/select answer
        'no_balances.json',
        # Our doc is present in v2/journal/search answer but balance in
        # balances/select answer is older than our entry
        'old_balance.json',
        # Our doc is present in v2/journal/search answer AND balance in
        # balances/select answer is fresh, but there was a race condition when
        # updating balance
        'update_race.json',
        # Our doc is present in v2/journal/search answer AND we got a balance
        # from balances/select, but there was a race condition when inserting
        # balance
        'insert_race.json',
    ],
)
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(BILLING_WALLET_ENABLE_BALANCE_SYNC=True)
async def test_rescheduled(
        stq_runner,
        stq,
        mongodb,
        load,
        testpoint,
        mock_journal_search,
        mock_balances_select,
        data_path,
):
    test_case = json.loads(load(data_path))

    @testpoint('billing_wallet_balance_sync::insert_race')
    def insert_race(data):
        if test_case.get('insert_race_condition'):
            assert test_case['expected_balances'] is not None
            doc = copy.deepcopy(test_case['expected_balances'])
            doc['updated_at'] = datetime.datetime.utcnow()
            mongodb.wallet_balances.insert(doc)

    @testpoint('billing_wallet_balance_sync::update_race')
    def update_race(data):
        if test_case.get('update_race_condition'):
            query = {'_id': test_case['yandex_uid']}
            update = {'$inc': {'version': 1}}
            mongodb.wallet_balances.update(query, update)

    journal_search_data = _load_json_or_none(
        load, test_case.get('journal_search_data_path'),
    )
    balances_select_data = _load_json_or_none(
        load, test_case.get('balances_select_data_path'),
    )
    journal_search = mock_journal_search(
        entries=journal_search_data['entries'],
    )
    balances_select = mock_balances_select(balances_select_data)
    kwargs = dict(_KWARGS)
    kwargs['yandex_uid'] = test_case['yandex_uid']
    await stq_runner.billing_wallet_balance_sync.call(
        task_id='task_id', args=(), kwargs=kwargs,
    )
    assert stq.billing_wallet_balance_sync.times_called == 1
    balances = mongodb.wallet_balances.find_one(
        {'_id': test_case['yandex_uid']},
    )
    if test_case['expected_balances'] is None:
        assert balances is None
    else:
        assert balances is not None
        del balances['updated_at']
        assert balances == test_case['expected_balances']
    assert (
        journal_search.times_called
        == test_case['expected_journal_search_times_called']
    )
    assert (
        balances_select.times_called
        == test_case['expected_balances_select_times_called']
    )
    assert (
        update_race.times_called
        == test_case['expected_before_update_times_called']
    )
    assert (
        insert_race.times_called
        == test_case['expected_insert_race_times_called']
    )


@pytest.mark.parametrize(
    'deadline,expect_fail',
    [(_NOW - datetime.timedelta(seconds=1), True), (_NOW, False)],
)
@pytest.mark.config(BILLING_WALLET_ENABLE_BALANCE_SYNC=True)
@pytest.mark.now(_NOW.isoformat())
async def test_deadline_missed(
        stq_runner, stq, mongodb, mock_journal_search, deadline, expect_fail,
):
    mock_journal_search(entries=[])
    kwargs = dict(_KWARGS)
    kwargs['yandex_uid'] = 'yandex-uid-without-cached-balances'
    kwargs['deadline'] = deadline.isoformat(timespec='microseconds')
    await stq_runner.billing_wallet_balance_sync.call(
        task_id='task_id', args=(), kwargs=kwargs, expect_fail=expect_fail,
    )
    if expect_fail:
        assert not stq.billing_wallet_balance_sync.times_called
    else:
        assert stq.billing_wallet_balance_sync.times_called == 1


@pytest.fixture(name='mock_balances_select')
def _mock_balances_select(mockserver):
    def do_mock(data):
        @mockserver.json_handler('/billing-accounts/v2/balances/select')
        def handler(request):
            return data

        return handler

    return do_mock


@pytest.fixture(name='mock_journal_search')
def _mock_journal_search(mockserver):
    def do_mock(entries):
        @mockserver.json_handler('/billing-docs/v2/journal/search')
        def handler(request):
            return {'entries': entries}

        return handler

    return do_mock


def _load_json_or_none(load, path):
    if path is not None:
        return json.loads(load(path))
    return None
