import utils
import cfg


def test_rt_data():
    assert bool(utils.get_url_in_dict(cfg.HOST_64_IFNAMES_URL_IPv6)) is True
    assert bool(utils.get_url_in_dict(cfg.L3_TORS_IPv6)) is True


def test_rt_vlan_domain():
    assert bool(utils.get_vlans()) is True


def test_project_id_format():
    assert utils.project_id_format("0x0") == "0000:0000"
    assert utils.project_id_format("0x01") == "0000:0001"
    assert utils.project_id_format("0x012") == "0000:0012"
    assert utils.project_id_format("0x0123") == "0000:0123"
    assert utils.project_id_format("0x0123a") == "0000:123a"
    assert utils.project_id_format("0x0123ab") == "0001:23ab"
    assert utils.project_id_format("0x0123abc") == "0012:3abc"
    assert utils.project_id_format("0x0123abcd") == "0123:abcd"
    assert utils.project_id_format("0x53fc") == "0000:53fc"
    assert utils.project_id_format("0x10d53fc") == "010d:53fc"


def test_gen_vlans_config():
    vlans = utils.get_vlans()
    # vlans = {'id': '235', 'group_id': None, 'description': 'macmini-projectids', 'subdomc': '0',
    #          'vlanlist': {'1': {'vlan_id': '1', 'vlan_type': 'compulsory', 'vlan_descr': 'default'},
    #                       '1201': {'vlan_id': '1201', 'vlan_type': 'ondemand',
    #                                'vlan_descr': '0x53a0 _MACFARM_SANDBOX_NETS_'},
    #                       '1210': {'vlan_id': '1210', 'vlan_type': 'ondemand',
    #                                'vlan_descr': '0x53cf _MACFARM_SANDBOX_BROWSER_NETS_'}}, 'switchlist': {
    #         '24018': {'object_id': '24018', 'template_id': '18', 'last_errno': '0', 'out_of_sync': 'no',
    #                   'age_seconds': '3093833'}}}
    res = utils.gen_vlans_config(vlans, "2a02:6b8:c0c:c880::1/57", filename=cfg.PATH_INTERFACE_CONFIGURATION_FILE_TEST)
    assert res == res
