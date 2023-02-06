import base64
import json

from Crypto.Cipher import AES
import pytest


SECRET_KEY_FROM_SECDIST = 'NdRgUkXp2s5v8y/A?D(G+KbPeShVmYq3'


class AESCipher:
    def __init__(self, key):
        self.key = key

    def unpad(self, enc):
        return enc[: -ord(enc[len(enc) - 1 :])]

    def decrypt(self, enc):
        block_size = 16
        enc = base64.urlsafe_b64decode(enc.encode('utf-8'))
        iv_ = enc[:block_size]
        cipher = AES.new(self.key.encode(), AES.MODE_CBC, iv_)
        return self.unpad(cipher.decrypt(enc[block_size:]))


@pytest.mark.parametrize('is_internal', [False, True])
@pytest.mark.parametrize('partner_id,place_id', [(1, 10), (2, 11), (3, 12)])
async def test_generate_key_data(
        taxi_eats_restapp_support_chat,
        partner_id,
        place_id,
        pgsql,
        is_internal,
):
    if is_internal:
        response = await taxi_eats_restapp_support_chat.post(
            '/internal/support_chat/v1/generate_key_data?'
            'partner_id={}&place_id={}'.format(partner_id, place_id),
        )
    else:
        response = await taxi_eats_restapp_support_chat.post(
            '/4.0/restapp-front/support_chat/v1/generate_key_data?'
            'place_id={}'.format(place_id),
            headers={'X-YaEda-PartnerId': str(partner_id)},
        )
    assert response.status == 200
    assert response.json()['data']
    secret_data = response.json()['data']
    # к сожалению, нельзя проверить по значению,
    # т. к. значение каждый раз будет новое,
    # но можно проверить по размерам блоков (кратно 4м)
    assert len(secret_data) % 4 == 0

    # проверка на создание записи в базе
    cursor = pgsql['eats_restapp_support_chat'].cursor()
    cursor.execute(
        'SELECT nonce,expire_at FROM'
        ' eats_restapp_support_chat.applied_keys',
    )
    res = list(cursor)
    assert len(res) == 1
    # расшифровываем полученную строку и сравниваем значения
    aes = AESCipher(SECRET_KEY_FROM_SECDIST)
    decrypt_json = aes.decrypt(secret_data)
    # распаковываем json
    data_json = json.loads(decrypt_json)
    assert data_json['nonce'] == res[0][0]
    assert data_json['partner_id'] == partner_id
    assert data_json['place_id'] == place_id


@pytest.mark.parametrize('is_internal', [False, True])
@pytest.mark.parametrize('partner_id,', [10, 15, 25])
async def test_generate_key_data_without_place_id(
        taxi_eats_restapp_support_chat, partner_id, pgsql, is_internal,
):
    if is_internal:
        response = await taxi_eats_restapp_support_chat.post(
            '/internal/support_chat/v1/generate_key_data?'
            'partner_id={}'.format(partner_id),
        )
    else:
        response = await taxi_eats_restapp_support_chat.post(
            '/4.0/restapp-front/support_chat/v1/generate_key_data',
            headers={'X-YaEda-PartnerId': str(partner_id)},
        )
    assert response.status == 200
    assert response.json()['data']
    secret_data = response.json()['data']
    # к сожалению, нельзя проверить по значению,
    # т. к. значение каждый раз будет новое,
    # но можно проверить по размерам блоков (кратно 4м)
    assert len(secret_data) % 4 == 0

    # проверка на создание записи в базе
    cursor = pgsql['eats_restapp_support_chat'].cursor()
    cursor.execute(
        'SELECT nonce,expire_at FROM'
        ' eats_restapp_support_chat.applied_keys',
    )
    res = list(cursor)
    assert len(res) == 1
    # расшифровываем полученную строку и сравниваем значения
    aes = AESCipher(SECRET_KEY_FROM_SECDIST)
    decrypt_json = aes.decrypt(secret_data)
    # распаковываем json
    data_json = json.loads(decrypt_json)
    assert data_json['nonce'] == res[0][0]
    assert data_json['partner_id'] == partner_id
    assert 'place_id' not in data_json
