async def test_strizh_create(taxi_logistic_platform_operator_emulator):
    response = await taxi_logistic_platform_operator_emulator.post(
        '/services/v2/sinc.asmx',
        headers={'Content-Type': 'text/xml'},
        data="""
        <?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                          xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                          xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <RegisterOrderExtended xmlns="http://tempuri.org/">
                    <Auth>
                        <Login>12345678</Login>
                        <Password>12345</Password>
                    </Auth>
                </RegisterOrderExtended>
            </soapenv:Body>
        </soapenv:Envelope>
        """,
    )

    assert response.status_code == 200


async def test_strizh_cancel(taxi_logistic_platform_operator_emulator):
    response = await taxi_logistic_platform_operator_emulator.post(
        '/services/v2/sinc.asmx',
        headers={'Content-Type': 'text/xml'},
        data="""
        <?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                          xmlns:xsd="http://www.w3.org/2001/XMLSchema"
                          xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
            <soapenv:Body>
                <RefuseOrder xmlns="http://tempuri.org/">
                    <Auth>
                        <Login>12345678</Login>
                        <Password>12345</Password>
                    </Auth>
                    <orderID>
                        123
                    </orderID>
                </RefuseOrder>
            </soapenv:Body>
        </soapenv:Envelope>
        """,
    )

    assert response.status_code == 200
