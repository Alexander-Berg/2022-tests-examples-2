from collections import namedtuple
from sandbox.projects.masstransit.common.shooting import Target, make_load_config


Resource = namedtuple('Resource', ['http_proxy'])


def test_multi_shooting():
    return make_load_config(
        task='MTDEV-305',
        component='mtinfo-all',
        targets=[
            Target(
                "host1.yandex.net:80",
                ['line(1,1000,3m)'],
                Resource('https://proxy.sandbox.yandex-team.ru/1'),
                [
                    'Host: mtinfo.maps.yandex.net',
                    'Accept: application/x-protobuf'
                ]
            ),
            Target(
                "host2.yandex.net:80",
                ['line(1,1000,1m)', 'const(1000, 2m)'],
                Resource('https://proxy.sandbox.yandex-team.ru/2'),
            ),
            Target(
                "host3.yandex.net:80",
                ['line(1,2000,1m)', 'line(1,2000,2m)'],
                ammo_resource=Resource('https://proxy.sandbox.yandex-team.ru/3'),
            ),
        ],
        autostop=[
            'http(5xx,10%,10)',
            'http(4xx,20%,10)',
        ]
    )


def test_const_shooting():
    return make_load_config(
        task='MTDEV-305',
        component='mtinfo-all (bus-receiver const)',
        targets=[
            Target(
                "host2.yandex.net:80",
                ['line(1,1000,1m)', 'const(1000, 10m)'],
                Resource('https://proxy.sandbox.yandex-team.ru/4'),
            ),
        ],
        is_const=True,
        autostop=[
            'http(5xx,10%,10)',
            'http(4xx,20%,10)',
        ]
    )
