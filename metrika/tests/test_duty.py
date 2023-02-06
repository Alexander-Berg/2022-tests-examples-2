import six
import pytest
import requests_mock

import metrika.pylib.structures.dotdict as mdd
import metrika.pylib.duty as mtd
from metrika.pylib.log import init_logger


init_logger('mtutils', stdout=True)
init_logger('urllib3', stdout=True)


def test_get_duty_group():
    url = mtd.BASE_URL + '/project/metrika/duty_group/adminus/'
    with requests_mock.Mocker() as mocker:
        mocker.get(
            url,
            json={
                "data": {
                    "id": 1,
                    "name": "Admin: On-callz",
                    "order": 10,
                    "startrek": "MTRSADMIN",
                    "forward_number": 1601,
                    "owner": "robert",
                    "api_key": "adminus",
                    "users": [
                        "frenz",
                        "robert",
                        "velom",
                    ],
                    "exclude_users": [],
                    "calculated_users": [
                        "frenz",
                        "robert",
                        "velom"
                    ],
                    "staff_groups": [],
                    "moderators": [],
                    "rotate_type": "manually",
                    "previuos_duty": None,
                    "duty": "frenz",
                    "project": 1
                },
                "result": True,
                "messages": [],
                "errors": [],
            },
            status_code=200,
        )

        api = mtd.DutyAPI(token='')
        group = api.get_duty_group('metrika', 'adminus')

        assert type(group) is mdd.DotDict
        assert group.id == 1
        assert group.duty == 'frenz'


def test_missing_duty_group():
    url = mtd.BASE_URL + '/project/metrika/duty_group/adminus/'
    with requests_mock.Mocker() as mocker:
        mocker.get(
            url,
            json={
                "messages": [],
                "errors": [
                    "Duty Group does not exist in project metrika with api_key adminus"
                ],
                "data": {},
                "result": False,
            },
            status_code=404,
        )

        api = mtd.DutyAPI(token='')

        with pytest.raises(mtd.BadRequestException) as e:
            api.get_duty_group('metrika', 'adminus')

            assert isinstance(e.message, six.string_types) and e.message
            assert "Duty Group does not exist in project metrika with api_key adminus" in e.message
