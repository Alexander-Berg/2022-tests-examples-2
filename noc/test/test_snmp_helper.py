import pytest

from noc.grad.grad.lib.snmp_helper import make_keys_key, oid_separator

a = {'1.1': [['1', b'if1', 1234], ['2', b'if2', 1234]], '1.2': [['1', b'', 1234], ['2', b'', 1234]]}


@pytest.mark.parametrize(
    "key_data,nokey_oids,result",
    [
        (
            {'1.1': [['1', b'if1', 1234], ['2', b'if2', 1234]], '1.2': [['1', b'', 1234], ['2', b'', 1234]]},
            [],
            (('1.1', (('1', b'if1'), ('2', b'if2'))), ('1.2', (('1', b''), ('2', b'')))),
        ),
        (
            {'1.2': [['1', b'', 1234], ['2', b'', 1234]], '1.1': [['1', b'if1', 1234], ['2', b'if2', 1234]]},
            [],
            (('1.1', (('1', b'if1'), ('2', b'if2'))), ('1.2', (('1', b''), ('2', b'')))),
        ),
    ],
)
def test_conf_merge(key_data, nokey_oids, result):
    assert make_keys_key(key_data, nokey_oids) == result


@pytest.mark.parametrize(
    "data,oid_types_key,nokey_oids,expected_red",
    [
        (
            [
                ['1.1', '2', b'aa1', 1234],
                ['1.1', '3', b'aa2', 1234],
                ['1.2', '2', b'bb1', 1234],
                ['1.2', '3', b'bb2', 1234],
            ],
            ('1.1', '1.2'),
            [],
            (
                {'1.1': [['2', b'aa1', 1234], ['3', b'aa2', 1234]], '1.2': [['2', b'bb1', 1234], ['3', b'bb2', 1234]]},
                {},
            ),
        ),
    ],
)
def test_oid_separator(data, oid_types_key, nokey_oids, expected_red):
    res = oid_separator(data, oid_types_key, nokey_oids)
    assert res == expected_red
