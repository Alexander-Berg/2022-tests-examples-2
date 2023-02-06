import json

import pytest

from tests_eats_order_revision import helpers


ORDER_ID = 'test_order'
FIRST_REVISION_ID = 'test_revision_1'
SECOND_REVISION_ID = 'test_revision_2'

DEFAULT_GET_EATER_RESPONSE = {'yandex_uid': '123456', 'eater_id': 'eater1'}


@pytest.mark.parametrize(
    'customer_service_id, need_to_add_discounts',
    [
        pytest.param(
            'composition-products', False, id='revision without discounts',
        ),
        pytest.param(
            'composition-products-with-discount',
            True,
            id='revision without discounts',
        ),
    ],
)
async def test_process_discounts_first_revision(
        stq_runner,
        stq,
        pgsql,
        mock_billing_limits_deposit,
        mock_eats_ordershistory_get_eater,
        load_json,
        customer_service_id,
        need_to_add_discounts,
):
    doc = load_json(
        'one_customer_service_revisions/{}.json'.format(customer_service_id),
    )

    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=FIRST_REVISION_ID,
        document=json.dumps(doc),
    )

    mock_billing_limits = mock_billing_limits_deposit(
        expected_request={
            'limit_ref': 'eats-discounts_3598',
            'amount': '430.000000',
            'currency': 'RUB',
            'event_at': '2022-06-02T09:08:45.980786+00:00',
        },
    )
    mock_eats_ordershistory = mock_eats_ordershistory_get_eater(
        order_id=ORDER_ID, response=DEFAULT_GET_EATER_RESPONSE,
    )

    await stq_runner.eats_order_revision_discounts_processing.call(
        task_id=ORDER_ID,
        kwargs={'order_id': ORDER_ID, 'origin_revision_id': FIRST_REVISION_ID},
    )

    if need_to_add_discounts:
        assert mock_billing_limits.times_called == 1
        assert mock_eats_ordershistory.times_called == 1
        assert stq.eats_discounts_statistics_add.times_called == 1
        discounts_add_stq_param = stq.eats_discounts_statistics_add.next_call()
        assert discounts_add_stq_param['args'] == []
        assert discounts_add_stq_param['eta']
        assert (
            discounts_add_stq_param['id'] == f'{ORDER_ID}_{FIRST_REVISION_ID}'
        )
        assert discounts_add_stq_param['kwargs']['order_id'] == ORDER_ID
        assert (
            discounts_add_stq_param['kwargs']['yandex_uid']
            == DEFAULT_GET_EATER_RESPONSE['yandex_uid']
        )
        assert (
            discounts_add_stq_param['kwargs']['eater_id']
            == DEFAULT_GET_EATER_RESPONSE['eater_id']
        )
        assert len(discounts_add_stq_param['kwargs']['discounts']) == 1
        assert discounts_add_stq_param['kwargs']['discounts'][0] == {
            'discount_id': 3598,
            'discount_value': 430.0,
        }


