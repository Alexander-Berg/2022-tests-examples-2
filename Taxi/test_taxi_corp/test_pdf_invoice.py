# pylint: disable=redefined-outer-name


async def test_invoice_pdf(taxi_corp_auth_client, mockserver):
    report_body = b'%PDF-1.4%%EOF'
    content_disposition = 'attachment; filename="ЛС-1.pdf"'
    content_type = 'application/pdf'

    @mockserver.json_handler('/corp-clients/v1/invoice')
    def _v1_invoice(request):
        return mockserver.make_response(
            report_body,
            content_type=content_type,
            headers={'Content-Disposition': content_disposition},
        )

    client_id = 'client1'

    query = {'contract_id': 101, 'value': '1000'}

    response = await taxi_corp_auth_client.get(
        '/1.0/client/{}/invoice_pdf'.format(client_id), params=query,
    )

    assert response.status == 200
    assert (await response.read()) == report_body
    assert response.headers['Content-Disposition'] == content_disposition
    assert response.headers['Content-Type'] == content_type
