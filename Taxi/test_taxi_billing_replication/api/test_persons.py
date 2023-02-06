import pytest


@pytest.mark.parametrize(
    'client_id,expected',
    [
        (
            '1',
            [
                {
                    'ID': '3265597',
                    'POSTADDRESS': 'Юрьевский пер. д. 16А (*)',
                    'OWNERSHIP_TYPE': None,
                    'DELIVERY_TYPE': None,
                    'LEGAL_ADDRESS_POSTCODE': None,
                    'NAME': 'Testar Testovich Testov',
                    'MNAME': 'Testovich',
                    'LONGNAME': (
                        'Индивидуальный предприниматель '
                        'Testar Testovich Testov'
                    ),
                    'LNAME': 'Testov',
                    'PHONE': '+71111111111',
                    'INN': '123',
                    'CLIENT_ID': '1',
                    'AUTHORITY_DOC_TYPE': 'Свидетельство о регистрации',
                    'FNAME': 'Testar',
                    'INVALID_BANKPROPS': 'True',
                    'LEGALADDRESS': '111111, улица, дом, Мытищи, МО, Россия',
                    'TYPE': 'ur',
                    'EMAIL': 'test01@gmail.com',
                    'SIGNER_PERSON_NAME': 'Another Dude Entirely',
                    'KPP': None,
                    'OGRN': '111102200022011',
                    'BIK': '044011044',
                    'BANK': None,
                    'BANKCITY': None,
                    'ACCOUNT': '00000010100000001100',
                    'CORRACCOUNT': None,
                    'DT': '2017-11-02 11:57:09',
                    'KZ_IN': None,
                },
                {
                    'ID': '3659468',
                    'POSTADDRESS': None,
                    'OWNERSHIP_TYPE': None,
                    'DELIVERY_TYPE': None,
                    'LEGAL_ADDRESS_POSTCODE': None,
                    'NAME': 'Estra Estrovna Estrova',
                    'MNAME': 'Estrovna',
                    'LONGNAME': (
                        'Индивидуальный предприниматель '
                        'Estra Estrovna Estrova'
                    ),
                    'LNAME': 'Estrova',
                    'PHONE': '+72222222222',
                    'INN': '456',
                    'CLIENT_ID': '1',
                    'AUTHORITY_DOC_TYPE': 'Устав',
                    'FNAME': 'Estra',
                    'INVALID_BANKPROPS': None,
                    'LEGALADDRESS': (
                        '100121, г.Екатеринбург, ул. Поддубная, 987/4'
                    ),
                    'TYPE': 'ph',
                    'EMAIL': 'd@mail.ru',
                    'SIGNER_PERSON_NAME': None,
                    'KPP': '118001001',
                    'OGRN': '111100000011011',
                    'BIK': '244211244',
                    'BANK': None,
                    'BANKCITY': None,
                    'ACCOUNT': '00000010100000001100',
                    'CORRACCOUNT': 'a',
                    'DT': '2016-12-11 18:20:58',
                    'KZ_IN': None,
                },
            ],
        ),
        (
            '2',
            [
                {
                    'ID': '9137508',
                    'POSTADDRESS': (
                        '620149,Екатеринбург,ул Рябинина,29, кв.539'
                    ),
                    'OWNERSHIP_TYPE': 'SELFEMPLOYED',
                    'DELIVERY_TYPE': '4',
                    'LEGAL_ADDRESS_POSTCODE': '110111',
                    'NAME': 'Web Design, Ltd',
                    'MNAME': None,
                    'LONGNAME': 'Web Design, Ltd',
                    'LNAME': None,
                    'PHONE': '+73333332222',
                    'INN': '789',
                    'CLIENT_ID': '2',
                    'AUTHORITY_DOC_TYPE': 'Доверенность',
                    'FNAME': None,
                    'INVALID_BANKPROPS': 'True',
                    'LEGALADDRESS': 'Israel Tel-Aviv Street 1',
                    'TYPE': 'eu_yt',
                    'EMAIL': 'a@yandex.ru',
                    'SIGNER_PERSON_NAME': None,
                    'KPP': None,
                    'OGRN': None,
                    'BIK': None,
                    'BANK': None,
                    'BANKCITY': None,
                    'ACCOUNT': None,
                    'CORRACCOUNT': None,
                    'DT': '2018-12-29 13:28:31',
                    'KZ_IN': '180540020512',
                },
            ],
        ),
        ('3', []),
        ('4', []),
    ],
)
async def test_get_client_persons(
        taxi_billing_replication_client, client_id, expected,
):
    response = await taxi_billing_replication_client.request(
        'GET', '/person/', params={'client_id': client_id},
    )

    assert response.status == 200

    response_data = await response.json()
    assert sorted(response_data, key=lambda x: x['ID']) == expected
