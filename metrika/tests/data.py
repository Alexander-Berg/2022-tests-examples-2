vault = {
    'sec-01ckbpeeq0926ty0rmz2jn5jy4': {
        'version': 'ver-01e20d0n56j1c4dy39mm6jzv2y',
        'name': 'awesome',
    },
    'sec-01ckx62bkvpee201ks4d4a1g09': {
        'version': 'ver-01ckx62bm2j00f44sag2910hn5',
        'name': 'super',
    }
}

yc_clusters = {
    "mdb7lttvnv3vomtq2f0s": {
        "type": "postgresql",
        "version": "12",
        "name": "airflow_postgresql",
        "hosts": [
            {
                "fqdn": "man-n94orrvcxn38tsxt.db.yandex.net",
                "dc": "man",
                "shard": "noshard"
            },
            {
                "fqdn": "sas-lmrjzxby9ry9et3e.db.yandex.net",
                "dc": "sas",
                "shard": "noshard"
            }
        ],
        "folder_id": "foori5uktoh2v12cbltq",
        "description": "postresql для airflow аналитиков",
        "id": "mdb7lttvnv3vomtq2f0s"
    },
    "mdbr7mc969bedk48vhl1": {
        "description": "Монга для Базинги. Продакшен.",
        "id": "mdbr7mc969bedk48vhl1",
        "folder_id": "foori5uktoh2v12cbltq",
        "hosts": [
            {
                "shard": "rs01",
                "dc": "man",
                "fqdn": "man-5lhxezsk0cui0kdf.db.yandex.net"
            },
            {
                "fqdn": "sas-9exbl0ftdyxaih26.db.yandex.net",
                "dc": "sas",
                "shard": "rs01"
            },
            {
                "fqdn": "vla-mslk73b98idch9wv.db.yandex.net",
                "dc": "vla",
                "shard": "rs01"
            }
        ],
        "type": "mongodb",
        "version": "4.2",
        "name": "bazinga-prod"
    },
    "mdbcgg3ua7bothld2oh0": {
        "hosts": [
            {
                "fqdn": "man-5hf9xkc01m32j4mc.db.yandex.net",
                "dc": "man",
                "shard": "shard2"
            },
            {
                "dc": "man",
                "fqdn": "man-7ktry56mhbey4odl.db.yandex.net",
                "shard": "shard3"
            },
            {
                "shard": "shard1",
                "dc": "man",
                "fqdn": "man-unjkfjj1bpuntj3u.db.yandex.net"
            },
            {
                "shard": "shard4",
                "dc": "man",
                "fqdn": "man-wqdak2frgd3lgd1e.db.yandex.net"
            },
            {
                "shard": "shard4",
                "dc": "sas",
                "fqdn": "sas-9cnwc2yqsmurdkbu.db.yandex.net"
            },
            {
                "dc": "sas",
                "fqdn": "sas-e5byl1z2e8drv6t9.db.yandex.net",
                "shard": "shard3"
            },
            {
                "fqdn": "sas-tqf56dh3bk1uvdjb.db.yandex.net",
                "dc": "sas",
                "shard": "shard2"
            },
            {
                "shard": "shard1",
                "fqdn": "sas-zjvmipae5g700ezf.db.yandex.net",
                "dc": "sas"
            },
            {
                "shard": "shard2",
                "fqdn": "vla-5vcii5z1q62kzbsd.db.yandex.net",
                "dc": "vla"
            },
            {
                "fqdn": "vla-g3x05gru8gc61kgl.db.yandex.net",
                "dc": "vla",
                "shard": "shard3"
            },
            {
                "shard": "shard4",
                "fqdn": "vla-jm9iwrc4xoiqtb38.db.yandex.net",
                "dc": "vla"
            },
            {
                "fqdn": "vla-smdkvluc5jy5m3nu.db.yandex.net",
                "dc": "vla",
                "shard": "shard1"
            }
        ],
        "type": "clickhouse",
        "version": "20.8",
        "name": "cdp",
        "description": "",
        "id": "mdbcgg3ua7bothld2oh0",
        "folder_id": "foori5uktoh2v12cbltq"
    },
    "mdb5613cdndsfitkfm7s": {
        "name": "Metrica-test-changed-for-test",
        "version": "5.7",
        "type": "mysql",
        "hosts": [
            {
                "shard": "noshard",
                "dc": "man",
                "fqdn": "man-eyxw7ulkuyt9e6bv.db.yandex.net",
                "replication_source": ""
            },
            {
                "shard": "noshard",
                "dc": "sas",
                "fqdn": "sas-od6p2sri5p9zr4vn.db.yandex.net",
                "replication_source": ""
            },
            {
                "shard": "noshard",
                "fqdn": "vla-t7ezuyq3h15tjx21.db.yandex.net",
                "dc": "vla",
                "replication_source": "sas-od6p2sri5p9zr4vn.db.yandex.net"
            }
        ],
        "folder_id": "foori5uktoh2v12cbltq",
        "id": "mdb5613cdndsfitkfm7s",
        "description": "mtclick Metrica тестинг"
    }
}