@pytest.mark.parametrize(
    [
        'first_customer_service_id',
        'second_customer_service_id',
        'need_to_add_discounts',
        'need_to_remove_discounts',
    ],
    [
        pytest.param(
            'composition-products',
            'composition-products-with-discount',
            True,
            False,
            id='new revision has discount; previous has not discounts',
        ),
        pytest.param(
            'composition-products-with-discount',
            'composition-products',
            False,
            True,
            id='previous revision has discount; new has not discounts',
        ),
        pytest.param(
            'composition-products',
            'composition-products',
            False,
            False,
            id='new and previous revision has not discounts',
        ),
        pytest.param(
            'composition-products-with-discount',
            'composition-products-with-discount',
            False,
            False,
            id='new and previous revision has equel discounts',
        ),
        pytest.param(
            'composition-products-with-discount',
            'composition-products-with-discount-2',
            False,
            True,
            id='new revision has less discount amount than previous',
        ),
        pytest.param(
            'composition-products-with-discount-2',
            'composition-products-with-discount',
            False,
            True,
            id='new revision has greater discount amount than previous',
        ),
    ],
)
async def test_process_discounts_two_revisions(
        stq_runner,
        stq,
        pgsql,
        mock_billing_limits_deposit,
        mock_eats_ordershistory_get_eater,
        load_json,
        first_customer_service_id,
        second_customer_service_id,
        need_to_add_discounts,
        need_to_remove_discounts,
):
    first_doc = load_json(
        'one_customer_service_revisions/{}.json'.format(
            first_customer_service_id,
        ),
    )

    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=FIRST_REVISION_ID,
        document=json.dumps(first_doc),
    )

    second_doc = load_json(
        'one_customer_service_revisions/{}.json'.format(
            second_customer_service_id,
        ),
    )

    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=SECOND_REVISION_ID,
        document=json.dumps(second_doc),
    )

    new_discount_value = 0
    previous_discount_value = 0

    if second_doc.get('discounts'):
        new_discount_value = float(
            second_doc['discounts'][0]['discount_amount'],
        )

    if first_doc.get('discounts'):
        previous_discount_value = float(
            first_doc['discounts'][0]['discount_amount'],
        )

    discounts_diff = new_discount_value - previous_discount_value

    mock_billing_limits = mock_billing_limits_deposit(
        expected_request={
            'limit_ref': 'eats-discounts_3598',
            'amount': '{:.6f}'.format(discounts_diff),
            'currency': 'RUB',
            'event_at': '2022-06-02T09:08:45.980786+00:00',
        },
    )
    mock_eats_ordershistory = mock_eats_ordershistory_get_eater(
        order_id=ORDER_ID, response=DEFAULT_GET_EATER_RESPONSE,
    )

    await stq_runner.eats_order_revision_discounts_processing.call(
        task_id=ORDER_ID,
        kwargs={
            'order_id': ORDER_ID,
            'origin_revision_id': SECOND_REVISION_ID,
        },
    )

    assert mock_billing_limits.times_called == int(
        need_to_add_discounts or need_to_remove_discounts,
    )
    assert mock_eats_ordershistory.times_called == int(need_to_add_discounts)
    assert stq.eats_discounts_statistics_add.times_called == int(
        need_to_add_discounts,
    )
    assert stq.eats_discounts_statistics_cancel.times_called == int(
        need_to_remove_discounts,
    )

    if need_to_add_discounts or need_to_add_discounts:
        if need_to_add_discounts:
            stq_param = stq.eats_discounts_statistics_add.next_call()
            assert (
                stq_param['kwargs']['yandex_uid']
                == DEFAULT_GET_EATER_RESPONSE['yandex_uid']
            )
            assert (
                stq_param['kwargs']['eater_id']
                == DEFAULT_GET_EATER_RESPONSE['eater_id']
            )
            assert stq_param['args'] == []
            assert stq_param['eta']
            assert stq_param['id'] == f'{ORDER_ID}_{SECOND_REVISION_ID}'
            assert stq_param['kwargs']['order_id'] == ORDER_ID
            assert len(stq_param['kwargs']['discounts']) == 1
            assert stq_param['kwargs']['discounts'][0] == {
                'discount_id': 3598,
                'discount_value': abs(discounts_diff),
            }

        if need_to_remove_discounts:
            stq_param = stq.eats_discounts_statistics_cancel.next_call()
            assert stq_param['args'] == []
            assert stq_param['eta']
            assert stq_param['id'] == f'{ORDER_ID}_{SECOND_REVISION_ID}'
            assert stq_param['kwargs']['order_id'] == ORDER_ID
            assert len(stq_param['kwargs']['discounts']) == 1
            assert stq_param['kwargs']['discounts'][0] == {
                'discount_id': 3598,
                'discount_value': abs(discounts_diff),
            }


async def test_process_discounts_process_first_when_two_revisions(
        stq_runner,
        stq,
        pgsql,
        mock_billing_limits_deposit,
        mock_eats_ordershistory_get_eater,
        load_json,
):
    filename = 'composition-products-with-discount'
    first_doc = load_json(f'one_customer_service_revisions/{filename}.json')

    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=FIRST_REVISION_ID,
        document=json.dumps(first_doc),
    )

    second_doc = load_json(f'one_customer_service_revisions/{filename}-2.json')

    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=SECOND_REVISION_ID,
        document=json.dumps(second_doc),
    )

    mock_eats_ordershistory = mock_eats_ordershistory_get_eater(
        order_id=ORDER_ID, response=DEFAULT_GET_EATER_RESPONSE,
    )

    mock_billing_limits = mock_billing_limits_deposit(
        expected_request={
            'limit_ref': 'eats-discounts_3598',
            'amount': '430.000000',
            'currency': 'RUB',
            'event_at': '2022-06-02T09:08:45.980786+00:00',
        },
    )

    await stq_runner.eats_order_revision_discounts_processing.call(
        task_id=ORDER_ID,
        kwargs={'order_id': ORDER_ID, 'origin_revision_id': FIRST_REVISION_ID},
    )

    assert mock_billing_limits.times_called == 1
    assert mock_eats_ordershistory.times_called == 1
    assert stq.eats_discounts_statistics_add.times_called == 1
    discounts_add_stq_param = stq.eats_discounts_statistics_add.next_call()
    assert discounts_add_stq_param['args'] == []
    assert discounts_add_stq_param['eta']
    assert discounts_add_stq_param['id'] == f'{ORDER_ID}_{FIRST_REVISION_ID}'
    assert discounts_add_stq_param['kwargs']['order_id'] == ORDER_ID
    assert (
        discounts_add_stq_param['kwargs']['yandex_uid']
        == DEFAULT_GET_EATER_RESPONSE['yandex_uid']
    )
    assert (
        discounts_add_stq_param['kwargs']['eater_id']
        == DEFAULT_GET_EATER_RESPONSE['eater_id']
    )
    assert len(discounts_add_stq_param['kwargs']['discounts']) == 1
    assert discounts_add_stq_param['kwargs']['discounts'][0] == {
        'discount_id': 3598,
        'discount_value': 430.0,
    }


