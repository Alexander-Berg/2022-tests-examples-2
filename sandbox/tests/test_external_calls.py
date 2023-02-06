import pytest
from sandbox.projects.tank.Firestarter.external_calls import call_tank_finder, parse_tf_response, get_tank_version
from sandbox.projects.tank.Firestarter.tasks import TankTest
from unittest.mock import patch

import json
import requests


class TestCallTankFinder:

    test_data_2 = [
        (   # 0 - target and tank given, they match
            ('matilda.tanks.yandex.net', '22', 'tulip.tanks.yandex.net', '8083',),
            ({"result": True}, ''),
            ('matilda.tanks.yandex.net', '22', 1, '')
        ),
        (   # 1 - target and tank given, they don't match
            ('matilda.tanks.yandex.net', '22', 'lee.tanks.yandex.net', '8083'),
            ({"result": False}, ''),
            ('matilda.tanks.yandex.net', '22', 0, 'Target and tank are in different dc, sorry')
        ),
        (   # 2 - only target is given by hostname
            ('matilda.tanks.yandex.net', '', '', ''),
            (
                [{"hostname": "matilda.tanks.yandex.net", "tank": "matilda.tanks.yandex.net", "port": 8083,
                  "service": "hardware", "dc": "iva"},
                 {"hostname": "matilda.tanks.yandex.net", "tank": "tulip.tanks.yandex.net", "port": 8083,
                  "service": "hardware", "dc": "iva"},
                 {"hostname": "matilda.tanks.yandex.net", "tank": "violet.tanks.yandex.net", "port": 8083,
                  "service": "hardware", "dc": "iva"}],
                ''
            ),
            ('matilda.tanks.yandex.net', '80', 3, '')
        ),
        (   # 3 - tank given by group name
            ('lee.tanks.yandex.net', '876', 'nanny:production_yandex_tank', '', ),
            (
                [
                    {"tank": "sas1-8786-a4e-all-rcloud-tanks-30169.gencfg-c.yandex.net",
                     "service": "rtc", "target_port": None, "hostname": "lee.tanks.yandex.net",
                     "port": 30169, "dc": "sas"},
                    {"tank": "sas1-0021-all-rcloud-tanks-30169.gencfg-c.yandex.net", "service": "rtc",
                     "target_port": None, "hostname": "lee.tanks.yandex.net", "port": 30169, "dc": "sas"},
                    {"tank": "sas1-0147-all-rcloud-tanks-30169.gencfg-c.yandex.net", "service": "rtc",
                     "target_port": None, "hostname": "lee.tanks.yandex.net", "port": 30169, "dc": "sas"},
                    {"tank": "sas2-7111-25e-all-rcloud-tanks-30169.gencfg-c.yandex.net", "service": "rtc",
                     "target_port": None, "hostname": "lee.tanks.yandex.net", "port": 30169, "dc": "sas"}
                ],
                ''
            ),
            ('lee.tanks.yandex.net', '876', 4, ''),
        ),
        (   # 4 - only target is given by ipv6
            ('2a02:6b8:c08:c907:0:1459:0:1a', '5000', '', '', ),
            (
                [{
                    "hostname": "2a02:6b8:c08:c907:0:1459:0:1a", "tank": "chaffee.tanks.yandex.net", "port": 8083,
                    "service": "hardware", "dc": "sas"
                },
                    {
                        "hostname": "2a02:6b8:c08:c907:0:1459:0:1a", "tank": "hellcat.tanks.yandex.net", "port": 8083,
                        "service": "hardware", "dc": "sas"
                    }
                    ],
                ''
            ),
            ('2a02:6b8:c08:c907:0:1459:0:1a', '5000', 2, '')
        ),
        (  # 5 - target is given by ipv6 in brackets
            ('[2a02:6b8:c08:c907:0:1459:0:1a]', '5000', '', '',),
            (
                [{
                    "hostname": "2a02:6b8:c08:c907:0:1459:0:1a", "tank": "chaffee.tanks.yandex.net", "port": 8083,
                    "service": "hardware", "dc": "sas"
                },
                    {
                        "hostname": "2a02:6b8:c08:c907:0:1459:0:1a", "tank": "hellcat.tanks.yandex.net", "port": 8083,
                        "service": "hardware", "dc": "sas"
                    }
                ],
                ''
            ),
            ('[2a02:6b8:c08:c907:0:1459:0:1a]', '5000', 2, '')
        ),
        (   # 6 - Connection Error
            ('2a02:6b8:c08:c907:0:1459:0:1a', '5000', '', '', ),
            ([], 'Reply from tank_finder is not available, check backend logs'),
            ('2a02:6b8:c08:c907:0:1459:0:1a', '5000', 0, 'Reply from tank_finder is not available, check backend logs')
        )
        ]

    test_data = [
        (   # 0 - target and tank given, they match
            ('matilda.tanks.yandex.net', 'tulip.tanks.yandex.net', 'man'),
            ({'result': True}, ''),
            []
        ),
        (   # 1 - target and tank given, they don't match
            ('matilda.tanks.yandex.net', 'lee.tanks.yandex.net', ''),
            ({'result': False}, ''),
            []
        ),
        (   # not list in tank-finder answer
            ('matilda.tanks.yandex.net', 'common', 'nng'),
            ({'tank': 'T-72', 'port': 'Murmansk'}, 'Ehal Greka cherez reku'),
            []
        ),
        (   # one tank in tank-finder answer
            ('matilda.tanks.yandex.net', 'common', ''),
            ([{'tank': 'pshenichnov', 'port': 1900}], ''),
            ['pshenichnov:1900']
        ),
        (   # two tanks in tank-finder answer
            ('matilda.tanks.yandex.net', 'nanny:sukhareva_1891', ''),
            ([{'tank': 'ermolieva', 'port': 1898}, {'tank': 'bakulev', 'port': 1890}], ''),
            ['ermolieva:1898', 'bakulev:1890']
        ),
        (   # one tank in tank-finder answer
            ('matilda.tanks.yandex.net', 'nanny:puchkovskaya_1908', 'sml'),
            ({'fqdn': ['rogozov:1934']}, ''),
            ['rogozov:1934']
        ),
        (   # two tanks in tank-finder answer
            ('matilda.tanks.yandex.net', 'deploy:amosov.1913', 'kiv'),
            ({'fqdn': ['roshal', 'bogomolets', 'ilizarov']}, ''),
            ['roshal', 'bogomolets', 'ilizarov']
        ),
    ]
    # TODO https://st.yandex-team.ru/LUNAPARK-3620
    # 6 - tank given by service and group

    @pytest.mark.parametrize('function_input, mock_reply, expected', test_data)
    def test_tank_finder_by_tank_host_and_target(self, mocker, function_input, mock_reply, expected):

        mocker.patch(
            'sandbox.projects.tank.Firestarter.external_calls.external_call', return_value=mock_reply
        )
        tank_list = call_tank_finder(*function_input)
        assert tank_list == expected


