import pytest
from noc.library.python.racktables.functions import l2_address_for_database, canonize_mac


@pytest.mark.parametrize('address, formatted_address', [
    ['', ''],
    ['000000000000', ''],
    ['AA:FF:22:33:44:55', 'AAFF22334455'],
    ['   AA:FF:22:33:44:55   ', 'AAFF22334455'],
    ['a:f:2:33:44:55   ', '0A0F02334455'],
    ['AAFF.2233.4455', 'AAFF22334455'],
    ['AAFF22334455', 'AAFF22334455'],
    ['AA-FF-22-33-44-55', 'AAFF22334455'],
    ['AA:FF:22:33:44:55:66:77', 'AAFF223344556677'],
    ['AA-FF-22-33-44-55-66-77', 'AAFF223344556677'],
    ['AAFF223344556677', 'AAFF223344556677'],
    ['0123456789ABCDEF', '0123456789ABCDEF'],
    ['1111111111111111111111111111111111111111', '1111111111111111111111111111111111111111'],
    ['11:11:11:11:11:11:11:11:11:11:11:11:11:11:11:11:11:11:11:11', '1111111111111111111111111111111111111111'],
    ['11-11-11-11-11-11-11-11-11-11-11-11-11-11-11-11-11-11-11-11', '1111111111111111111111111111111111111111'],

])
def test_l2_address_for_database(address, formatted_address):
    assert l2_address_for_database(address) == formatted_address


@pytest.mark.parametrize('address', [
    '1',
    'a',
    '192.168.1.1',
    '11:22',
    'AAFF?2233!4455',
])
def test_malformed_l2_address_for_database(address):
    with pytest.raises(ValueError):
        l2_address_for_database(address)


@pytest.mark.parametrize('db_address, mac', [
    ['AAFF22334455', 'AA:FF:22:33:44:55'],
    ['AA:FF:22:33:44:55', 'AA:FF:22:33:44:55'],
    ['aa:ff:22:33:44:55', 'AA:FF:22:33:44:55'],
    ['aaff22334455', 'AA:FF:22:33:44:55'],
    ['001d.a2b9.e1f0', '00:1D:A2:B9:E1:F0'],
])
def test_format_to_mac(db_address, mac):
    assert canonize_mac(db_address) == mac
