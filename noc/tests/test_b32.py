import noc.packages.mondata_server.mondata.ck_autojob as ckaj


def test_base32_tag():
    assert ckaj.base32_tag('port_name', 'eth0') == 'b32_port_name_mv2gqma'
