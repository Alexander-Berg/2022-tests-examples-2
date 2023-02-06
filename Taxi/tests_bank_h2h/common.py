import collections
import datetime

import dateutil.parser

JWT_VERIFIER_PRIVATE_KEY_ES256 = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg6oLnbeoSb7op3C422x7bCsMhkTYJNM
GBUyKb0/+zPxyhRANCAAR5AKFDN18dHDyJwLAgclHuAAaFnzKjfWI5FqC8ddxersVfO+Z7RayfHc1V
6qMmqnrooadTdlq5VjuU/4KRxjl1
-----END PRIVATE KEY-----"""

JWT_VERIFIER_PRIVATE_KEY_RS256 = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDKd6A31nVN+x+DweauyCdWBYNPy5
9aq9IyCyU760LdDmGL2yXanFYhMa2++hByOw3YpE4QjxEi88cuXOCsUTnyZ+0P4XVc5PbxfDrXMaDo
QbLxnIPX8lYOvmwwl58qhwbpiUWrSPifQOWAUK02FXMDieq59fZvvBYphP24Afs59hJ2x6+M7LqDAc
SemOFErMzGt98I6X+c+j+IFlTFVoZutHH0M5hEwNIB9fCwd44Y/QwSek2tj8ZleHrfdtY9YAmfnOMT
guvTf6m5j6M70sXMzzNBr0KHGnmnprjWv66An6OGZiIWoQmeVUjcSNUjqpAOPw6T/fcSNpA0xmAGWe
eZAgMBAAECggEALVqmSpPRI7aPHPP84abG/wNNorydlhFazOiHvvgoun2b9tkQzfuK5LUs81SvhfM6
Gw9VSGrP/ykmM3nNP3STmzxSE6Zg5L4KnlZClQ2SOqzq8aoqs59ezT81W54/YqasMvjT4TZ/sSb3si
qAXpbn9IE60kzplyaGPWdD8aoJ9bXGQ1AfxqloZvaySO2ZXgqHKEtBlXDDmGSuIprcSIc3KwpRINvm
D4WzNWqJOtApGYj/1GMRyOydst818acAGQ2g3sH+KzwK3046FN45qKidmPBRPmgXOsi+UqwbCTWWfS
QiCHYEYN8K/TP94C6D6/2UZ7zVy1e/i8xBgfVHGEZkTQKBgQDyRrUDnsBZdnDnsJHFYNUxJ6Q0MZVc
L5tQjZeDdHA6q8cC73U3D2b0E/oqPSIo6DqtAjaqfleXzajFz05k8hDfyG8nA5fKClGC98qHqZ1J9S
3G1VoeAt9HhojBggLKnoD1vO0nKlhbk5pvCrldAWR7tido+BVB/2MU/4+gY7xVVQKBgQDV76RpLGj3
MxNWRvwAEeWz8Qb7xVk9ApXtb0SHhWwZ+xPUKdZ3kuIDS/toDbm1Ltbha/rmwG4cUYMvSF6kwssgMN
HvQW8NKxZiuU6pNRPa164Uh0SmAekJJul5h3rNQzCJVyHNfINprVVW9TxXaoXcK+IjciCWtG4Vd7d2
++tJNQKBgGwEMEIr7jA0yUPTCjrI4GQo+2G11ZSjOQjiB/I44KyX14OshUMGH+2kVn2sgeVhHH/0I7
FB4QWyUJPYyGfjMLjFISFwzaTrksnkdiyj55eIs18Z0jLdLvUxuxkjQOFbZ72n/MfgbkJt/YWSb3BS
5ZzuaoW3Tar+FQvQoRVuQhJ9AoGAUx0f/bBAM1GHgKxhONG7MNZCBUxdaAN6Jd1lfVULc2iFApcieB
/7aJZ7XKiAbnB9EOS3fDBkVuIgGh1+j3oSGjZ9SPtd3nrP3pjpg3lYdlv2iIko1WnGlESmzg0hW19w
GttcCY4HK+YoUnlB8SA0Ux5FY8nx+Tqtze9Nuo8SkMUCgYAwro8pvwOJL/vYdKyg29zSZXTl3Q0lp4
Cko0aZdclfjD0ksNyBRXRtUnyOPisMoeSt8YGQ+/OGxF8i1AgZxtoXeyIHVhppVYQQD+w90LTTIkba
Mr6lGgXjFxXDv3MRVpH/vu3DiTXaP02kLaKNX7JcmLYQXAe9Y0qP5nl/+fMF5Q==
-----END PRIVATE KEY-----"""

