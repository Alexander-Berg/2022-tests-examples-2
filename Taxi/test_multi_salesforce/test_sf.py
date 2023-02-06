import pytest


@pytest.mark.usefixtures('salesforce')
async def test_create_multi_sf_singleton(
        library_context, mock_salesforce_auth,
):
    client1 = library_context.multi_sf.b2b
    client2 = library_context.multi_sf.taxi
    client3 = library_context.multi_sf.b2b
    client4 = library_context.multi_sf.taxi
    assert id(client1) != id(client2)
    assert id(client1) == id(client3)
    assert id(client2) == id(client4)


@pytest.mark.usefixtures('salesforce')
async def test_login_multi_sf(library_context, mock_salesforce_auth):
    client1 = library_context.multi_sf.b2b
    await client1.login()
    client3 = library_context.multi_sf.b2b
    assert client3._login == client1._login  # pylint: disable=W0212


@pytest.mark.usefixtures('salesforce')
async def test_get_user(library_context, mock_salesforce_auth):
    userb2b = await library_context.multi_sf.b2b.Account.get('123')
    usertaxi = await library_context.multi_sf.taxi.Accout.get('123')
    assert userb2b != usertaxi


@pytest.mark.usefixtures('salesforce')
async def test_create_sobject(library_context, mock_salesforce_auth):
    data_b2b = {
        'RecordTypeId': 'RecordTypeAccount',
        'AccountId': 'b2b',
        'Status': 'In Progress',
        'Origin': 'API',
        'IBAN__c': '1',
        'SWIFT__c': '1',
        'Subject': 'Self-Employed Change Payment Details',
    }
    data_taxi = {
        'RecordTypeId': 'RecordTypeAccount',
        'AccountId': 'taxi',
        'Status': 'In Progress',
        'Origin': 'API',
        'IBAN__c': '2',
        'SWIFT__c': '2',
        'Subject': 'Self-Employed Change Payment Details',
    }
    data_case_taxi = {
        'RecordTypeId': 'RecordTypeCase',
        'AccountId': 'taxi',
        'Status': 'In Progress',
        'Origin': 'API',
        'IBAN__c': '3',
        'SWIFT__c': '3',
        'Subject': 'Self-Employed Change Payment Details',
    }
    account_b2b = await library_context.multi_sf.b2b.Account.create(data_b2b)
    account_taxi = await library_context.multi_sf.taxi.Account.create(
        data_taxi,
    )
    case_taxi = await library_context.multi_sf.taxi.Case.create(data_case_taxi)
    assert account_b2b.body['AccountId'] == 'b2b'
    assert account_b2b.body['RecordTypeId'] == 'RecordTypeAccount'
    assert account_taxi.body['AccountId'] == 'taxi'
    assert account_taxi.body['RecordTypeId'] == 'RecordTypeAccount'
    assert case_taxi.body['AccountId'] == 'taxi'
    assert case_taxi.body['RecordTypeId'] == 'RecordTypeCase'


@pytest.mark.usefixtures('salesforce')
async def test_dont_remove_task_type(library_context, mock_salesforce_auth):
    sf = library_context.multi_sf.b2b  # pylint: disable=C0103
    async for i in sf.query_all_gen(query='SELECT * FROM table'):
        print(i)
