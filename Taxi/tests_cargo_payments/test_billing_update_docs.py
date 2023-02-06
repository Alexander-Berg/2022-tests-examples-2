import pytest


def _make_doc(
        *,
        billing_doc_id,
        payment_status='RECONCILED',
        payment_order_number='1122',
        **kwargs,
):
    result = dict(**kwargs)
    result['billing_doc_id'] = billing_doc_id
    if payment_status is not None:
        result['payment_status'] = payment_status
    if payment_order_number is not None:
        result['payment_order_number'] = payment_order_number
    return result


@pytest.fixture(name='get_oebs_data')
async def _get_oebs_data(pgsql):
    def wrapper(billing_doc_id):
        cursor = pgsql['cargo_payments'].dict_cursor()
        cursor.execute(
            """
            SELECT
                approve_instant,
                oebs_sync_resolution,
                oebs_payment_status,
                payment_order_number,
                oebs_extra,
                updated_ts
            FROM cargo_payments.billing_tasks_history
            WHERE billing_doc_id = %s
            """,
            (billing_doc_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)

    return wrapper


async def test_happy_path(
        taxi_cargo_payments,
        approve_billing_tasks,
        register_billing_tasks,
        get_oebs_data,
):
    """
        Check oebs final status/meta stored.
    """
    response = await register_billing_tasks()
    approve_billing_tasks()

    response = await taxi_cargo_payments.post(
        'v1/billing/update-docs',
        json={
            'docs': [
                _make_doc(
                    billing_doc_id='1', billing_extra_key='some extra value',
                ),
                _make_doc(billing_doc_id='2'),
            ],
        },
    )
    assert response.status_code == 200

    # check fields stored
    oebs_data = get_oebs_data('1')
    assert oebs_data['oebs_payment_status'] == 'RECONCILED'
    assert oebs_data['payment_order_number'] == '1122'
    assert oebs_data['oebs_extra'] == {'billing_extra_key': 'some extra value'}
    assert oebs_data['oebs_sync_resolution'] == 'success'
    first_call_updated_ts = oebs_data['updated_ts']

    oebs_data = get_oebs_data('2')
    assert oebs_data['oebs_payment_status'] == 'RECONCILED'
    assert oebs_data['payment_order_number'] == '1122'
    assert oebs_data['oebs_extra'] == {}
    assert oebs_data['oebs_sync_resolution'] == 'success'

    # check not updated second time
    response = await taxi_cargo_payments.post(
        'v1/billing/update-docs',
        json={'docs': [_make_doc(billing_doc_id='1')]},
    )
    assert response.status_code == 200
    assert get_oebs_data('1')['updated_ts'] == first_call_updated_ts


async def test_intermediate_statuses(
        taxi_cargo_payments,
        approve_billing_tasks,
        register_billing_tasks,
        get_oebs_data,
        check_unprocessed_docs,
):
    """
        Check oebs updates with intermediate statuses:

            CONFIRMED - intermediate status, still polling oebs;
            RECONCILED - final status, stop polling oebs;
    """
    response = await register_billing_tasks()
    approve_billing_tasks()

    response = await taxi_cargo_payments.post(
        'v1/billing/update-docs',
        json={
            'docs': [
                _make_doc(
                    billing_doc_id='1',
                    payment_status='TRANSMITTED',
                    payment_order_number=None,
                ),
            ],
        },
    )
    assert response.status_code == 200

    # check update without payment_order_number
    oebs_data = get_oebs_data('1')
    assert oebs_data['oebs_payment_status'] == 'TRANSMITTED'
    assert oebs_data['payment_order_number'] is None
    assert oebs_data['oebs_sync_resolution'] is None

    response = await taxi_cargo_payments.post(
        'v1/billing/update-docs',
        json={
            'docs': [
                _make_doc(billing_doc_id='1', payment_status='CONFIRMED'),
                _make_doc(billing_doc_id='2'),
            ],
        },
    )
    assert response.status_code == 200

    # check billing_doc_id='1' keep polling
    await check_unprocessed_docs(expected=['1'])

    # check fields stored
    oebs_data = get_oebs_data('1')
    assert oebs_data['oebs_payment_status'] == 'CONFIRMED'
    assert oebs_data['payment_order_number'] == '1122'
    assert oebs_data['oebs_sync_resolution'] is None
    first_call_updated_ts = oebs_data['updated_ts']

    # check not updated second time
    response = await taxi_cargo_payments.post(
        'v1/billing/update-docs',
        json={
            'docs': [
                _make_doc(billing_doc_id='1', payment_status='CONFIRMED'),
            ],
        },
    )
    assert response.status_code == 200
    assert get_oebs_data('1')['updated_ts'] == first_call_updated_ts

    # check resolution after intermediate status
    response = await taxi_cargo_payments.post(
        'v1/billing/update-docs',
        json={
            'docs': [
                _make_doc(billing_doc_id='1', payment_status='RECONCILED'),
            ],
        },
    )
    assert response.status_code == 200
    oebs_data = get_oebs_data('1')
    assert oebs_data['oebs_payment_status'] == 'RECONCILED'
    assert oebs_data['payment_order_number'] == '1122'
    assert oebs_data['oebs_sync_resolution'] == 'success'

    # check billing_doc_id='1' finished polling
    await check_unprocessed_docs(expected=[])


async def test_invalid_status(
        taxi_cargo_payments,
        approve_billing_tasks,
        register_billing_tasks,
        get_oebs_data,
        check_unprocessed_docs,
):
    """
        Check oebs updates skiped without required info:
          - payment_status
          - payment_order_number
    """
    response = await register_billing_tasks()
    approve_billing_tasks()

    response = await taxi_cargo_payments.post(
        'v1/billing/update-docs',
        json={
            'docs': [
                _make_doc(billing_doc_id='1', payment_status=None),
                _make_doc(billing_doc_id='2'),
            ],
        },
    )
    assert response.status_code == 200

    # check billing_doc_id='1' keep polling
    await check_unprocessed_docs(expected=['1'])

    # check update is ignored
    oebs_data = get_oebs_data('1')
    assert oebs_data['oebs_payment_status'] is None
    assert oebs_data['payment_order_number'] is None
    assert oebs_data['oebs_sync_resolution'] is None


async def test_report_basic(
        taxi_cargo_payments,
        approve_billing_tasks,
        register_billing_tasks,
        get_billing_report,
):
    """
        Check oebs data in report.
    """
    response = await register_billing_tasks()
    approve_billing_tasks()

    response = await taxi_cargo_payments.post(
        'v1/billing/update-docs',
        json={'docs': [_make_doc(billing_doc_id='1')]},
    )
    assert response.status_code == 200

    report = await get_billing_report(payment_order_number='1122')
    assert len(report['transactions']) == 1
    doc = report['transactions'][0]
    assert doc['payment_order_number'] == '1122'
    assert doc['status'] == 'Платёж выверен с выпиской'
    assert doc['transaction_kind'] == 'payment'
