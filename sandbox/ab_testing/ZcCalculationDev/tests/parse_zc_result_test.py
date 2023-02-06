# coding=utf-8
import sandbox.projects.ab_testing.ZcCalculationDev.zc_calculation as zc


def get_test_cpc_output():
    return """
            #|
            ||version|date|method|slice|bid_type|avg|lower|upper|group_count||
            ||4|20210903-20210903|BIDS_RATIO_1|ab410899|CappedBid|0.995642180466|0.983114441627|1.00772298843|194195.0||
            ||4|20210903-20210903|BIDS_RATIO_1|ab410906|CappedBid|1.00602654393|0.990485053696|1.01996588946|194471.0||
            ||4|20210903-20210903|BIDS_RATIO_1|ab410899|Cost|0.995245339485|0.982244692592|1.00850533078|194195.0||
            ||4|20210903-20210903|BIDS_RATIO_1|ab410906|Cost|1.00677715029|0.994650857432|1.02014031592|194471.0||
            ||4|20210903-20210903|BIDS_RATIO_1|ab410899|NormedBid|0.994613981097|0.983646333826|1.00599132481|194195.0||
            ||4|20210903-20210903|BIDS_RATIO_1|ab410906|NormedBid|1.00657448179|0.995837230779|1.01962403489|194471.0||
            |#
    """


def get_test_cpm_output():
    return """
            #|
            || **experiment** | **action** | **zC** | **cost_d** | **zC * cost** ||
            || 410899 | lclick | 1.0260 +/- 0.0500 | **!!(red)-87.4670 +/- 1.4371!!** | **!!(red)-87.1412 +/- 1.6035!!** ||
            || 410906 | lclick | 1.0022 +/- 0.0506 | **!!(red)-87.4772 +/- 1.4250!!** | **!!(red)-87.4503 +/- 1.5638!!** ||
            |#
    """


def get_test_cpm_v2_output():
    return """
            #|
            || **ExperimentID** | **Action** | **zC** | **Normalized zC** ||
            || 535217 | lclick | **!!(green)1.0221 +/- 0.0000!!** | 1.0000 ||
            || 535221 | lclick | **!!(green)1.0536 +/- 0.0000!!** | **!!(green)1.0308 +/- 0.0000!!** ||
            || 535223 | lclick | **!!(green)1.0788 +/- 0.0000!!** | **!!(green)1.0555 +/- 0.0000!!** ||
            |#
    """


def get_empty_zc_result(testids, start_date, end_date):
    zc_result = zc.get_default_empty_zc_result()

    zc_result["task"]["testids"] = testids
    zc_result["data"]["testids"] = testids
    zc_result["task"]["start"] = start_date
    zc_result["task"]["finish"] = end_date

    return zc_result