JWT_VERIFIER_PUBLIC_KEY_ES256 = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEeQChQzdfHRw8icCwIHJR7gAGhZ8yo31iORagvHXcXq
7FXzvme0Wsnx3NVeqjJqp66KGnU3ZauVY7lP+CkcY5dQ==
-----END PUBLIC KEY-----"""

# JWT_SIGNER_PRIVATE_KEY_RS256 in service.yaml/secdist

JWT_SIGNER_PUBLIC_KEY_RS256 = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAjw+HFkYn5XVVtyQVPa3gIuK77RwimAC/5i
7WA5fjUHe8qE/cOKAWEQOI8q07ytTyc92K8JWbIQza2iGrqBw/nVcGiWOOVvqLRwkiYJ+BCULeEYbA
8w70MU4ykG21/PsXWNHPo3jNnZBGAH+Brl4XuUkkbqTD++DCAX+tGNBtl0XRlei9oy2BPWjyH4Eson
ykYxwNYypSQBlrh346Qbrq9RJZt+NIVXOFNl4gbgG0W4es9K4IkO5SksJP6tjJ63dyC/BMS66DQw25
1OZC9iArBu93jBgYg5HbLL2w6rTIwoxoiOgKtt6C8fS1OEens+/BBvOhnBXUIjp95tpDCSPnfQIDAQ
AB
-----END PUBLIC KEY-----"""

SERVICE_NAME = 'bank-h2h'
IDEMPOTENCY_TOKEN = 'cfdb1504-6438-4193-885b-5885493304fe'
SENDER = 'YANDEX_PRO'
DOCUMENT_ID = 'document_id'
STATUS_ACCEPTED = 'ACCEPTED'
STATUS_NEW = 'NEW'
STATUS_FAILED = 'FAILED'
STATUS_FINISHED = 'FINISHED'

MOCK_NOW = '2021-09-28T19:31:00.1+0000'
MOCK_DATE_NOW = '2021-09-28'


def get_headers(sender=SENDER, idempotency_token=None):
    headers = {'X-YaBank-TVM-Source-Service-Name': sender}
    if idempotency_token is not None:
        headers['X-Idempotency-Token'] = idempotency_token
    return headers


def insert_statement(
        pgsql,
        idempotency_token,
        status='NEW',
        sender='',
        account='',
        date_from=datetime.date.today(),
        date_to=datetime.date.today(),
        wait_end_of_day=False,
        need_archive=False,
        statement_jwt='',
        file_name=None,
        file_name_id=None,
        error_response=None,
        created_at=datetime.datetime.now().isoformat(),
):
    cursor = pgsql['bank_h2h'].cursor()
    cursor.execute(
        (
            'INSERT INTO bank_h2h.statements(idempotency_token, status, '
            'sender, account, date_from, date_to, wait_end_of_day, '
            'need_archive, statement_jwt, file_name, file_name_id, '
            'error_response, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
            'RETURNING id'
        ),
        [
            idempotency_token,
            status,
            sender,
            account,
            date_from,
            date_to,
            wait_end_of_day,
            need_archive,
            statement_jwt,
            file_name,
            file_name_id,
            error_response,
            created_at,
        ],
    )
    return cursor.fetchone()[0]


Statement = collections.namedtuple(
    'Statement',
    [
        'idempotency_token',
        'status',
        'sender',
        'account',
        'date_from',
        'date_to',
        'wait_end_of_day',
        'need_archive',
        'statement_jwt',
        'file_name',
        'file_name_id',
        'error_response',
    ],
)