class TestParseTFResponse:

    tankfinder_reply = [
        # 0 - /check_hosts True
        (
            {'result': True},
            (0, '')
        ),
        # 1 - /check_hosts False
        (
            {'result': False},
            (0, '')
        ),
        # 2 - /check_hosts error
        (
            {"result": "error", "error_msg": "Wrong tank or target hostname(ip address)"},
            (0, 'Wrong tank or target hostname(ip address)')
        ),
        # 3 - tanks list
        (
            [
                {"hostname": "lee.tanks.yandex.net", "tank": "chaffee.tanks.yandex.net", "port": 8083,
                 "service": "hardware", "dc": "sas"},
                {"hostname": "lee.tanks.yandex.net", "tank": "hellcat.tanks.yandex.net", "port": 8083,
                 "service": "hardware", "dc": "sas"}
            ],
            (
                2,
                ''
            )
        )
    ]

    @pytest.mark.parametrize('tf_reply, expected', tankfinder_reply)
    def test_parsing(self, tf_reply, expected):
        tanks_list, error = parse_tf_response(tf_reply)
        assert (len(tanks_list), error) == expected


class TestCheckTestStatus:

    def test_get_status_with_exception(self):
        job = TankTest()
        with patch('load.projects.tankapi_cmd.src.client.LunaparkTank.get_test_status') as get_test:
            get_test.side_effect = IOError
            assert job.check_status() == (0, 'FAILED', None)


def test_get_tank_version():
    resp = requests.Response()
    with patch('requests.get') as response:

        # If the response from the tank contains the version field
        resp._content = json.dumps({'users_activity': [], 'version': 'YandexTank/1.16.4'}).encode('utf-8')
        response.return_value = resp
        assert get_tank_version('lee.tanks.yandex.net:8083') == '1.16.4'

        # If the response from the tank does not contain the version field
        resp._content = json.dumps({'is_preparing': False, 'is_testing': False, 'lunapark_ids': []}).encode('utf-8')
        response.return_value = resp
        assert get_tank_version('lee.tanks.yandex.net:8083') is None
