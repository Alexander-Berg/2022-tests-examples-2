import pytest

from base64 import b64decode

from smart_devices.tools.burn_data.lib import (
    extract_keyboxes,
    extract_hdcp_14_keys,
    provision_keywrapper,
    WIDEVINE_PROVISION_KEY_TYPE,
    gpg_decrypt,
    Tables,
    make_old_device_id,
    DeviceType,
    make_unified_device_id,
    check_unified_device_id,
    WV_KEYBOX_EXPECTED_DEVICED_ID_LENGTH,
)


def test_tables():
    actual_tables = [t for t in dir(Tables) if not t.startswith('_') and type(getattr(Tables, t)) == type]

    for t in actual_tables:
        assert getattr(Tables, t).SUFFIX
        assert getattr(Tables, t).SCHEMA


def test_make_device_id():
    assert (
        make_old_device_id(DeviceType.yandexstation_2, 'black', 123, '01234567890', 0)
        == 'XK0000000000000001230000dff1981c'
    )
    assert (
        make_old_device_id(DeviceType.yandexstation_2, 'black', 123, '01234567890', 1)
        == 'XK00000000000000012300014722be7b'
    )
    assert (
        make_old_device_id(DeviceType.yandexmini_2, 'red', 345, '01234567890', 0) == 'MR000000000000000345000015b60331'
    )


def test_make_udid():
    assert make_unified_device_id(DeviceType.yandexmini_2, 'black', number=101, revision=0) == 'M005300003V0XK'
    assert (
        make_unified_device_id(DeviceType.yandexmini_2, 'black', number=102, revision=0, capabilities=0b00001)
        == 'M10630000XD3VK'
    )
    assert make_unified_device_id(DeviceType.yandexmodule_2, 'white', number=1001, revision=3) == 'D039Z00003ZHXW'
    assert make_unified_device_id(DeviceType.yandexmodule_2, 'white', number=1002, revision=3) == 'D03AZ0000FDPJW'
    assert make_unified_device_id(DeviceType.yandexmidi, 'black', number=101, revision=0) == 'U00530000ZKGEK'
    assert make_unified_device_id(DeviceType.yandexmidi, 'black', number=102, revision=0) == 'U0063000027PYK'
    assert make_unified_device_id(DeviceType.yandexstation_2, 'black', number=101, revision=0) == 'X00530000FEJKK'
    assert make_unified_device_id(DeviceType.yandexstation_2, 'black', number=102, revision=0) == 'X00630000JTM3K'
    assert (
        make_unified_device_id(DeviceType.yandexstation_2, 'black', number=100, revision=0, capabilities=0b00001)
        == 'X10430000RHNBK'
    )
    assert make_unified_device_id(DeviceType.yandexpluto, 'black', number=201, revision=0) == 'P00960000WQW6K'
    assert make_unified_device_id(DeviceType.yandexchiron, 'black', number=123, revision=0) == 'C00V300008DSKK'

    # Maximum possible number is encoded as ZZZZZZ
    assert (
        make_unified_device_id(DeviceType.yandexmodule_2, 'white', number=2 ** 30 - 1, revision=3) == 'D03ZZZZZZB69PW'
    )

    with pytest.raises(ValueError):
        assert make_unified_device_id(DeviceType.yandexmodule_2, 'white', number=2 ** 30, revision=3)


def test_check_udid():
    udid = make_unified_device_id(DeviceType.yandexmodule_2, 'white', number=123, revision=15, capabilities=0b10101)

    assert check_unified_device_id(udid)
    assert check_unified_device_id(udid.upper())
    assert check_unified_device_id(udid.lower())

    broken = udid[:4] + '0' + udid[5:]  # change symbol # 4
    assert not check_unified_device_id(broken)


def test_extract_keyboxes_blank():
    assert extract_keyboxes('<xml></xml>') == {}


def test_extract_short_did_keybox():
    short_did = 'aa'
    boxes = extract_keyboxes(
        f'''<?xml version="1.0"?>
<Widevine>
    <NumberOfKeyboxes>1</NumberOfKeyboxes>
    <Keybox DeviceID="{short_did}"><Key>bb</Key><ID>11</ID><Magic>22</Magic><CRC>ff</CRC></Keybox>
</Widevine>'''
    )

    pad = b'\x00' * (WV_KEYBOX_EXPECTED_DEVICED_ID_LENGTH - len(short_did))
    padded_did = short_did.encode('ascii') + pad

    assert len(short_did) < WV_KEYBOX_EXPECTED_DEVICED_ID_LENGTH
    assert len(padded_did) == WV_KEYBOX_EXPECTED_DEVICED_ID_LENGTH
    assert len(boxes) == 1
    assert short_did in boxes.keys()
    assert boxes[short_did] == padded_did + b'\xbb\x11\x22\xff'


