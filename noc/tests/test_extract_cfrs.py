from noc.graphene.graphene import config
from noc.graphene.graphene.apps import cacher


def test_extract_cfrs():
    hosts = [
        {
            "fqdn": "sas1-i582.yndx.net",
            "itags": [
                {"id": 306, "tag": "конюшня NOC", "parent_id": None},
                {"id": 67, "tag": "свитч", "parent_id": 306},
            ],
            "etags": [
                {"id": 465, "tag": "свитч для IPMI", "parent_id": 67},
            ],
        },
        {
            "fqdn": "consoles-vla2-8.yndx.net",
            "itags": [{"id": 306, "tag": "конюшня NOC", "parent_id": None}],
            "etags": [{"id": 313, "tag": "сервер консольного доступа", "parent_id": 306}],
        },
        {
            "fqdn": "sas-1d4.yndx.net",
            "itags": [
                {"id": 306, "tag": "конюшня NOC", "parent_id": None},
                {"id": 67, "tag": "свитч", "parent_id": 306},
                {"id": 69, "tag": "магистральный свитч", "parent_id": 67},
                {"id": 873, "tag": "distrubution с FastBone", "parent_id": 69},
            ],
            "etags": [
                {"id": 1683, "tag": "spine1", "parent_id": 67},
                {"id": 1935, "tag": "старая многодэшка", "parent_id": 873},
            ],
        },
    ]

    cases = [
        {"конюшня NOC", "свитч", "свитч для IPMI"},
        {"конюшня NOC", "сервер консольного доступа"},
        {"конюшня NOC", "свитч", "магистральный свитч", "distrubution с FastBone", "spine1", "старая многодэшка"},
    ]

    for idx, types in enumerate(cases):
        host = hosts[idx]
        raw_tags = host["itags"] + host["etags"]
        assert types == cacher.extract_cfrs(raw_tags, config.RT_ATTR_TYPE_ROOT)
