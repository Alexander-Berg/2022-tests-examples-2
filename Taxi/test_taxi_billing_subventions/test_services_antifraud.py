import dataclasses
import datetime
import decimal
from unittest import mock

import aiohttp
import pytest
import pytz

from taxi import billing
from taxi import clients
from taxi import discovery

from taxi_billing_subventions.common import models as common_models
from taxi_billing_subventions.services import antifraud as afs
from taxi_billing_subventions.single_ride import models


async def test_antifraud_service_check_order_allowed_af_request(
        service, mock_uantifraud, order, load_json,
):
    uantifraud = mock_uantifraud({'status': 'allow'})
    await _check_is_allowed(service, order)
    assert uantifraud.times_called == 1
    expected = load_json('uantifraud_request.json')
    assert uantifraud.next_call()['request'].json == expected


@pytest.mark.parametrize(
    'raw_response,expected',
    (({'status': 'allow'}, True), ({'status': 'block'}, False)),
)
async def test_antifraud_service_check_order_allowed_af_response(
        service, mock_uantifraud, order, raw_response, expected,
):
    mock_uantifraud(raw_response)
    response = await _check_is_allowed(service, order)
    assert response is expected


async def _check_is_allowed(service, order):
    return await service.is_order_allowed_for_subvention(
        order=order, rule_type='single_ride',
    )


async def test_antifraud_service_check_order_subvention_af_request(
        service, zone, mock_antifraud, order, load_json,
):
    antifraud = mock_antifraud(load_json('antifraud_pay.json'))
    await _check_order_subvention(service, zone, order)
    assert antifraud.times_called == 1
    expected = load_json('antifraud_request.json')
    assert antifraud.next_call()['request'].json == expected


@pytest.mark.parametrize(
    'af_response,expected',
    (
        (
            'antifraud_pay.json',
            common_models.doc.AntifraudResponse(
                antifraud_id='afc0de',
                billing_id='doc_id/1212',
                action=common_models.doc.AntifraudAction.PAY,
                till=None,
                reason=None,
            ),
        ),
        (
            'antifraud_block.json',
            common_models.doc.AntifraudResponse(
                antifraud_id='afc0de',
                billing_id='doc_id/1212',
                action=common_models.doc.AntifraudAction.BLOCK,
                till=None,
                reason={'message': 'Fraud detected'},
            ),
        ),
        (
            'antifraud_delay.json',
            common_models.doc.AntifraudResponse(
                antifraud_id='afc0de',
                billing_id='doc_id/1212',
                action=common_models.doc.AntifraudAction.DELAY,
                till=datetime.datetime.fromisoformat(
                    '2020-09-10T01:30:00+00:00',
                ),
                reason=None,
            ),
        ),
    ),
)
async def test_antifraud_service_check_order_subvention_af_response(
        service, mock_antifraud, load_json, zone, order, af_response, expected,
):
    mock_antifraud(load_json(af_response))
    response = await _check_order_subvention(service, zone, order)
    assert dataclasses.asdict(response) == dataclasses.asdict(expected)


async def _check_order_subvention(service, zone, order):
    return await service.check_order_subvention(
        billing_id='doc_id/1212',
        order=models.Order(
            id=order.id,
            alias_id=order.alias_id,
            due=order.due,
            billing_at=order.billing_at,
            billing_client_id='<billing_client_id>',
            tariff_class=order.tariff.class_,
            agglomeration=None,
            tariff_zone=order.zone_name,
            payment_type=order.payment_type,
            invoice_date=order.completed_at,
            is_netting=False,
        ),
        driver=models.Driver(
            db_id=order.performer.db_id,
            license=order.performer.driver_license,
            uuid=order.performer.uuid,
        ),
        subvention=billing.Money(
            amount=decimal.Decimal('122.0846'), currency='RUB',
        ),
        zone=zone,
    )


@pytest.fixture(name='service')
def make_service(session):
    tvm_client = clients.tvm.TVMClient(
        service_name='test_taxi_billing_subventions',
        secdist={},
        config=mock.Mock(TVM_RULES={}),
        session=session,
    )
    uantifraud = clients.uantifraud.UAntiFraudClient(
        session=session,
        cfg=mock.Mock(
            UANTIFRAUD_CLIENT_QOS={
                '__default__': {'attempts': 1, 'timeout-ms': 10000},
            },
        ),
        tvm_client=tvm_client,
    )
    antifraud = clients.antifraud.AntifraudClient(
        service=discovery.find_service('antifraud'),
        session=session,
        tvm_client=tvm_client,
    )
    return afs.AntifraudService(
        uantifraud_client=uantifraud, antifraud_client=antifraud,
    )


@pytest.fixture(name='session')
async def make_session():
    session = aiohttp.client.ClientSession()
    yield session
    await session.close()


@pytest.fixture(name='zone')
def make_zone():
    return common_models.Zone(
        name='moscow',
        city_id='Москва',
        tzinfo=pytz.timezone('Europe/Moscow'),
        currency='RUB',
        locale='ru',
        vat=common_models.Vat.make_naive(12000),
        country='RU',
    )


@pytest.fixture(name='order')
def make_order(load_py_json):
    return load_py_json('order.json')