def get_true_test_zc_result():
    return {
        "task": {
            "granularity": "24",
            "user": "leftmain",
            "start": "20210903",
            "finish": "20210903",
            "testids": ["410899", "410906"],
            "metrics": [
                "Cost_upper",
                "Cost_lower",
                "Cost_avg",
                "CappedBid_upper",
                "CappedBid_lower",
                "CappedBid_avg",
                "NormedBid_upper",
                "NormedBid_lower",
                "NormedBid_avg",
                "lclick_cost_d",
                "lclick_zC*cost",
                "lclick_zC",
            ]
        },
        "data": {
            "testids": ["410899", "410906"],
            "metrics": {
                "lclick_zC": [
                    {"val": "1.0260"},
                    {"val": "1.0022"}
                ],
                "CappedBid_upper": [
                    {"val": "1.00772298843"},
                    {"val": "1.01996588946"}
                ],
                "Cost_upper": [
                    {"val": "1.00850533078"},
                    {"val": "1.02014031592"}
                ],
                "NormedBid_avg": [
                    {"val": "0.994613981097"},
                    {"val": "1.00657448179"}
                ],
                "lclick_cost_d": [
                    {"color": "red", "val": "-87.4670"},
                    {"color": "red", "val": "-87.4772"}
                ],
                "NormedBid_lower": [
                    {"val": "0.983646333826"},
                    {"val": "0.995837230779"}
                ],
                "CappedBid_lower": [
                    {"val": "0.983114441627"},
                    {"val": "0.990485053696"}
                ],
                "CappedBid_avg": [
                    {"val": "0.995642180466"},
                    {"val": "1.00602654393"}
                ],
                "Cost_lower": [
                    {"val": "0.982244692592"},
                    {"val": "0.994650857432"}
                ],
                "NormedBid_upper": [
                    {"val": "1.00599132481"},
                    {"val": "1.01962403489"}
                ],
                "Cost_avg": [
                    {"val": "0.995245339485"},
                    {"val": "1.00677715029"}
                ],
                "lclick_zC*cost": [
                    {"color": "red", "val": "-87.1412"},
                    {"color": "red", "val": "-87.4503"}
                ]
            }
        },
        "meta": {
            "group_nodes": [
                {
                    "key": "root",
                    "name": None,
                    "collapsed": False,
                    "metrics": [],
                    "groups": ["CPC", "CPM"]
                },
                {
                    "key": "CPC",
                    "name": "CPC",
                    "collapsed": False,
                    "metrics": [],
                    "groups": ["Cost", "CappedBid", "NormedBid"]
                },
                {
                    "key": "Cost",
                    "name": "Cost",
                    "collapsed": False,
                    "metrics": [
                        "Cost_upper",
                        "Cost_lower",
                        "Cost_avg",
                    ],
                    "groups": [],
                },
                {
                    "groups": [],
                    "metrics": [
                        "CappedBid_upper",
                        "CappedBid_lower",
                        "CappedBid_avg",
                    ],
                    "collapsed": False,
                    "name": "CappedBid",
                    "key": "CappedBid"
                },
                {
                    "groups": [],
                    "metrics": [
                        "NormedBid_upper",
                        "NormedBid_lower",
                        "NormedBid_avg",
                    ],
                    "collapsed": False,
                    "name": "NormedBid",
                    "key": "NormedBid"
                },
                {
                    "groups": [
                        "lclick"
                    ],
                    "metrics": [],
                    "collapsed": False,
                    "name": "CPM",
                    "key": "CPM"
                },
                {
                    "key": "lclick",
                    "name": "lclick",
                    "collapsed": False,
                    "groups": [],
                    "metrics": [
                        "lclick_cost_d",
                        "lclick_zC*cost",
                        "lclick_zC",
                    ],
                }
            ],
            "metrics": [
                {
                    "name": "Cost_upper",
                    "hname": "upper",
                },
                {
                    "name": "Cost_lower",
                    "hname": "lower",
                },
                {
                    "name": "Cost_avg",
                    "hname": "avg",
                },
                {
                    "name": "CappedBid_upper",
                    "hname": "upper",
                },
                {
                    "name": "CappedBid_lower",
                    "hname": "lower",
                },
                {
                    "name": "CappedBid_avg",
                    "hname": "avg",
                },
                {
                    "name": "NormedBid_upper",
                    "hname": "upper",
                },
                {
                    "name": "NormedBid_lower",
                    "hname": "lower",
                },
                {
                    "name": "NormedBid_avg",
                    "hname": "avg",
                },
                {
                    "name": "lclick_cost_d",
                    "hname": "cost_d",
                },
                {
                    "name": "lclick_zC*cost",
                    "hname": "zC*cost",
                },
                {
                    "name": "lclick_zC",
                    "hname": "zC",
                },
            ]
        }
    }


def get_true_error_test_zc_result():
    return {
        "task": {
            "granularity": "24",
            "user": "leftmain",
            "start": "20210903",
            "finish": "20210903",
            "testids": ["410899", "410906"],
            "metrics": [
                "FAILED",
                "lclick_cost_d",
                "lclick_zC*cost",
                "lclick_zC",
            ]
        },
        "data": {
            "testids": ["410899", "410906"],
            "metrics": {
                "FAILED": [{}, {}],
                "lclick_zC": [
                    {"val": "1.0260"},
                    {"val": "1.0022"}
                ],
                "lclick_cost_d": [
                    {"color": "red", "val": "-87.4670"},
                    {"color": "red", "val": "-87.4772"}
                ],
                "lclick_zC*cost": [
                    {"color": "red", "val": "-87.1412"},
                    {"color": "red", "val": "-87.4503"}
                ]
            }
        },
        "meta": {
            "group_nodes": [
                {
                    "key": "root",
                    "name": None,
                    "collapsed": False,
                    "metrics": [],
                    "groups": ["CPC", "CPM"]
                },
                {
                    "key": "CPC",
                    "name": "CPC",
                    "collapsed": False,
                    "metrics": ["FAILED"],
                    "groups": []
                },
                {
                    "groups": [
                        "lclick"
                    ],
                    "metrics": [],
                    "collapsed": False,
                    "name": "CPM",
                    "key": "CPM"
                },
                {
                    "key": "lclick",
                    "name": "lclick",
                    "collapsed": False,
                    "groups": [],
                    "metrics": [
                        "lclick_cost_d",
                        "lclick_zC*cost",
                        "lclick_zC",
                    ],
                }
            ],
            "metrics": [
                {
                    "name": "FAILED",
                    "hname": "FAILED",
                },
                {
                    "name": "lclick_cost_d",
                    "hname": "cost_d",
                },
                {
                    "name": "lclick_zC*cost",
                    "hname": "zC*cost",
                },
                {
                    "name": "lclick_zC",
                    "hname": "zC",
                },
            ]
        }
    }


