from taxi_personal_wallet.modules import wallets


def _make_task_id(task_kwargs):
    # see https://nda.ya.ru/t/C2VaqVIZ3VuJzX

    return '_'.join(
        (
            task_kwargs['event_type'],
            task_kwargs['phonish_uid'],
            task_kwargs['portal_uid'],
        ),
    )


def _check_merge_queue(expected_target_wallet_ids: dict, merge_queue):
    while merge_queue.has_calls:
        call = merge_queue.next_call()
        kwargs = call['kwargs']

        source_wallet = wallets.models.Wallet.from_dict(
            kwargs['source_wallet'],
        )
        target_wallet = wallets.models.Wallet.from_dict(
            kwargs['target_wallet'],
        )

        expected_target_wallet_id = expected_target_wallet_ids.pop(
            source_wallet.wallet_id,
        )
        assert target_wallet.wallet_id.startswith(expected_target_wallet_id)

    assert not expected_target_wallet_ids


async def test_uid_notify_unbind(stq_runner, stq):
    # Shouldn't do anything for the unbind event

    kwargs = {
        'portal_uid': '123456',
        'phonish_uid': '654321',
        'event_type': 'unbind',
    }

    await stq_runner.personal_wallet_uid_notify_handler.call(
        task_id=_make_task_id(kwargs), args=[], kwargs=kwargs,
    )

    assert not stq.personal_wallet_merge_accounts.has_calls


async def test_uid_notify(stq_runner, stq, stq3_context):
    kwargs = {
        'portal_uid': 'portal_uid',
        'phonish_uid': 'phonish_uid',
        'event_type': 'bind',
    }

    await stq_runner.personal_wallet_uid_notify_handler.call(
        task_id=_make_task_id(kwargs), args=[], kwargs=kwargs,
    )

    merge_queue = stq.personal_wallet_merge_accounts

    expected_target_wallet_ids = {
        # source: target
        'wallet_id/5': 'wallet_id/1',
        'wallet_id/6': 'wallet_id/4',
        'wallet_id/7': 'z',  # newly created wallet
    }

    _check_merge_queue(expected_target_wallet_ids, merge_queue)


async def test_uid_notify_already_merged_phonish_uid(
        stq_runner, stq, stq3_context,
):
    kwargs = {
        'portal_uid': 'portal_uid',
        'phonish_uid': 'phonish_uid_already_merged',
        'event_type': 'bind',
    }

    await stq_runner.personal_wallet_uid_notify_handler.call(
        task_id=_make_task_id(kwargs), args=[], kwargs=kwargs,
    )

    merge_queue = stq.personal_wallet_merge_accounts

    expected_target_wallet_ids = {
        # source: target
        'wallet_id/8': 'wallet_id/1',
    }

    _check_merge_queue(expected_target_wallet_ids, merge_queue)
