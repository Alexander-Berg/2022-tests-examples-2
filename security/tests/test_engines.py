


from app.engines.redis_checker_engine import RedisCheckerEngine
from app.settings import PROTO_TCP
from app.utils import addr_to_proto


def test_redis_scan_res_to_splunk_events():
    input_ = {
        'auth_required': None,
        'ip': '2a02:6b8:0:1a46:682b:7fff:fec9:37f1',
        'enabled': False,
        'ssl': None,
        'version': None,
        'unknown_exception': False,
        'protected_mode': False,
        'port': 6379
    }

    expected_resp = 'nikkraev,oxcd8o,glush,eatroshkin,broom,isharov'
    expected_scripts = {
        'redis_checker_version': None,
        'redis_checker_auth_required': None,
        'redis_checker_unknown_exception': False,
        'redis_checker_protected_mode': False,
        'redis_checker_ssl': None
    }
    expected = {
        'event_type': 'info',

        'projectId': None,
        'projectName': None,
        'engine': None,
        'logClosed': None,
        'tags': [],

        'policyId': None,

        'dest_ip': input_.get('ip'),
        'resp': expected_resp,
        'protocol': addr_to_proto(input_.get('ip')),

        'dest_port': input_.get('port'),
        'transport': PROTO_TCP,
        'time': None,
        'enabled': False,
        'scripts': expected_scripts,

        'service_name': None,
        'service_product': None,
        'service_version': None,

        'scanId': None,
        'scanStartTime': None,

        'taskId': None,
    }

    res = RedisCheckerEngine._scan_results_to_splunk_events_imp([input_])
    assert len(res) == 1
    assert expected == res[0]
