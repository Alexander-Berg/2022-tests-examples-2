# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import jwt
import pytest

from talaria_misc_plugins import *  # noqa: F403 F401


@pytest.fixture(name='get_users_form_db')
def _get_users_from_db(pgsql):
    def _get(where, fields=None):
        if fields is None:
            fields = [
                'wind_user_id',
                'firebase_local_id',
                'wind_token',
                'wind_pd_token',
                'yandex_uid',
                'yandex_user_id',
                'personal_phone_id',
                'locale',
            ]

        fields_str = ','.join(fields)
        cursor = pgsql['talaria_misc'].cursor()

        cursor.execute(
            f'SELECT {fields_str} '
            f'FROM talaria_misc.users '
            f'WHERE {where};',
        )
        users = []
        rows = cursor.fetchall()
        for row in rows:
            row = list(row)
            user = dict()
            for i, field in enumerate(fields):
                user[field] = row[i]
            users.append(user)
        return users

    return _get


@pytest.fixture(name='default_pa_headers')
def _default_pa_headers():
    def _wrapper(
            phone_pd_id='phone_pd_id',
            yandex_uid='yandex_uid',
            yandex_user_id='some_user_id',
            app_brand='yataxi',
            app_name='iphone',
    ):
        return {
            'X-LOGIN-ID': 'login_id',
            'X-Yandex-UID': yandex_uid,
            'X-Request-Language': 'en',
            'X-YaTaxi-User': (
                f'personal_phone_id={phone_pd_id},'
                'personal_email_id=333,'
                'eats_user_id=444'
            ),
            'X-YaTaxi-PhoneId': phone_pd_id,
            'X-Request-Application': (
                f'app_name={app_name},'
                f'app_ver1=10,app_ver2=2,app_brand={app_brand}'
            ),
            'User-Agent': 'some_agent',
            'X-YaTaxi-UserId': yandex_user_id,
            'Timezone': 'Europe/Moscow',
            'X-Remote-IP': '1.2.3.4',
        }

    return _wrapper


@pytest.fixture(name='wind_user_auth_mock')
def _default_auth_mock(
        load_json, mockserver, jwt_iss, jwt_aud, jwt_scope, wind_api_key,
):
    @mockserver.json_handler('/google-oauth/token')
    def _mock_google_oauth(request):
        decoded = jwt.decode(
            request.json['assertion'],
            jwt_secret,
            algorithms=['RS256'],
            audience='https://oauth2.googleapis.com/token',
            options={'verify_signature': False},
        )
        assert decoded.get('iss') == jwt_iss
        assert decoded.get('aud') == jwt_aud
        assert decoded.get('scope') == jwt_scope
        return load_json('google_oauth_response.json')

    @mockserver.json_handler('/firebase-api/v1/projects/123/accounts:lookup')
    def _mock_firebase_lookup_response(request):
        phone_number = request.json['phoneNumber'][0]
        users = load_json('firebase_response.json')
        for user in users:
            if user['users'][0].get('phoneNumber') == phone_number:
                return user
        return {'kind': 'test'}

    @mockserver.json_handler('/firebase-api/v1/projects/123/accounts')
    def _mock_firebase_create_user_response(request):
        return load_json('firebase_create_new_user_response.json')

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _mock_firebase_response(request):
        return load_json('personal_v1_phone_find_primary.json')

    @mockserver.json_handler('/wind-pd/pf/v1/user')
    def _mock_wind_get_user(request):
        assert request.headers.get('x-api-key') == wind_api_key
        firebase_uid = request.json['firebaseUid']
        users = load_json('wind_pf_v1_user_response.json')
        for user in users:
            if user['user']['firebaseUid'] == firebase_uid:
                return user
        return load_json('wind_pf_v1_user_response_default.json')[0]