@pytest.mark.config(
    EATS_ORDER_REVISION_DISCOUNTS_PROCESSING_TAGS={
        'skip': ['delivered', 'closed'],
        'remove_all': ['cancelled'],
    },
)
@pytest.mark.parametrize(
    'tags',
    [
        (['cancelled', 'closed']),
        (['delivered', 'closed']),
        (['delivered']),
        (['cancelled']),
        (['closed']),
        ([]),
    ],
)
async def test_discounts_stq_revision_tags_processing(
        stq_runner,
        stq,
        pgsql,
        mock_billing_limits_deposit,
        mock_eats_ordershistory_get_eater,
        load_json,
        tags,
):
    doc = load_json(
        'one_customer_service_revisions/{}.json'.format(
            'composition-products-with-discount',
        ),
    )

    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=FIRST_REVISION_ID,
        document=json.dumps(doc),
    )

    helpers.insert_tags(pgsql=pgsql, revision_id=1, tags=tags)

    if 'cancelled' in tags:
        need_to_update_discounts = True
        discounts_diff = -1 * float(doc['discounts'][0]['discount_amount'])
    elif not tags:
        need_to_update_discounts = True
        discounts_diff = float(doc['discounts'][0]['discount_amount'])
    elif 'closed' in tags or 'delivered' in tags:
        need_to_update_discounts = False
        discounts_diff = 0

    mock_billing_limits = mock_billing_limits_deposit(
        expected_request={
            'limit_ref': 'eats-discounts_3598',
            'amount': '{:.6f}'.format(discounts_diff),
            'currency': 'RUB',
            'event_at': '2022-06-02T09:08:45.980786+00:00',
        },
    )
    mock_eats_ordershistory = mock_eats_ordershistory_get_eater(
        order_id=ORDER_ID, response=DEFAULT_GET_EATER_RESPONSE,
    )

    await stq_runner.eats_order_revision_discounts_processing.call(
        task_id=ORDER_ID,
        kwargs={'order_id': ORDER_ID, 'origin_revision_id': FIRST_REVISION_ID},
    )

    assert mock_billing_limits.times_called == int(need_to_update_discounts)
    assert mock_eats_ordershistory.times_called == int(
        need_to_update_discounts and not tags,
    )

    if need_to_update_discounts:
        if not tags:
            assert stq.eats_discounts_statistics_add.times_called == 1
            stq_param = stq.eats_discounts_statistics_add.next_call()
            assert (
                stq_param['kwargs']['yandex_uid']
                == DEFAULT_GET_EATER_RESPONSE['yandex_uid']
            )
            assert (
                stq_param['kwargs']['eater_id']
                == DEFAULT_GET_EATER_RESPONSE['eater_id']
            )
        else:
            assert stq.eats_discounts_statistics_cancel.times_called == 1
            stq_param = stq.eats_discounts_statistics_cancel.next_call()

        assert stq_param['args'] == []
        assert stq_param['eta']
        assert stq_param['id'] == f'{ORDER_ID}_{FIRST_REVISION_ID}'
        assert stq_param['kwargs']['order_id'] == ORDER_ID
        assert len(stq_param['kwargs']['discounts']) == 1
        assert stq_param['kwargs']['discounts'][0] == {
            'discount_id': 3598,
            'discount_value': abs(discounts_diff),
        }


@pytest.mark.parametrize(
    ['ordershistory_status', 'billing_limits_status'],
    [(500, 500), (200, 500), (500, 200), (200, 200)],
)
async def test_discounts_processing_stq_fails(
        stq_runner,
        pgsql,
        mock_billing_limits_deposit,
        mock_eats_ordershistory_get_eater,
        load_json,
        ordershistory_status,
        billing_limits_status,
):
    doc = load_json(
        'one_customer_service_revisions/{}.json'.format(
            'composition-products-with-discount',
        ),
    )

    helpers.insert_revision(
        pgsql=pgsql,
        order_id=ORDER_ID,
        origin_revision_id=FIRST_REVISION_ID,
        document=json.dumps(doc),
    )

    mock_billing_limits_deposit(
        expected_request={
            'limit_ref': 'eats-discounts_3598',
            'amount': '{:.6f}'.format(
                float(doc['discounts'][0]['discount_amount']),
            ),
            'currency': 'RUB',
            'event_at': '2022-06-02T09:08:45.980786+00:00',
        },
        status=billing_limits_status,
    )
    mock_eats_ordershistory_get_eater(
        order_id=ORDER_ID,
        response=DEFAULT_GET_EATER_RESPONSE,
        status=ordershistory_status,
    )

    await stq_runner.eats_order_revision_discounts_processing.call(
        task_id=ORDER_ID,
        kwargs={'order_id': ORDER_ID, 'origin_revision_id': FIRST_REVISION_ID},
        expect_fail=(
            billing_limits_status != 200 or ordershistory_status != 200
        ),
    )
