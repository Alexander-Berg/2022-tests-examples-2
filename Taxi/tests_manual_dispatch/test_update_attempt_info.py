import datetime

import pytest


def make_fields_response(**kwargs):
    return {
        'document': {'_id': 'fa952069bc1560b2a37b6e7a364cc01a', **kwargs},
        'order_id': 'fa952069bc1560b2a37b6e7a364cc01a',
        'replica': 'secondary',
        'revision': {'version': 'DAAAAAAABgAMAAQABgAAAPFHWMZzAQAA'},
    }


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_no_attempt(stq_runner):
    await stq_runner.manual_dispatch_update_attempt_info.call(
        task_id='some_uuid',
        args=[],
        kwargs={'attempt_id': 1},
        expect_fail=True,
    )


@pytest.mark.parametrize(
    'status,fields',
    [
        ('pending', {'manual_dispatch': {'attempt_id': 1}}),
        ('filtered', {'manual_dispatch': {'mirror_only': True}}),
        ('pending', {'manual_dispatch': {'attempt_id': 2}}),
        ('filtered', {'manual_dispatch': {'attempt_id': 2}}),
    ],
)
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_no_update_required(
        stq_runner,
        create_order,
        create_dispatch_attempt,
        mock_set_order_fields,
        status,
        fields,
):
    order = create_order()
    attempt = create_dispatch_attempt(
        order_id=order['order_id'], status=status,
    )
    mock_set_order_fields['get_response'] = make_fields_response(**fields)
    await stq_runner.manual_dispatch_update_attempt_info.call(
        task_id='some_uuid',
        args=[],
        kwargs={'attempt_id': attempt['id']},
        expect_fail=False,
    )
    assert mock_set_order_fields['get_handler'].times_called == 1
    assert mock_set_order_fields['handler'].times_called == 0


@pytest.mark.parametrize(
    'status,fields,new_value',
    [
        (
            'pending',
            {'manual_dispatch': {'mirror_only': True}},
            {'manual_dispatch': {'attempt_id': 1}},
        ),
        (
            'filtered',
            {'manual_dispatch': {'attempt_id': 1}},
            {'manual_dispatch': {'mirror_only': True}},
        ),
    ],
)
@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
async def test_update_required(
        stq_runner,
        create_order,
        create_dispatch_attempt,
        mock_set_order_fields,
        status,
        fields,
        new_value,
):
    order = create_order()
    attempt = create_dispatch_attempt(
        order_id=order['order_id'], status=status,
    )
    mock_set_order_fields['get_response'] = make_fields_response(**fields)
    mock_set_order_fields['expected_value'] = {'$set': new_value}
    await stq_runner.manual_dispatch_update_attempt_info.call(
        task_id='some_uuid',
        args=[],
        kwargs={'attempt_id': attempt['id']},
        expect_fail=False,
    )
    assert mock_set_order_fields['get_handler'].times_called == 1
    assert mock_set_order_fields['handler'].times_called == 1


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_expired(
        stq_runner,
        create_order,
        create_dispatch_attempt,
        get_dispatch_attempt,
        mock_set_order_fields,
):
    order = create_order()
    attempt = create_dispatch_attempt(
        order_id=order['order_id'],
        expiration_ts=datetime.datetime(
            2019, 12, 31, 0, 0, 0, tzinfo=datetime.timezone.utc,
        ),
    )
    mock_set_order_fields['get_response'] = make_fields_response(
        manual_dispatch={'mirror_only': True},
    )
    await stq_runner.manual_dispatch_update_attempt_info.call(
        task_id='some_uuid',
        args=[],
        kwargs={'attempt_id': attempt['id']},
        expect_fail=False,
    )
    assert mock_set_order_fields['get_handler'].times_called == 1
    assert mock_set_order_fields['handler'].times_called == 0
    assert (
        get_dispatch_attempt(attempt_id=attempt['id'])['status'] == 'expired'
    )


@pytest.mark.config(MANUAL_DISPATCH_DISABLE_LEGACY_HANDLERS=True)
@pytest.mark.parametrize('status', ['pending', 'filtered'])
async def test_clear_only(
        stq_runner,
        create_order,
        create_dispatch_attempt,
        mock_set_order_fields,
        status,
):
    order = create_order()
    attempt = create_dispatch_attempt(
        order_id=order['order_id'], status=status,
    )
    mock_set_order_fields['get_response'] = make_fields_response(
        manual_dispatch={'attempt_id': attempt['id']},
    )
    mock_set_order_fields['expected_value'] = {
        '$set': {'manual_dispatch': {'mirror_only': True}},
    }
    await stq_runner.manual_dispatch_update_attempt_info.call(
        task_id='some_uuid',
        args=[],
        kwargs={'attempt_id': attempt['id'], 'clear_only': True},
        expect_fail=False,
    )
    assert mock_set_order_fields['get_handler'].times_called == 1
    assert mock_set_order_fields['handler'].times_called == 1