def get_true_test_zc_result_cpc():
    return {
        "task": {
            "granularity": "24",
            "user": "leftmain",
            "start": "20210903",
            "finish": "20210903",
            "testids": ["410899", "410906"],
            "metrics": [
                "Cost_upper",
                "Cost_lower",
                "Cost_avg",
                "CappedBid_upper",
                "CappedBid_lower",
                "CappedBid_avg",
                "NormedBid_upper",
                "NormedBid_lower",
                "NormedBid_avg",
            ]
        },
        "data": {
            "testids": ["410899", "410906"],
            "metrics": {
                "CappedBid_upper": [
                    {"val": "1.00772298843"},
                    {"val": "1.01996588946"}
                ],
                "Cost_upper": [
                    {"val": "1.00850533078"},
                    {"val": "1.02014031592"}
                ],
                "NormedBid_avg": [
                    {"val": "0.994613981097"},
                    {"val": "1.00657448179"}
                ],
                "NormedBid_lower": [
                    {"val": "0.983646333826"},
                    {"val": "0.995837230779"}
                ],
                "CappedBid_lower": [
                    {"val": "0.983114441627"},
                    {"val": "0.990485053696"}
                ],
                "CappedBid_avg": [
                    {"val": "0.995642180466"},
                    {"val": "1.00602654393"}
                ],
                "Cost_lower": [
                    {"val": "0.982244692592"},
                    {"val": "0.994650857432"}
                ],
                "NormedBid_upper": [
                    {"val": "1.00599132481"},
                    {"val": "1.01962403489"}
                ],
                "Cost_avg": [
                    {"val": "0.995245339485"},
                    {"val": "1.00677715029"}
                ],
            }
        },
        "meta": {
            "group_nodes": [
                {
                    "key": "root",
                    "name": None,
                    "collapsed": False,
                    "metrics": [],
                    "groups": ["CPC"]
                },
                {
                    "key": "CPC",
                    "name": "CPC",
                    "collapsed": False,
                    "metrics": [],
                    "groups": ["Cost", "CappedBid", "NormedBid"]
                },
                {
                    "key": "Cost",
                    "name": "Cost",
                    "collapsed": False,
                    "metrics": [
                        "Cost_upper",
                        "Cost_lower",
                        "Cost_avg",
                    ],
                    "groups": [],
                },
                {
                    "groups": [],
                    "metrics": [
                        "CappedBid_upper",
                        "CappedBid_lower",
                        "CappedBid_avg",
                    ],
                    "collapsed": False,
                    "name": "CappedBid",
                    "key": "CappedBid"
                },
                {
                    "groups": [],
                    "metrics": [
                        "NormedBid_upper",
                        "NormedBid_lower",
                        "NormedBid_avg",
                    ],
                    "collapsed": False,
                    "name": "NormedBid",
                    "key": "NormedBid"
                },
            ],
            "metrics": [
                {
                    "name": "Cost_upper",
                    "hname": "upper",
                },
                {
                    "name": "Cost_lower",
                    "hname": "lower",
                },
                {
                    "name": "Cost_avg",
                    "hname": "avg",
                },
                {
                    "name": "CappedBid_upper",
                    "hname": "upper",
                },
                {
                    "name": "CappedBid_lower",
                    "hname": "lower",
                },
                {
                    "name": "CappedBid_avg",
                    "hname": "avg",
                },
                {
                    "name": "NormedBid_upper",
                    "hname": "upper",
                },
                {
                    "name": "NormedBid_lower",
                    "hname": "lower",
                },
                {
                    "name": "NormedBid_avg",
                    "hname": "avg",
                },
            ]
        }
    }


