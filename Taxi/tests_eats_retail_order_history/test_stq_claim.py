import pytest

from . import utils


def make_kwargs(
        order_nr: str = utils.ORDER_ID,
        claim_id: str = utils.CLAIM_ID,
        corp_client_alias: str = utils.CORP_CLIENT_ALIAS,
        attempt: int = 1,
):
    return {
        'order_nr': order_nr,
        'claim_id': claim_id,
        'corp_client_alias': corp_client_alias,
        'attempt': attempt,
    }


def make_task_id(kwargs: dict):
    return f'{kwargs["order_nr"]}_{kwargs["attempt"]}'


@pytest.mark.parametrize(
    'current_claim_id, current_attempt, attempt, do_set_claim',
    [
        (None, None, 1, True),
        (None, None, 2, True),
        ('current_claim_id', None, 2, True),
        ('current_claim_id', 1, 2, True),
        ('current_claim_id', 2, 1, False),
        ('current_claim_id', 2, 2, False),
    ],
)
async def test_stq_claim(
        stq_runner,
        create_order,
        get_order_by_order_nr,
        current_claim_id,
        current_attempt,
        attempt,
        do_set_claim,
):

    create_order(claim_id=current_claim_id, claim_id_attempt=current_attempt)
    kwargs = make_kwargs(attempt=attempt)

    await stq_runner.eats_retail_order_history_claim.call(
        task_id=make_task_id(kwargs), kwargs=kwargs,
    )

    order = get_order_by_order_nr(kwargs['order_nr'])
    assert (
        order['claim_id'] == utils.CLAIM_ID
        if do_set_claim
        else current_claim_id
    )
    assert (
        order['claim_id_attempt'] == attempt
        if do_set_claim
        else current_attempt
    )


async def test_stq_claim_no_order_reschedule(
        stq_runner, mockserver, get_order_by_order_nr,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    kwargs = make_kwargs()

    await stq_runner.eats_retail_order_history_claim.call(
        task_id=make_task_id(kwargs), kwargs=kwargs,
    )
    assert mock_stq_reschedule.times_called == 1

    order = get_order_by_order_nr(kwargs['order_nr'])
    assert order is None


@pytest.mark.parametrize(
    'retries, exec_tries, reschedule_counter, do_reschedule',
    [
        (1, 0, 0, True),
        (1, 1, 0, False),
        (1, 0, 1, False),
        (5, 1, 3, True),
        (5, 1, 4, False),
    ],
)
async def test_stq_claim_no_order_reschedule_retries(
        stq_runner,
        mockserver,
        taxi_config,
        retries,
        exec_tries,
        reschedule_counter,
        do_reschedule,
):
    taxi_config.set_values(
        {
            'EATS_RETAIL_ORDER_HISTORY_CLAIM_SETTINGS': {
                'stq_settings': {'retries': retries, 'timeout': 0},
            },
        },
    )

    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    kwargs = make_kwargs()

    await stq_runner.eats_retail_order_history_claim.call(
        task_id=make_task_id(kwargs),
        kwargs=kwargs,
        exec_tries=exec_tries,
        reschedule_counter=reschedule_counter,
    )
    assert mock_stq_reschedule.times_called == do_reschedule


async def test_stq_claim_exception_reschedule(
        stq_runner, mockserver, testpoint, create_order,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def mock_stq_reschedule(request):
        return {}

    @testpoint('stq_claim_exception')
    def _stq_claim_exception_tp(data):
        return {'inject_std_exception': True}

    create_order()
    kwargs = make_kwargs()

    await stq_runner.eats_retail_order_history_claim.call(
        task_id=make_task_id(kwargs), kwargs=kwargs,
    )
    assert mock_stq_reschedule.times_called == 1
