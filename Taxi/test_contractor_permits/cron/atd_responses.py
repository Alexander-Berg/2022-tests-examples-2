# flake8: noqa
# pylint: skip-file

AUTHORIZATION = {
    'SUCCESS': """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><AuthorizationResponse xmlns="https://srvepak.atd.lv:9473/"><AuthorizationResult>valid_session_key</AuthorizationResult></AuthorizationResponse></soap:Body></soap:Envelope>""",
    'FAILED': """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Header><Error xmlns="https://srvepak.atd.lv:9473/"><Type>Error</Type><Message>Login or password is incorrect.</Message></Error></soap:Header><soap:Body><AuthorizationResponse xmlns="https://srvepak.atd.lv:9473/"><AuthorizationResult /></AuthorizationResponse></soap:Body></soap:Envelope>""",
}

VALID_TAXI_DRIVING_LICENSE = {
    'OK': """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Body>
                <ValidTaxiDrivingLicensesResponse xmlns="https://srvepak.atd.lv:9473/">
                    <ValidTaxiDrivingLicensesResult>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-1">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2019-10-04T00:00:00</StartDate>
                                <EndDate>2022-10-03T00:00:00</EndDate>
                                <Status>Reģistrēts</Status>
                                <StatusChangeDate>2019-10-04T00:00:00</StatusChangeDate>
                                <DrivingLicenseNumber>LICENSE</DrivingLicenseNumber>
                            </TaxiDrivingLicense>
                        </DocumentList>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-2">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2018-10-22T00:00:00</StartDate>
                                <EndDate>2021-10-21T00:00:00</EndDate>
                                <Status>Izslēgts</Status>
                                <StatusChangeDate>2020-10-23T00:00:00</StatusChangeDate>
                            </TaxiDrivingLicense>
                        </DocumentList>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-3">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2019-10-04T00:00:00</StartDate>
                                <EndDate>2022-10-03T00:00:00</EndDate>
                                <Status>Reģistrēts</Status>
                                <StatusChangeDate>2019-10-04T00:00:00</StatusChangeDate>
                                <DrivingLicenseNumber>LICENSE</DrivingLicenseNumber>
                            </TaxiDrivingLicense>
                        </DocumentList>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-5">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2019-10-04T00:00:00</StartDate>
                                <EndDate>2022-10-03T00:00:00</EndDate>
                                <Status>Reģistrēts</Status>
                                <StatusChangeDate>2019-10-04T00:00:00</StatusChangeDate>
                                <DrivingLicenseNumber>MISMATCHED_LICENSE</DrivingLicenseNumber>
                            </TaxiDrivingLicense>
                        </DocumentList>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-6">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2019-10-04T00:00:00</StartDate>
                                <EndDate>2022-10-03T00:00:00</EndDate>
                                <Status>Reģistrēts</Status>
                                <StatusChangeDate>2019-10-04T00:00:00</StatusChangeDate>
                                <DrivingLicenseNumber>LICENSE</DrivingLicenseNumber>
                            </TaxiDrivingLicense>
                        </DocumentList>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-7">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2019-10-04T00:00:00</StartDate>
                                <EndDate>2022-10-03T00:00:00</EndDate>
                                <Status>Reģistrēts</Status>
                                <StatusChangeDate>2019-10-04T00:00:00</StatusChangeDate>
                                <DrivingLicenseNumber>MISMATCHED_LICENSE</DrivingLicenseNumber>
                            </TaxiDrivingLicense>
                        </DocumentList>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-8">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2019-10-04T00:00:00</StartDate>
                                <EndDate>2022-10-03T00:00:00</EndDate>
                                <Status>Reģistrēts</Status>
                                <StatusChangeDate>2019-10-04T00:00:00</StatusChangeDate>
                                <DrivingLicenseNumber>LICENSE</DrivingLicenseNumber>
                            </TaxiDrivingLicense>
                        </DocumentList>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-9">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2019-10-04T00:00:00</StartDate>
                                <EndDate>2022-10-03T00:00:00</EndDate>
                                <Status>Reģistrēts</Status>
                                <StatusChangeDate>2019-10-04T00:00:00</StatusChangeDate>
                                <DrivingLicenseNumber>LICENSE</DrivingLicenseNumber>
                            </TaxiDrivingLicense>
                        </DocumentList>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-10">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2019-10-04T00:00:00</StartDate>
                                <EndDate>2022-10-03T00:00:00</EndDate>
                                <Status>Reģistrēts</Status>
                                <StatusChangeDate>2019-10-04T00:00:00</StatusChangeDate>
                                <DrivingLicenseNumber>LICENSE</DrivingLicenseNumber>
                            </TaxiDrivingLicense>
                        </DocumentList>
                        <DocumentList DriverName="VJAČESLAVS JEMEĻJANOVS">
                            <TaxiDrivingLicense Number="TV-11">
                                <Type ID="TX" Name="Taksometru vadītāju reģistrācija" />
                                <DriverName>VJAČESLAVS JEMEĻJANOVS</DriverName>
                                <StartDate>2019-10-04T00:00:00</StartDate>
                                <EndDate>2022-10-03T00:00:00</EndDate>
                                <Status>Reģistrēts</Status>
                                <StatusChangeDate>2019-10-04T00:00:00</StatusChangeDate>
                                <DrivingLicenseNumber>LICENSE</DrivingLicenseNumber>
                            </TaxiDrivingLicense>
                        </DocumentList>
                    </ValidTaxiDrivingLicensesResult>
                </ValidTaxiDrivingLicensesResponse>
            </soap:Body>
        </soap:Envelope>
    """,
    'WRONG_TOKEN': """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Header>
                <Error xmlns="https://srvepak.atd.lv:9473/">
                    <Type>Error</Type>
                    <Message>Not set token.</Message>
                </Error>
            </soap:Header>
            <soap:Body>
                <ValidTaxiDrivingLicenseResponse xmlns="https://srvepak.atd.lv:9473/" />
            </soap:Body>
        </soap:Envelope>
    """,
    'EXPIRED_TOKEN': """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Body>
                <soap:Fault>
                    <faultcode>soap:Server</faultcode>
                    <faultstring>Server was unable to process request. ---&gt; [u]The token is expired</faultstring>
                    <detail />
                </soap:Fault>
            </soap:Body>
        </soap:Envelope>
    """,
    'REJECT_ALL': """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Body>
                <ValidTaxiDrivingLicenseResponse xmlns="https://srvepak.atd.lv:9473/"/>
            </soap:Body>
        </soap:Envelope>
    """,
}

