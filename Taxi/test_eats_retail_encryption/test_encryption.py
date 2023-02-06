import uuid

import pytest

from eats_retail_encryption.internal import entities


@pytest.mark.parametrize(
    'vendor_host, client_id, client_secret, scope, retail_key',
    [
        [
            'ya_test.ru',
            'client_id',
            'client_secret',
            'RZ-0pXpN6B4865sp',
            'retail_key',
        ],
        [
            'ya_test.ru',
            '9gjV9j1oBA==',
            '7EZcIf4O',
            'RZ-0pXpN6B4865sp',
            'retail_key',
        ],
    ],
)
async def test_encryption_correct_decode(
        library_context,
        vendor_host,
        client_id,
        client_secret,
        scope,
        retail_key,
):

    base_retail_data = entities.RetailInfo(
        **{
            'id': 1,
            'vendor_host': vendor_host,
            'client_id': client_id,
            'client_secret': client_secret,
            'dek': uuid.uuid4().hex,
            'scope': scope,
            'retail_key': retail_key,
        },
    )
    retail_data = (
        await library_context.retail_encryption.encrypt_credentional_partner(
            retail_info=base_retail_data,
        )
    )

    retail_data = (
        await library_context.retail_encryption.get_credentional_partner(
            retail_info=retail_data,
        )
    )
    assert retail_data['vendor_host'] == vendor_host
    assert retail_data['client_id'] == client_id
    assert retail_data['client_secret'] == client_secret


async def test_encryption_encode_and_decode(
        mockserver, library_context, load_json,
):
    secdist = library_context.secdist
    retail_setting = secdist['settings_override']['RETAILS_CREDENTIALS']
    key = retail_setting['retail']['secret_key']

    origin_sting = 'Origin String for test'
    dek = uuid.uuid4().hex
    encode_string = library_context.retail_encryption.encrypt(
        origin_sting, dek,
    )
    wrapper_dek = library_context.retail_encryption.encrypt(dek, key)

    decode_string = library_context.retail_encryption.decrypt(
        encode_string, wrapper_dek, key,
    )
    assert origin_sting == decode_string
