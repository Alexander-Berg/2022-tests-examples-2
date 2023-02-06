async def test_simple(
        taxi_persey_payments_web,
        mockserver,
        pgsql,
        load,
        trust_create_partner_success,
        trust_create_product_success,
        mock_balance,
):
    partner_mock = trust_create_partner_success('create_partner_simple.json')
    product_mock = trust_create_product_success('create_product_simple.json')
    method_response = {
        'Balance2.FindClient': 'find_client_simple.xml',
        'Balance2.GetClientPersons': 'get_client_persons_simple.xml',
        'Balance2.CreatePerson': 'create_person_simple.xml',
        'Balance2.CreateCommonContract': 'create_common_contract_simple.xml',
        'Balance2.GetClientContracts': 'get_client_contracts_simple.xml',
    }
    balance_mock = mock_balance(method_response)

    response = await taxi_persey_payments_web.post(
        '/v1/lab/create',
        json={
            'lab_id': 'some_lab',
            'client_person': {'bik': '777', 'account': '123'},
            'contract_start_dt': '2017-05-30',
            'partner_uid': 'some_partner_uid',
            'partner_commission': '1.23',
        },
    )

    assert response.status == 200
    assert await response.json() == {'contract_id': 'some_contract'}

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(
        'SELECT lab_id, partner_uid, operator_uid, '
        'trust_product_id_delivery, trust_product_id_test, '
        'trust_partner_id, balance_client_id, balance_client_person_id, '
        'balance_contract_id, status FROM persey_payments.lab',
    )
    labs = [row for row in cursor]
    assert labs == [
        (
            'some_lab',
            'some_partner_uid',
            'nonexistent',
            'some_lab_delivery',
            'some_lab_test',
            'some_partner_id',
            '1231434',
            'some_person',
            'some_contract',
            'ready',
        ),
    ], labs
    assert partner_mock.times_called == 1
    assert product_mock.times_called == 2
    assert balance_mock.times_called == 5

    response = await taxi_persey_payments_web.post(
        '/v1/lab/create',
        json={
            'lab_id': 'some_lab',
            'client_person': {'bik': '777', 'account': '123'},
            'contract_start_dt': '2017-05-30',
            'partner_uid': 'some_partner_uid',
            'partner_commission': '1.23',
        },
    )

    assert response.status == 200
    assert await response.json() == {'contract_id': 'some_contract'}

    assert partner_mock.times_called == 1
    assert product_mock.times_called == 2
    assert balance_mock.times_called == 5


async def test_contract_already_created(
        taxi_persey_payments_web,
        mockserver,
        pgsql,
        load,
        trust_create_partner_success,
        trust_create_product_success,
        mock_balance,
):
    partner_mock = trust_create_partner_success('create_partner_simple.json')
    product_mock = trust_create_product_success('create_product_simple.json')
    method_response = {
        'Balance2.FindClient': 'find_client_simple.xml',
        'Balance2.GetClientPersons': 'get_client_persons_simple.xml',
        'Balance2.CreatePerson': 'create_person_simple.xml',
        'Balance2.GetClientContracts': (
            'get_client_contracts_already_created.xml'
        ),
    }
    balance_mock = mock_balance(method_response)

    response = await taxi_persey_payments_web.post(
        '/v1/lab/create',
        json={
            'lab_id': 'some_lab',
            'client_person': {'bik': '777', 'account': '123'},
            'contract_start_dt': '2017-05-30',
            'partner_uid': 'some_partner_uid',
            'partner_commission': '3.21',
        },
    )

    assert response.status == 200
    assert await response.json() == {'contract_id': '4564563'}

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT lab_id FROM persey_payments.lab')
    labs = [row[0] for row in cursor]
    assert labs == ['some_lab']
    assert partner_mock.times_called == 1
    assert product_mock.times_called == 2
    assert balance_mock.times_called == 4


async def test_partner_already_created(
        taxi_persey_payments_web,
        mockserver,
        pgsql,
        load,
        trust_create_product_success,
        mock_balance,
):
    @mockserver.json_handler('/trust-payments/v2/partners/')
    def partner_mock(request):
        return {
            'status': 'error',
            'status_code': 'invalid_request',
            'status_desc': (
                'Passport greenriver-ru (176428396) is '
                'already linked to OTHER client 2237685, balance_4008'
            ),
        }

    product_mock = trust_create_product_success(
        'create_product_partner_created.json',
    )
    method_response = {
        'Balance2.FindClient': 'find_client_simple.xml',
        'Balance2.GetClientPersons': 'get_client_persons_simple.xml',
        'Balance2.CreatePerson': 'create_person_simple.xml',
        'Balance2.GetClientContracts': (
            'get_client_contracts_already_created.xml'
        ),
    }
    balance_mock = mock_balance(method_response)

    response = await taxi_persey_payments_web.post(
        '/v1/lab/create',
        json={
            'lab_id': 'some_lab',
            'client_person': {'bik': '777', 'account': '123'},
            'contract_start_dt': '2017-05-30',
            'partner_uid': 'some_partner_uid',
            'partner_commission': '3.21',
        },
    )

    assert response.status == 200
    assert await response.json() == {'contract_id': '4564563'}

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute('SELECT lab_id FROM persey_payments.lab')
    labs = [row[0] for row in cursor]
    assert labs == ['some_lab']
    assert partner_mock.times_called == 1
    assert product_mock.times_called == 2
    assert balance_mock.times_called == 4