def get_true_test_zc_result_cpm():
    return {
        "task": {
            "granularity": "24",
            "user": "leftmain",
            "start": "20210903",
            "finish": "20210903",
            "testids": ["410899", "410906"],
            "metrics": [
                "lclick_cost_d",
                "lclick_zC*cost",
                "lclick_zC",
            ]
        },
        "data": {
            "testids": ["410899", "410906"],
            "metrics": {
                "lclick_zC": [
                    {"val": "1.0260"},
                    {"val": "1.0022"}
                ],
                "lclick_cost_d": [
                    {"color": "red", "val": "-87.4670"},
                    {"color": "red", "val": "-87.4772"}
                ],
                "lclick_zC*cost": [
                    {"color": "red", "val": "-87.1412"},
                    {"color": "red", "val": "-87.4503"}
                ]
            }
        },
        "meta": {
            "group_nodes": [
                {
                    "key": "root",
                    "name": None,
                    "collapsed": False,
                    "metrics": [],
                    "groups": ["CPM"]
                },
                {
                    "groups": [
                        "lclick"
                    ],
                    "metrics": [],
                    "collapsed": False,
                    "name": "CPM",
                    "key": "CPM"
                },
                {
                    "key": "lclick",
                    "name": "lclick",
                    "collapsed": False,
                    "groups": [],
                    "metrics": [
                        "lclick_cost_d",
                        "lclick_zC*cost",
                        "lclick_zC",
                    ],
                }
            ],
            "metrics": [
                {
                    "name": "lclick_cost_d",
                    "hname": "cost_d",
                },
                {
                    "name": "lclick_zC*cost",
                    "hname": "zC*cost",
                },
                {
                    "name": "lclick_zC",
                    "hname": "zC",
                },
            ]
        }
    }


class TestCPC(object):
    def test_parse_cpc_result_small(self):
        cpc_result = zc.parse_cpc_result("""
                #|
                ||version|date|method|slice|bid_type|jeltok|belok|yayka|group_count||
                ||4|20210903-20210903|BIDS_RATIO_1|ab410899|insanity|0|1|2|11111||
                ||4|20210903-20210903|BIDS_RATIO_1|ab410906|insanity|2|3|4|22222||
                ||4|20210903-20210903|BIDS_RATIO_1|ab410899|madness|5|6|7|33333||
                ||4|20210903-20210903|BIDS_RATIO_1|ab410906|madness|8|9|9|44444||
                |#
        """)
        true_cpc_result = {
            "insanity": {
                "jeltok": {"410906": {"val": "2"}, "410899": {"val": "0"}},
                "belok": {"410906": {"val": "3"}, "410899": {"val": "1"}},
                "yayka": {"410906": {"val": "4"}, "410899": {"val": "2"}},
            },
            "madness": {
                "jeltok": {"410906": {"val": "8"}, "410899": {"val": "5"}},
                "belok": {"410906": {"val": "9"}, "410899": {"val": "6"}},
                "yayka": {"410906": {"val": "9"}, "410899": {"val": "7"}},
            }
        }

        assert cpc_result == true_cpc_result

    def test_parse_cpc_result(self):
        cpc_result = zc.parse_cpc_result(get_test_cpc_output())
        true_cpc_result = {
            "CappedBid": {
                "upper": {"410906": {"val": "1.01996588946"}, "410899": {"val": "1.00772298843"}},
                "lower": {"410906": {"val": "0.990485053696"}, "410899": {"val": "0.983114441627"}},
                "avg": {"410906": {"val": "1.00602654393"}, "410899": {"val": "0.995642180466"}}},
            "Cost": {
                "upper": {"410906": {"val": "1.02014031592"}, "410899": {"val": "1.00850533078"}},
                "lower": {"410906": {"val": "0.994650857432"}, "410899": {"val": "0.982244692592"}},
                "avg": {"410906": {"val": "1.00677715029"}, "410899": {"val": "0.995245339485"}}},
            "NormedBid": {
                "upper": {"410906": {"val": "1.01962403489"}, "410899": {"val": "1.00599132481"}},
                "lower": {"410906": {"val": "0.995837230779"}, "410899": {"val": "0.983646333826"}},
                "avg": {"410906": {"val": "1.00657448179"}, "410899": {"val": "0.994613981097"}}}
        }

        assert cpc_result == true_cpc_result


