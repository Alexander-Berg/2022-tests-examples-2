from selfemployed.fns import client as client_fns


async def test_lavka_v1_send_register_income_msg_post(se_client, patch):
    @patch('selfemployed.fns.client.Client.register_income_raw')
    async def _register_income_raw(data):
        assert data.customer_inn == 'CustomerInn'
        return 'MessageId'

    result = await se_client.post(
        '/lavka/v1/send-register-income-msg',
        json={
            'Inn': 'Inn',
            'RequestTime': '2020-01-01T12:00:00+03',
            'OperationTime': '2020-01-01T11:00:00+03',
            'IncomeType': 'FROM_LEGAL_ENTITY',
            'CustomerInn': 'CustomerInn',
            'CustomerOrganization': 'CustomerOrganization',
            'Services': [
                {'Amount': '123', 'Name': 'Name1', 'Quantity': 1},
                {'Amount': '0.99', 'Name': 'Name2', 'Quantity': 1},
            ],
            'TotalAmount': '123.99',
            'GeoInfo': {'Latitude': 0.123, 'Longitude': 0.321},
            'OperationUniqueId': 'OperationUniqueId',
        },
    )

    assert result.status == 200
    assert await result.json() == {'MessageId': 'MessageId'}


async def test_lavka_v1_send_revert_income_msg_post(se_client, patch):
    @patch('selfemployed.fns.client.Client.revert_income_raw')
    async def _register_income_raw(data):
        assert data.receipt_id == 'ReceiptId'
        return 'MessageId'

    result = await se_client.post(
        '/lavka/v1/send-revert-income-msg',
        json={'Inn': 'Inn', 'ReceiptId': 'ReceiptId', 'ReasonCode': 'REFUND'},
    )

    assert result.status == 200
    assert await result.json() == {'MessageId': 'MessageId'}


async def test_lavka_v1_get_register_income_result_post_ok(se_client, patch):
    @patch('selfemployed.fns.client.Client.get_register_income_response')
    async def _get_response(msg_id):
        assert msg_id == 'MessageId'
        return 'ReceiptId', 'https://ReceiptLink'

    result = await se_client.post(
        '/lavka/v1/get-register-income-result',
        json={'MessageId': 'MessageId'},
    )

    assert result.status == 200
    assert await result.json() == {
        'ProcessingStatus': 'COMPLETED',
        'Message': {'ReceiptId': 'ReceiptId', 'Link': 'https://ReceiptLink'},
    }


async def test_lavka_v1_get_register_income_result_post_proc(se_client, patch):
    @patch('selfemployed.fns.client.Client.get_register_income_response')
    async def _get_response(msg_id):
        assert msg_id == 'MessageId'
        raise client_fns.ProcessingError()

    result = await se_client.post(
        '/lavka/v1/get-register-income-result',
        json={'MessageId': 'MessageId'},
    )

    assert result.status == 200
    assert await result.json() == {'ProcessingStatus': 'PROCESSING'}


async def test_lavka_v1_get_register_income_result_post_fail(se_client, patch):
    @patch('selfemployed.fns.client.Client.get_register_income_response')
    async def _get_response(msg_id):
        assert msg_id == 'MessageId'
        raise client_fns.SmzPlatformError(
            code='INTERNAL_ERROR',
            message='Too bad :-(',
            additional={'Key': 'Value'},
        )

    result = await se_client.post(
        '/lavka/v1/get-register-income-result',
        json={'MessageId': 'MessageId'},
    )

    assert result.status == 400
    assert await result.json() == {
        'Code': 'INTERNAL_ERROR',
        'Message': 'Too bad :-(',
        'Args': [{'Key': 'Key', 'Value': 'Value'}],
    }


async def test_lavka_v1_get_register_income_result_post_404(se_client, patch):
    @patch('selfemployed.fns.client.Client.get_register_income_response')
    async def _get_response(msg_id):
        assert msg_id == 'MessageId'
        raise client_fns.UnknownMessageFail(
            f'По переданному MessageId: {msg_id} сообщение не найдено',
        )

    result = await se_client.post(
        '/lavka/v1/get-register-income-result',
        json={'MessageId': 'MessageId'},
    )

    assert result.status == 404
    assert await result.json() == {
        'Code': 'MESSAGE_NOT_FOUND',
        'Message': 'По переданному MessageId: MessageId сообщение не найдено',
    }


async def test_lavka_v1_get_revert_income_result_post_ok(se_client, patch):
    @patch('selfemployed.fns.client.Client.get_revert_income_response')
    async def _get_response(msg_id):
        assert msg_id == 'MessageId'
        return 'DELETED'

    result = await se_client.post(
        '/lavka/v1/get-revert-income-result', json={'MessageId': 'MessageId'},
    )

    assert result.status == 200
    assert await result.json() == {
        'ProcessingStatus': 'COMPLETED',
        'Message': {'RequestResult': 'DELETED'},
    }


async def test_lavka_v1_get_revert_income_result_post_proc(se_client, patch):
    @patch('selfemployed.fns.client.Client.get_revert_income_response')
    async def _get_response(msg_id):
        assert msg_id == 'MessageId'
        raise client_fns.ProcessingError()

    result = await se_client.post(
        '/lavka/v1/get-revert-income-result', json={'MessageId': 'MessageId'},
    )

    assert result.status == 200
    assert await result.json() == {'ProcessingStatus': 'PROCESSING'}


async def test_lavka_v1_get_revert_income_result_post_fail(se_client, patch):
    @patch('selfemployed.fns.client.Client.get_revert_income_response')
    async def _get_response(msg_id):
        assert msg_id == 'MessageId'
        raise client_fns.SmzPlatformError(
            code='INTERNAL_ERROR',
            message='Too bad :-(',
            additional={'Key': 'Value'},
        )

    result = await se_client.post(
        '/lavka/v1/get-revert-income-result', json={'MessageId': 'MessageId'},
    )

    assert result.status == 400
    assert await result.json() == {
        'Code': 'INTERNAL_ERROR',
        'Message': 'Too bad :-(',
        'Args': [{'Key': 'Key', 'Value': 'Value'}],
    }


async def test_lavka_v1_get_revert_income_result_post_404(se_client, patch):
    @patch('selfemployed.fns.client.Client.get_revert_income_response')
    async def _get_response(msg_id):
        assert msg_id == 'MessageId'
        raise client_fns.UnknownMessageFail(
            f'По переданному MessageId: {msg_id} сообщение не найдено',
        )

    result = await se_client.post(
        '/lavka/v1/get-revert-income-result', json={'MessageId': 'MessageId'},
    )

    assert result.status == 404
    assert await result.json() == {
        'Code': 'MESSAGE_NOT_FOUND',
        'Message': 'По переданному MessageId: MessageId сообщение не найдено',
    }
