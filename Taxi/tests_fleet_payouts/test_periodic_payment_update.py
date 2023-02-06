import contextlib

import pytest

from tests_fleet_payouts.utils import pg
from tests_fleet_payouts.utils import xcmp


def next_request(mock):
    request = mock.next_call()['request'].json
    with contextlib.suppress(TypeError, KeyError, AttributeError):
        request['doc_ids'].sort()
    return request


@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
async def test_queue(
        taxi_fleet_payouts, mock_docs_by_id, mock_docs_select, pgsql,
):
    # Step 1

    initial_payments = pg.dump_payments(pgsql)
    initial_payment_entries = pg.dump_payment_entries(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-update')

    assert mock_docs_by_id.times_called == 1
    assert next_request(mock_docs_by_id) == {
        'doc_ids': [4871000000, 4872000000],
    }

    assert mock_docs_select.times_called == 1
    assert next_request(mock_docs_select) == {
        'external_obj_id': 'taxi/payment_order/clid/CLID01/76000000',
        'begin_time': xcmp.Date('2020-03-21T15:00:00+03:00'),
        'end_time': xcmp.Date('2020-03-21T21:00:00+03:00'),
        'limit': 3,
    }

    updated_payments = pg.dump_payments(pgsql)
    updated_payment_entries = pg.dump_payment_entries(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT01': {
            **initial_payments['PAYMENT01'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'status': 'completed',
        },
        'PAYMENT02': {
            **initial_payments['PAYMENT02'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
        },
    }
    assert updated_payment_entries == {
        **initial_payment_entries,
        ('PAYMENT01', '810000'): {
            **initial_payment_entries[('PAYMENT01', '810000')],
            'status_code': 'DONE',
            'status_message': None,
            'reject_code': None,
            'reject_message': None,
        },
        ('PAYMENT01', '810001'): {
            **initial_payment_entries[('PAYMENT01', '810001')],
            'status_code': 'OLD',
            'status_message': 'Сообщение',
            'reject_code': None,
            'reject_message': None,
        },
        ('PAYMENT01', '810002'): {
            **initial_payment_entries[('PAYMENT01', '810002')],
            'status_code': 'REJECT',
            'status_message': None,
            'reject_code': 'E_PAY_REQUEST_NOT_ALLOWED',
            'reject_message': 'По договору не разрешен вывод по кнопке',
        },
    }

    # Step 2

    initial_payments = updated_payments
    initial_payment_entries = updated_payment_entries

    await taxi_fleet_payouts.run_task('periodic-payment-update')

    assert mock_docs_by_id.times_called == 1
    assert next_request(mock_docs_by_id) == {
        'doc_ids': [4870000000, 4873000000],
    }

    assert mock_docs_select.times_called == 1
    assert next_request(mock_docs_select) == {
        'external_obj_id': 'taxi/payment_order/clid/CLID03/76000000',
        'begin_time': xcmp.Date('2020-03-21T15:00:00+03:00'),
        'end_time': xcmp.Date('2020-03-21T21:00:00+03:00'),
        'limit': 1,
    }

    updated_payments = pg.dump_payments(pgsql)
    updated_payment_entries = pg.dump_payment_entries(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT00': {
            **initial_payments['PAYMENT00'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
        },
        'PAYMENT03': {
            **initial_payments['PAYMENT03'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'status': 'completed',
        },
    }
    assert updated_payment_entries == {
        **initial_payment_entries,
        ('PAYMENT03', '830000'): {
            **initial_payment_entries[('PAYMENT03', '830000')],
            'status_code': 'DONE',
            'status_message': None,
            'reject_code': None,
            'reject_message': None,
        },
    }

    # Step 3

    initial_payments = updated_payments
    initial_payment_entries = updated_payment_entries
    initial_payment_timers = pg.dump_payment_timers(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-update')

    assert mock_docs_by_id.times_called == 1
    assert next_request(mock_docs_by_id) == {'doc_ids': [4874000000]}

    assert mock_docs_select.times_called == 1
    assert next_request(mock_docs_select) == {
        'external_obj_id': 'taxi/payment_order/clid/CLID06/76000000',
        'begin_time': xcmp.Date('2020-03-21T15:00:00+03:00'),
        'end_time': xcmp.Date('2020-03-21T21:00:00+03:00'),
        'limit': 1,
    }

    updated_payments = pg.dump_payments(pgsql)
    updated_payment_entries = pg.dump_payment_entries(pgsql)
    updated_payment_timers = pg.dump_payment_timers(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT06': {
            **initial_payments['PAYMENT06'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'status': 'completed',
        },
    }
    assert updated_payment_entries == {
        **initial_payment_entries,
        ('PAYMENT06', '840000'): {
            **initial_payment_entries[('PAYMENT06', '840000')],
            'status_code': 'REJECTED',
            'status_message': None,
            'reject_code': 'N_PAYMENT_PENDED',
            'reject_message': 'День выплаты не наступил',
        },
    }
    assert updated_payment_timers == {
        **initial_payment_timers,
        'CLID06': {
            **initial_payment_timers['CLID06'],
            'expires_at': xcmp.Date('2020-03-22T02:00:00+03:00'),
        },
    }

    # Step 4

    initial_payments = updated_payments
    initial_payment_entries = updated_payment_entries

    await taxi_fleet_payouts.run_task('periodic-payment-update')

    assert mock_docs_by_id.times_called == 0
    assert mock_docs_select.times_called == 0

    updated_payments = pg.dump_payments(pgsql)
    updated_payment_entries = pg.dump_payment_entries(pgsql)

    assert initial_payments == updated_payments
    assert initial_payment_entries == updated_payment_entries


@pytest.mark.now('2020-03-21T18:15:00+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
async def test_age_condition(
        taxi_fleet_payouts, mock_docs_by_id, mock_docs_select, pgsql,
):
    initial_payments = pg.dump_payments(pgsql)
    initial_payment_entries = pg.dump_payment_entries(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-update')

    assert mock_docs_by_id.times_called == 1
    assert next_request(mock_docs_by_id) == {'doc_ids': [4872000000]}
    assert mock_docs_select.times_called == 0

    updated_payments = pg.dump_payments(pgsql)
    updated_payment_entries = pg.dump_payment_entries(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT02': {
            **initial_payments['PAYMENT02'],
            'updated_at': xcmp.Date('2020-03-21T18:15:00+03:00'),
        },
    }
    assert updated_payment_entries == initial_payment_entries


@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
async def test_skip_on_error_1st(
        taxi_fleet_payouts, mock_docs_select, mockserver, pgsql,
):
    @mockserver.json_handler('/billing-reports/v1/docs/by_id')
    def mock_docs_by_id(request):
        return mockserver.make_response(status=500)

    initial_payments = pg.dump_payments(pgsql)
    initial_payment_entries = pg.dump_payment_entries(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-update')

    assert mock_docs_by_id.times_called >= 2
    while mock_docs_by_id.times_called > 0:
        assert next_request(mock_docs_by_id) == {
            'doc_ids': [4871000000, 4872000000],
        }

    updated_payments = pg.dump_payments(pgsql)
    updated_payment_entries = pg.dump_payment_entries(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT01': {
            **initial_payments['PAYMENT01'],
            # now - min_age = 20:30
            'updated_at': xcmp.Date('2020-03-21T20:30:00+03:00'),
        },
        'PAYMENT02': {
            **initial_payments['PAYMENT02'],
            # now - min_age = 20:30
            'updated_at': xcmp.Date('2020-03-21T20:30:00+03:00'),
        },
    }
    assert updated_payment_entries == initial_payment_entries


@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
async def test_skip_on_error_2nd(
        taxi_fleet_payouts, mock_docs_by_id, mockserver, pgsql,
):
    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def mock_docs_select(request):
        return mockserver.make_response(status=500)

    initial_payments = pg.dump_payments(pgsql)
    initial_payment_entries = pg.dump_payment_entries(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-update')

    assert mock_docs_by_id.times_called == 1
    assert next_request(mock_docs_by_id) == {
        'doc_ids': [4871000000, 4872000000],
    }

    assert mock_docs_select.times_called >= 2
    while mock_docs_select.times_called > 0:
        assert next_request(mock_docs_select) == {
            'external_obj_id': 'taxi/payment_order/clid/CLID01/76000000',
            'begin_time': xcmp.Date('2020-03-21T15:00:00+03:00'),
            'end_time': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'limit': 3,
        }

    updated_payments = pg.dump_payments(pgsql)
    updated_payment_entries = pg.dump_payment_entries(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT01': {
            **initial_payments['PAYMENT01'],
            # now - min_age = 20:30
            'updated_at': xcmp.Date('2020-03-21T20:30:00+03:00'),
        },
        'PAYMENT02': {
            **initial_payments['PAYMENT02'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
        },
    }
    assert updated_payment_entries == initial_payment_entries