class TestCPM(object):
    def test_parse_cpm_result_small(self):
        cpm_result = zc.parse_cpm_result("""
            #|
            || **experiment** | **action** | ** metric - 1 ** | **metric - 2** ||
            || 410899 | LLLLL | 1.0260 +/- 0.0500 | **!!(pink_floyd)-8888.8 +/- 1.4371!!** ||
            || 410906 | LLLLL | 1.0022 +/- 0.0506 | **!!(pink_floyd)-99.9999 +/- 1.4250!!** ||
            |#
        """)

        true_cpm_result = {
            "LLLLL": {
                "metric-2": {
                    "410906": {"color": "pink_floyd", "val": "-99.9999"},
                    "410899": {"color": "pink_floyd", "val": "-8888.8"}},
                "metric-1": {
                    "410906": {"val": "1.0022"},
                    "410899": {"val": "1.0260"}
                }
            }
        }
        assert cpm_result == true_cpm_result

    def test_parse_cpm_result(self):
        cpm_result = zc.parse_cpm_result(get_test_cpm_output())
        true_cpm_result = {
            "lclick": {
                "cost_d": {
                    "410906": {"color": "red", "val": "-87.4772"},
                    "410899": {"color": "red", "val": "-87.4670"}},
                "zC*cost": {
                    "410906": {"color": "red", "val": "-87.4503"},
                    "410899": {"color": "red", "val": "-87.1412"}},
                "zC": {
                    "410906": {"val": "1.0022"},
                    "410899": {"val": "1.0260"}
                }
            }
        }
        assert cpm_result == true_cpm_result

    def test_parse_cpm_v2_result(self):
        cpm_v2_result = zc.parse_cpm_result(get_test_cpm_v2_output())
        true_cpm_v2_result = {
            "lclick": {
                "zC": {
                    "535217": {"color": "green", "val": "1.0221"},
                    "535221": {"color": "green", "val": "1.0536"},
                    "535223": {"color": "green", "val": "1.0788"}},
                "NormalizedzC": {
                    "535217": {"val": "1.0000"},
                    "535221": {"color": "green", "val": "1.0308"},
                    "535223": {"color": "green", "val": "1.0555"}},
            }
        }
        assert cpm_v2_result == true_cpm_v2_result


class TestZC(object):
    def test_build_zc_result_cpc(self):
        true_cpc_zc_result = get_true_test_zc_result_cpc()

        cpc_result = zc.parse_cpc_result(get_test_cpc_output())

        zc_result = get_empty_zc_result(["410899", "410906"], "20210903", "20210903")
        zc.add_group_to_zc_result(cpc_result, "CPC", zc_result)

        assert zc_result == true_cpc_zc_result

    def test_build_zc_result_cpm(self):
        true_cpm_zc_result = get_true_test_zc_result_cpm()

        cpm_result = zc.parse_cpm_result(get_test_cpm_output())

        zc_result = get_empty_zc_result(["410899", "410906"], "20210903", "20210903")
        zc.add_group_to_zc_result(cpm_result, "CPM", zc_result)

        assert zc_result == true_cpm_zc_result

    def test_build_zc_result(self):
        true_zc_result = get_true_test_zc_result()

        cpc_result = zc.parse_cpc_result(get_test_cpc_output())
        cpm_result = zc.parse_cpm_result(get_test_cpm_output())

        zc_result = get_empty_zc_result(["410899", "410906"], "20210903", "20210903")
        zc.add_group_to_zc_result(cpc_result, "CPC", zc_result)
        zc.add_group_to_zc_result(cpm_result, "CPM", zc_result)
        assert zc_result == true_zc_result

    def test_build_zc_result_with_errors(self):
        true_error_zc_result = get_true_error_test_zc_result()

        cpm_result = zc.parse_cpm_result(get_test_cpm_output())

        zc_result = get_empty_zc_result(["410899", "410906"], "20210903", "20210903")
        zc.add_group_to_zc_result({}, "CPC", zc_result)
        zc.add_empty_metric_to_the_last_group("FAILED", zc_result)
        zc.add_group_to_zc_result(cpm_result, "CPM", zc_result)
        assert zc_result == true_error_zc_result
