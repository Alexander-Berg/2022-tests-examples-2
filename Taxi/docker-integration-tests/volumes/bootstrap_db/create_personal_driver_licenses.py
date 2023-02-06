# pylint: disable=C0103
import base64
import binascii
import hashlib
import hmac
import json
import uuid

from Crypto import Random
from taxi_linters import taxi_jsonfmt

import personal_helper


def create_by_dbdriver(db_dbdrivers_file: str):
    secdist_file = 'volumes/taxi-secdist/taxi.json'
    with open(secdist_file) as file:
        secdist_json = json.load(file)

    driver_secrets = secdist_json['settings_override'][
        'PERSONAL_CRYPTO_HASH_SETTINGS'
    ]['data_types']['driver_licenses']
    key = binascii.unhexlify(driver_secrets['crypto_key'])
    cip = personal_helper.AESCipher(key)
    hash_key = binascii.unhexlify(driver_secrets['hash_key'])

    with open(db_dbdrivers_file) as file:
        drivers_json = json.load(file)

    json_output = []
    for doc in drivers_json:
        if 'driver_license_pd_id' not in doc:
            new_uuid = str(uuid.uuid4()).replace('-', '')
            doc['driver_license_pd_id'] = new_uuid

        crypto_iv = Random.get_random_bytes(16)
        hashed_value = hmac.new(
            key=hash_key,
            msg=doc['license'].encode('utf-8'),
            digestmod=hashlib.sha256,
        ).hexdigest()
        json_output.append(
            {
                '_id': doc['driver_license_pd_id'],
                'created': {'$date': float(doc['created_date']['$date'])},
                'crypto_iv': {
                    '$binary': base64.b64encode(crypto_iv).decode('utf-8'),
                    '$type': '00',
                },
                'hashed_value': hashed_value,
                'value': {
                    '$binary': cip.encrypt(doc['license'], crypto_iv).decode(
                        'utf-8',
                    ),
                    '$type': '00',
                },
            },
        )

    res_file = 'volumes/bootstrap_db/db_data/db_personal_driver_licenses.json'
    with open(res_file, 'w') as file:
        taxi_jsonfmt.dump(json_output, file)

    with open(db_dbdrivers_file, 'w', encoding='utf-8') as file:
        taxi_jsonfmt.dump(drivers_json, file)


if __name__ == '__main__':
    create_by_dbdriver('volumes/bootstrap_db/db_data/db_dbdrivers.json')
