import sandbox.projects.k50.sow_chunk_merge as sow_chunk_merge

TABLES = {
    "SOW": {
        "google_adwords": {
            "ACCOUNT_PERFORMANCE_REPORT": {
                "2fa3f96f236ac848d262afeee76b74d1": {
                    "2020-01-01": None,
                    "tmp": {
                        "2020-01-02": None,
                    }
                }
            }
        },
        "my_target": {
            "campaigns_stat": {
                "29c0efae7b2f4022598a0c469e0505dd": {
                    "2020-01-03": None,
                    "tmp": {
                        "2020-01-04": None,
                    }
                }
            }
        }
    }
}

EXP_RESULT = [
    "SOW/google_adwords/ACCOUNT_PERFORMANCE_REPORT/2fa3f96f236ac848d262afeee76b74d1/2020-01-01",
    "SOW/my_target/campaigns_stat/29c0efae7b2f4022598a0c469e0505dd/2020-01-03",
]


def test_parse_tables():
    assert EXP_RESULT == sow_chunk_merge.parse_tables(TABLES)
