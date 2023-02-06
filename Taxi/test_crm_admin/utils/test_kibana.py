import re

from crm_admin.utils import kibana


def test_make_url():
    url = kibana.make_url('ngroups:taxi_crm-admin* and level:ERROR')

    regex = r'https:\/\/kibana.*\/app\/kibana#\/discover\?_g=\(.*\)&_a=\(.*\)'
    assert re.match(regex, url)