VALID_VEHICLE_DOCUMENT = {
    'OK': """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Body>
                <ValidVehicleDocumentResponse xmlns="https://srvepak.atd.lv:9473/">
                    <ValidVehicleDocumentResult CompanyRegistrationNumber="43603083565" CompanyName="SIA &quot;Relax CAR&quot;">
                        <Documents>
                            <Document Number="NT-522022" IsActive="true">
                                <Type ID="LK" Name="Licences kartīte" />
                                <Code ID="NT" Name="Pasažieru komercpārvadājumiem ar vieglajiem automobiļiem" />
                                <StartDate>2021-01-01T00:00:00</StartDate>
                                <ExpireDate>2021-01-31T00:00:00</ExpireDate>
                                <SuspendedDate xsi:nil="true" />
                                <ExtendedDocument>
                                    <Number>NT-523750</Number>
                                    <ExpireDate>2021-02-28T00:00:00</ExpireDate>
                                </ExtendedDocument>
                                <VehicleNumber>LB3001</VehicleNumber>
                            </Document>
                        </Documents>
                    </ValidVehicleDocumentResult>
                </ValidVehicleDocumentResponse>
            </soap:Body>
        </soap:Envelope>
    """,
    'WRONG_TOKEN': """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Header>
                <Error xmlns="https://srvepak.atd.lv:9473/">
                    <Type>Error</Type>
                    <Message>Not set token.</Message>
                </Error>
            </soap:Header>
            <soap:Body>
                <ValidVehicleDocumentResponse xmlns="https://srvepak.atd.lv:9473/" />
            </soap:Body>
        </soap:Envelope>
    """,
    'EXPIRED_TOKEN': """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Body>
                <soap:Fault>
                    <faultcode>soap:Server</faultcode>
                    <faultstring>Server was unable to process request. ---&gt; [u]The token is expired</faultstring>
                    <detail />
                </soap:Fault>
            </soap:Body>
        </soap:Envelope>
    """,
    'NOT_FOUND': """<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
            <soap:Body>
                <ValidVehicleDocumentResponse xmlns="https://srvepak.atd.lv:9473/">
                    <ValidVehicleDocumentResult CompanyRegistrationNumber="" CompanyName="">
                        <Documents />
                    </ValidVehicleDocumentResult>
                </ValidVehicleDocumentResponse>
            </soap:Body>
        </soap:Envelope>
    """,
}
