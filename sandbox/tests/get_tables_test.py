import sandbox.projects.k50.sow_map_reduce as map_reduce

TREE = {
    "SOW": {
        "google_adwords": {
            "ACCOUNT_PERFORMANCE_REPORT": {
                "2fa3f96f236ac848d262afeee76b74d1": {
                    "123": None,
                    "456": None,
                    "tmp": {
                        "2020-01-01": None,
                        "2020-01-02": None,
                        "2020-01-01_tmp": None,
                        "2020-01-02_tmp": None,
                    }
                }
            }
        },
        "my_target": {
            "campaigns_stat": {
                "29c0efae7b2f4022598a0c469e0505dd": {
                    "qwe": None,
                    "rty": None,
                    "tmp": {
                        "2020-01-03": None,
                        "2020-01-04": None,
                        "2020-01-03_tmp": None,
                        "2020-01-04_tmp": None,
                    }
                }
            }
        }
    }
}

TABLES = [
    "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-01",
    "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-02",
    "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-01_tmp",
    "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-02_tmp",
    "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-03",
    "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-04",
    "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-03_tmp",
    "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-04_tmp",
]

DATES = {
    "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-01": [
        "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-01",
        "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-01_tmp",
    ],
    "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-02": [
        "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-02",
        "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-02_tmp"
    ],
    "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-03": [
        "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-03",
        "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-03_tmp",
    ],
    "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-04": [
        "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-04",
        "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/tmp/2020-01-04_tmp",
    ],
}


def test_parse_tables():
    exp_tables = sorted(TABLES)
    res_tables = sorted(map_reduce.parse_tables(TREE))
    assert exp_tables == res_tables


def test_get_res_table():
    test_table = "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/tmp/2020-01-01_tmp"
    exp_table = "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/2020-01-01"
    res_table = map_reduce.get_res_table_name(test_table)
    assert exp_table == res_table


def test_get_dates():
    assert DATES == map_reduce.get_dates(TABLES)
