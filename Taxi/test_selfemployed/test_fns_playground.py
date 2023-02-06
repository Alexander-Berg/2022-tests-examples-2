# type: ignore
# pylint: skip-file

""" Playground for ФНС/ЦРПТ SOAP calls

Integration playground, these tests should NOT be run on regular basis.
"""

import asyncio
import datetime as dt

import pytest
import pytz

import selfemployed.fns.client as fns
import selfemployed.helpers.fns as fns_helpers

# Don't forget to start ssh tunnel
# ssh -N $PROD_SELFEMPLOYED_HOST -L 8080:localhost:8080

MASTER_TOKEN = (
    '4WKOCoOLArPnF1ijCkQBH6CKNWeO2cfBvZlWJqNCpnuopMD0ISGSefPGILAQ'
    'I2n4rntacA3X1oc1QCHuYOG0zx6M0wGE7x9saHMJdBIJnUyL4ePu7pvK4UBq'
    '0OMpuvSD'
)


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['selfemployed_fns'] = {'FNS_MASTER_TOKEN': MASTER_TOKEN}
    return simple_secdist


@pytest.mark.skip
@pytest.mark.not_mock_request()
async def test_client_init(web_context):
    fns_client: fns.Client = web_context.client_fns
    assert fns_client


@pytest.mark.skip
@pytest.mark.not_mock_request()
async def test_register_partner(web_context):
    fns_client: fns.Client = web_context.client_fns
    f = open('selfemployed/test_selfemployed/resources/icon_fns.jpg', 'rb')
    jpg_base64 = f.read(50 * 1024)

    msg_id = await fns_client.reg_partner(
        'Яндекс.Такси',
        '7704340310',
        '+7 (495) 739-70-00',
        self_reg=True,
        jpg_base64=jpg_base64,
    )

    result_msg = await fns_client.get_response_retry(msg_id)
    result = fns_client.parse_partner_status(result_msg)

    partner_id, reg_date = result

    assert partner_id
    assert reg_date


@pytest.mark.skip
@pytest.mark.not_mock_request()
async def test_get_response_bad_msg_id(web_context):
    fns_client: fns.Client = web_context.client_fns
    with pytest.raises(fns.UnknownMessageFail):
        await fns_client.get_response('007')


@pytest.mark.skip
@pytest.mark.not_mock_request()
async def test_bind_with_phone(web_context):
    fns_client: fns.Client = web_context.client_fns
    msg_id = await fns_client.bind_by_phone(
        '+70002711664', [fns.Permission.PAYMENT_INFORMATION],
    )

    assert msg_id


@pytest.mark.skip
@pytest.mark.not_mock_request()
async def test_happy_path(web_context):
    fns_client: fns.Client = web_context.client_fns
    # Lets bind a new selfemployed by phone number...
    msg_id = await fns_client.bind_by_phone(
        '70002711664', fns_helpers.PERMISSIONS,
    )

    try:
        # ...and wait for response
        bind_msg = await fns_client.get_response_retry(msg_id)
    except fns.TaxpayerAlreadyBoundError as exc:
        # And if it's already done - just unbind him...
        unbind_msg_id = await fns_client.unbind(exc.inn)
        _ = await fns_client.get_response_retry(unbind_msg_id)
        # ... and bind again
        msg_id = await fns_client.bind_by_phone(
            '70002711664', fns_helpers.PERMISSIONS,
        )
        bind_msg = await fns_client.get_response_retry(msg_id)

    # Error check
    # code = msg.xpath('//smz:Code', namespaces=SMZ_NS_MAP)[0]
    # message = msg.xpath('//smz:Message', namespaces=SMZ_NS_MAP)[0]
    # print(code)
    # print(code.text)
    # print(message)
    # print(message.text)
    # print(msg)

    request_id = fns_client.parse_bind(bind_msg)

    # Wait until user accept request
    # WARINIG: IT ACTUALLY WAIT FOR YOUR ACTION IN APP OR TAX PAYER CABINET
    status = ''
    inn = ''
    while status != 'COMPLETED':
        msg_id1 = await fns_client.check_bind_status(request_id)
        bind_msg = await fns_client.get_response_retry(msg_id1)
        status, inn = fns_client.parse_bind_status(bind_msg)
        await asyncio.sleep(1)

    now_date = dt.datetime.utcnow()

    # Now let's register a new income #1
    reg_id = await fns_client.register_income(
        inn, 'Перевозка пассажиров и багажа', 510, now_date, now_date,
    )
    income_msg = await fns_client.get_response_retry(reg_id)
    receipt_id, link = fns_client.parse_income(income_msg)

    assert receipt_id
    assert link

    # And new income #2 with same props
    reg_id = await fns_client.register_income(
        inn, 'Перевозка пассажиров и багажа', 510, now_date, now_date,
    )

    try:
        await fns_client.get_response_retry(reg_id)
    except fns.DuplicateReceiptPlatformError as exc:
        receipt_id = exc.receipt_id
        link = exc.receipt_url
        assert receipt_id
        assert link

    # # And a commercial one
    # comm_reg_id = await fns_client.register_income(
    #     inn, 'Перевозка пассажиров и багажа', 250,
    #     dt.datetime.utcnow(), dt.datetime.utcnow(),
    #     customer_inn='7704340310')
    #
    # income_msg = await fns_client.get_response_retry(comm_reg_id)
    # comm_receipt_id, comm_link = fns_client.parse_income(income_msg)
    #
    # assert comm_receipt_id
    # assert comm_link

    # And finally revert first receipt...
    # msg_id = await fns_client.revert_income(inn, receipt_id)
    # revert_msg = await fns_client.get_response_retry(msg_id)
    #
    # revert_result = fns_client.parse_revert(revert_msg)
    #
    # assert revert_result == 'DELETED'


@pytest.mark.skip
@pytest.mark.not_mock_request()
async def test_get_income(web_context):
    fns_client: fns.Client = web_context.client_fns
    inn = '212910455904'
    from_date = dt.datetime(2019, 1, 1, tzinfo=pytz.utc)
    to_date = dt.datetime(2019, 2, 1, tzinfo=pytz.utc)

    all_receipts = await fns_helpers.fetch_all_receipts(
        fns_client, inn, from_date, to_date, 1000, 10,
    )

    assert all_receipts


@pytest.mark.skip
@pytest.mark.not_mock_request()
async def test_get_details(web_context):
    fns_client: fns.Client = web_context.client_fns
    msg_id = await fns_client.get_details('771977706439')
    bind_msg = await fns_client.get_response_retry(msg_id)
    first, last, middle = fns_client.parse_details(bind_msg)

    assert first
    assert last
    assert middle