def select_statement(pgsql, statement_id):
    sql = (
        'SELECT idempotency_token, status, sender, account, date_from, '
        'date_to, wait_end_of_day, need_archive, statement_jwt, '
        'file_name, file_name_id, error_response '
        'FROM bank_h2h.statements '
        'WHERE id = %s'
    )
    cursor = pgsql['bank_h2h'].cursor()
    cursor.execute(sql, [statement_id])
    result = cursor.fetchone()
    if result is None:
        return None
    result_dict = Statement(*result)
    return result_dict


def eq_timestamp(lhv, rhv):
    return dateutil.parser.isoparse(lhv) == dateutil.parser.isoparse(rhv)


def get_support_headers(token='allow'):
    headers = {'X-Bank-Token': token}
    return headers


Document = collections.namedtuple(
    'Document', ['sender', 'id', 'document', 'document_jwt', 'status_info'],
)


def select_document(pgsql, sender, document_id):
    sql = (
        'SELECT sender, id, document, document_jwt, status_info '
        'FROM bank_h2h.documents '
        'WHERE sender = %s AND id = %s'
    )
    cursor = pgsql['bank_h2h'].cursor()
    cursor.execute(sql, [sender, document_id])
    result = cursor.fetchall()
    assert len(result) == 1
    result_dict = Document(*(result[0]))
    return result_dict


def insert_document(
        pgsql,
        sender=SENDER,
        document_id=DOCUMENT_ID,
        document='{}',
        document_jwt='',
        status_info='{}',
        created_at=datetime.datetime.now().isoformat(),
):
    cursor = pgsql['bank_h2h'].cursor()
    cursor.execute(
        (
            'INSERT INTO bank_h2h.documents(sender, id, document, '
            'document_jwt, status_info, created_at) '
            'VALUES (%s, %s, %s, %s, %s, %s) '
            'RETURNING id'
        ),
        [sender, document_id, document, document_jwt, status_info, created_at],
    )
    return cursor.fetchone()[0]


def get_document_body():
    return {
        'document_id': DOCUMENT_ID,
        'notification_url': 'https://url',
        'instructions': [
            {
                'instruction_id': '1',
                'type': 'instruction_type',
                'payment_type': 'PAYMENT_ORDER',
                'money': {'amount': '1234.56', 'currency': 'RUB'},
                'debtor': {
                    'accessor': {
                        'type': 'ACCOUNT_NUMBER',
                        'value': '40702810500000000001',
                    },
                },
                'creditor': {
                    'accessor': {
                        'type': 'EXTERNAL_WALLET_ID',
                        'value': 'w_id1',
                    },
                    'person': {'name': 'А Б В', 'tin': '823306043019'},
                },
                'settlement_date': '2022-01-01',
                'purpose_of_payment': 'Оплата поездки',
                'additional_attributes': {'any': 'any'},
                'statement_attributes': {'any2': 'any2'},
            },
            {
                'instruction_id': '2',
                'type': 'instruction_type',
                'payment_type': 'PAYMENT_REQUIREMENT',
                'money': {'amount': '234.56', 'currency': 'USD'},
                'debtor': {
                    'accessor': {
                        'type': 'EXTERNAL_WALLET_ID',
                        'value': 'w_id2',
                    },
                },
                'creditor': {
                    'accessor': {
                        'type': 'ACCOUNT_NUMBER',
                        'value': '40702810500000000002',
                    },
                },
                'settlement_date': '2022-01-02',
                'purpose_of_payment': 'Штраф',
                'additional_attributes': {'any3': 'any3'},
                'statement_attributes': {'any4': 'any4'},
            },
        ],
    }


def get_status_info():
    return {
        'instruction_statuses': [
            {
                'instruction_id': '1',
                'original_money': {'amount': '1234.56', 'currency': 'RUB'},
                'status': STATUS_ACCEPTED,
                'status_history': [
                    {'date': MOCK_DATE_NOW, 'new_status': STATUS_ACCEPTED},
                ],
            },
            {
                'instruction_id': '2',
                'original_money': {'amount': '234.56', 'currency': 'USD'},
                'status': STATUS_ACCEPTED,
                'status_history': [
                    {'date': MOCK_DATE_NOW, 'new_status': STATUS_ACCEPTED},
                ],
            },
        ],
    }