@pytest.fixture(name='jwt_secret')
def jwt_secret():
    return """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDQFGa0DaTCGXrd
qhXjM9rUjY8ATePXX8GjHNxsrwbTdUFdh9fMEdA80IGJt0jAyHl9+8sMNS7guwpr
id1i8HIr0vMdnTWK4LCkcnvqEVjYFamttMH6aCK2EjDBWO724LUFLs9bW9RB5D5X
0gRNAFTMbdhPAlNpn9F+Ult8QLxbjVW1TCYxf6iZVuIUsMUIiSrT//4u0niAPJVb
pAK+QbdqSvy5OQM4DQUg6z9J3hbTINcI0vXqBDaBGmSYTDVUX6gzAPcO5orLSP88
GTD6l8eJ8t63xHtPqbXqTLhVyXWysZa2e5yx7EaUqKo9HZOAD9Dj/aKfQPT8V3dn
V7VkPtXPAgMBAAECggEAYaTRNTkZ0cPnNlH0h3P0Ar6TFo92lcDnu0V14sKXr29c
xylSCP9q+r7VquyJhX4OFSKtfAMRBoB/OUuuyhkPWqVZVNJLJ+qcue7HW2XcjTpN
L6idRobLkykiG/lB2jREfjQjNjn3dxxGbSuuvPukz3HUie8LeYt34ZGAQOSX/1WQ
KAob7IXqb1284dJODhT6pbfQZg1UKwSky5zPkX4H0uSlGHf+K53QV5qxfB9Grxbr
NseUUhNddv0BGSwqA5A5I4+88eEFevPA2/Ur4THWg//UDxpunS5LfWqa859H2HR7
G7ujuNXU+J8ENoj1VOnfMLFp+di/59W64aL6eabiAQKBgQD8EV3ONa6mVeFcYrwq
ot88fO9CPttUwWaPtANQrCgB45SH5C3OKZxSAsFmIs9yfc5/e3eXu6iuX+Y3QBgR
yNpHIChPfbVECKkbwxNRCpATD2OLkUgNH3uLFA/j5LFQTc5jeoIX9uPvGTpbUydJ
1yBQPvJpQCBFiEI6WBlaTH3ZTwKBgQDTU140Gfe9x1QOpbFHVfj4heSdhassAAYW
TQgBNsNggzq1yMxa1aL2CC3eOTbOszRSnDNWHAwOj7G8yMkDofG4WHH/Tnu3TXXr
f+X+powPmI6gBi8zmzROESNnqQfNSzaUAjt7vJFkQ6SKkXvKhLLvc2CKcCLaCOeV
RGcPUkcbgQKBgQDmL9XCIjPDolmSzHeZV/MUgeLcVBpnY9YNFQ6R9STz1KgnELDj
vAwMuId0hgV7QHf64v1riuuXkeviOJ3CX/E1UqB9Nwb5gg8sUxCoyUSYo0z8f0eU
9FMVxtRcANQLyYHYRl/XEpdEGX25OE6Al/viTBmDFBRkavJP5XQBiijC8QKBgCKj
SY+UqgzLPTXhZrtglhx2JdDD9hiSMG07VxKL3V5WZCsjrIs+9SUKlioUiq06plrc
C3YTxs4kM2fUKU6VHr+uj5DfVlvnMGrXXeVtewubX9VO7jGxQNOC76CwDf1SVLHR
49oWQGaEx9WGnxnEwmeJK8vFMZE3YG4Q9iuGuu0BAoGALQg779BZsO9ETR+Gg9im
y8v61QptKG8CRZ38mqfeTXRYTwZ+gSZNL2ZFPOYI3PsH4U4df7NRQAEnN5EeaKY6
SxwFppy1qRIKKVD2hlsRqIbLFFq9pxTzk8oh31VY0qTISj4MckJCC+d3QAnHfui1
VSsoAj/D67zjNBVEBtmYiNU=
-----END PRIVATE KEY-----
"""


@pytest.fixture(name='jwt_aud')
def _jwt_aud():
    return 'https://oauth2.googleapis.com/token'


@pytest.fixture(name='jwt_iss')
def _jwt_iss():
    return 'firebase-testingaccount@testing-fa9bc.iam.gserviceaccount.com'


@pytest.fixture(name='jwt_scope')
def _jwt_scope():
    return 'https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/datastore https://www.googleapis.com/auth/devstorage.read_write https://www.googleapis.com/auth/firebase https://www.googleapis.com/auth/identitytoolkit https://www.googleapis.com/auth/userinfo.email'  # noqa


@pytest.fixture(name='wind_api_key')
def _wind_api_key():
    return 'windapikey'


@pytest.fixture(name='x_latitude')
def _x_latitude():
    return '32.061985'


@pytest.fixture(name='x_longitude')
def _x_longitude():
    return '34.808826'
