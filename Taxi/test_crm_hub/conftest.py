# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
import pytest

import crm_hub.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['crm_hub.generated.service.pytest_plugins']


@pytest.fixture(scope='function')
def check_report(caplog):
    def _check_report(required_fields, no_report=False, **kwargs):
        validate = {'success': 'true', **kwargs}
        for record in caplog.get_records(when='call'):
            if record.msg == 'report':
                if no_report:
                    pytest.fail('report not expected')
                assert record.levelname == 'INFO'
                for field in required_fields:
                    assert field in record.extdict
                for key, val in validate.items():
                    if val is None:
                        assert key not in record.extdict
                    else:
                        assert record.extdict[key] == val
                return
        if not no_report:
            pytest.fail('report isn\'t found')

    return _check_report


@pytest.fixture(scope='function')
def dif_log(caplog):
    def _dif_log(substr):
        result = False
        for record in caplog.get_records(when='call'):
            log_msg = record.msg
            if log_msg.find(substr) != -1:
                result = True
        return result

    return _dif_log