def test_extract_long_did_keybox():
    long_did = '01234567890123456789012345678901'
    boxes = extract_keyboxes(
        f'''<?xml version="1.0"?>
<Widevine>
    <NumberOfKeyboxes>1</NumberOfKeyboxes>
    <Keybox DeviceID="{long_did}"><Key>bb</Key><ID>11</ID><Magic>22</Magic><CRC>ff</CRC></Keybox>
</Widevine>'''
    )

    assert len(long_did) == WV_KEYBOX_EXPECTED_DEVICED_ID_LENGTH
    assert len(boxes) == 1
    assert long_did in boxes.keys()
    assert boxes[long_did] == long_did.encode('ascii') + b'\xbb\x11\x22\xff'


def test_extract_hdcp_14_keys_empty():
    empty_tx_package = b'\x01\x00\x00\x00'

    assert extract_hdcp_14_keys(empty_tx_package) == []


def test_extract_hdcp_14_keys_one():
    prefix = b'\x01\x00\x00\x00'
    # key set is some data + sha1() digest of the data
    key_set = (b'\x00' * 288) + b'\xe1f|\x8c\xee\xcc\xda\xfc\xf6\xc3\xeb\xb9\xad8\xd2*\xfc\xf9\x90\x93'

    assert extract_hdcp_14_keys(prefix + key_set) == [key_set]


def test_extract_hdcp_14_keys_wrong_prefix():
    with pytest.raises(ValueError):
        extract_hdcp_14_keys(b'\x02\x00\x00\x00')


def test_extract_hdcp_14_keys_wrong_size():
    with pytest.raises(ValueError):
        extract_hdcp_14_keys(b'\x01\x00\x00\x00' + b'\x00' * 307)


def test_extract_hdcp_14_keys_wrong_checksum():
    with pytest.raises(ValueError):
        extract_hdcp_14_keys(
            b'\x01\x00\x00\x00'
            + b'\x00' * 288
            + b'\xe1f|\x8c\xee\xcc\xda\xfc\xf6\xc3\xeb\xb9\xad8\xd2*\xfc\xf9\x90\x92'
        )


def test_provision_keywrapper_smoke():
    with provision_keywrapper() as wrap:
        assert wrap(b'\x01' * 16, WIDEVINE_PROVISION_KEY_TYPE, b'\x02' * 16)


def test_gpg_decrypt():
    pk = b64decode(
        '''
    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
L/rnnavE5YR2W1Ap539lwwCqiAodBvlF
'''.strip()
    )

    secret_data = b64decode(
        '''
    hQGMA6SIun9+U1IWAQv/Y9AF1Ds87OoLIgOLm/wDIUmD6Fl59jD4pWc+SypaVr8LAPJDabmDiv+G
C0S7NA+cJcK5DDMFwUn7clYyVLqI3xtrjKkb61sZAVkd7q4v08Owz7dccy3y+73Kgj6rQCwjShRK
GRWIfDx/d0euydbadBozfbf6f3W+YliwwZr3s9N32SBQx6YBUlASnXsDUhn4iBhQ1N8ozbWCLrL2
IDGVs9sBmWsFA+Bnwe/klkO9UkXy3+AMqIXNIyfYOlqnLKSPXBZ/epapZDPvJugYgOJF1yc7h+Cc
D0Z3tWzqKhJN27zTmiYYAVcFi1NjMgGDe8h6RW4hNatFTbB1T8Bs88NSHDp/Fz+O66unOXBu3HSm
ztV4EyNnswaexzxHGWTqonpw0jU1A5IDrw9dlE0FmMbrWuXJSfRTp5CPoo19AgDW4rFxzJNDw0tj
xyNAayISJoN9/8si1T2u1fwtsy9jO+s8oQvmOFbdcgJ6v9LrV0c31r3eDb/uaD2nvT4arKhLV/rT
0kQB3AO6AC2x3UEXUR2H8cYWhjtyfHHeMfGyQONLZjfvCmXdzUz68CSEmm224vyYa444YDMiPNA2
1/F07GnOgGfKH4JNzA=='''.strip()
    )

    key_secret = {'value': {'passphrase': 'test', 'protected_private.key': pk}}

    with gpg_decrypt(key_secret) as decrypt:
        assert decrypt(secret_data) == b'foobar\n'
