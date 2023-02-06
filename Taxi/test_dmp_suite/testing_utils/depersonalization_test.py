from .depersonalization import Depersonalization
from copy import deepcopy


def test_depersonalization_phones():
    raw = [
        {'user_phone': '+79111228111', 'foo': 'boo', 'l': [1, 2, 3, {'phone': '+1123-123-12'}, True]},
        {'phone': '+79111228111'}
    ]
    copy = deepcopy(raw) 
    _, replaced = Depersonalization().replace_inplace(copy)
    assert replaced
    assert raw[0]['user_phone'] != copy[0]['user_phone']
    assert raw[0]['foo'] == copy[0]['foo']
    assert raw[0]['l'][1] == copy[0]['l'][1]
    assert raw[0]['l'][3]['phone'] != copy[0]['l'][3]['phone']
    assert copy[0]['user_phone'] == copy[1]['phone']


def test_depersonalization_fio():
    raw = [
        {'name': 'Иванов Иван  Иванович '},
        {'name': 'Иванов Иван'},
        {'_name': 'Иванов Иван'},
    ]
    copy = deepcopy(raw)
    _, replaced = Depersonalization().replace_inplace(copy)
    assert replaced
    assert raw[0]['name'] != copy[0]['name']
    assert raw[1]['name'] != copy[1]['name']
    assert raw[2]['_name'] == copy[2]['_name']


def test_depersonalization_not_replaced():
    raw = [
        {'a': [1, {'id': [1, 2, 3]}]},
        {'a': 'Иванов Иван'},
        {'c': True, 'd': 1.2, },
    ]

    copy = deepcopy(raw)
    new_list, replaced = Depersonalization().replace_inplace(copy)
    assert replaced is False
    assert raw == new_list
