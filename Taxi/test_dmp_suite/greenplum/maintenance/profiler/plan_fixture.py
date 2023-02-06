PLAN_RESULT_DICT = {
    "Plan": {
        "Node Type": "Gather Motion",
        "Senders": 128,
        "Receivers": 1,
        "Slice": 2,
        "Segments": 128,
        "Gang Type": "primary reader",
        "Startup Cost": 0.00,
        "Total Cost": 2247.71,
        "Plan Rows": 633,
        "Plan Width": 42,
        "operatorMem": 100,
        "Actual Startup Time": 6521.505,
        "Actual Total Time": 6524.858,
        "Actual Rows": 1016,
        "Actual Loops": 1,
        "Output": ["object_meta.object_schema_name", "(count((count(DISTINCT object_meta.gp_oid))))", "(count((count())))"],
        "Plans": [
            {
                "Node Type": "Aggregate",
                "Strategy": "Hashed",
                "Parent Relationship": "Outer",
                "Slice": 2,
                "Segments": 128,
                "Gang Type": "primary reader",
                "Startup Cost": 0.00,
                "Total Cost": 2247.65,
                "Plan Rows": 633,
                "Plan Width": 42,
                "operatorMem": 5394,
                "Actual Startup Time": 6509.372,
                "Actual Total Time": 6509.407,
                "Actual Rows": 16,
                "Actual Loops": 1,
                "Output": ["object_meta.object_schema_name", "count((count(DISTINCT object_meta.gp_oid)))", "count((count()))"],
                "Group Key": ["object_meta.object_schema_name"],
                "Executor Memory": 11198,
                "Executor Memory Segments": 128,
                "Executor Max Memory": 89,
                "Executor Max Memory Segment": 0,
                "Extra Text": [
                    {
                        "Extra Text": "(seg89)  Hash chain length 1.2 avg, 3 max, using 13 of 32 buckets; total 0 expansions.\n"
                    }
                ],
                "Plans": [
                    {
                        "Node Type": "Redistribute Motion",
                        "Senders": 128,
                        "Receivers": 128,
                        "Parent Relationship": "Outer",
                        "Slice": 1,
                        "Segments": 128,
                        "Gang Type": "primary reader",
                        "Startup Cost": 0.00,
                        "Total Cost": 2247.65,
                        "Plan Rows": 633,
                        "Plan Width": 42,
                        "operatorMem": 100,
                        "Actual Startup Time": 5509.217,
                        "Actual Total Time": 6508.483,
                        "Actual Rows": 781,
                        "Actual Loops": 1,
                        "Output": ["object_meta.object_schema_name", "(count(DISTINCT object_meta.gp_oid))", "(count())"],
                        "Hash Key": "object_meta.object_schema_name",
                        "Plans": [
                            {
                                "Node Type": "Result",
                                "Parent Relationship": "Outer",
                                "Slice": 1,
                                "Segments": 128,
                                "Gang Type": "primary reader",
                                "Startup Cost": 0.00,
                                "Total Cost": 2247.65,
                                "Plan Rows": 633,
                                "Plan Width": 42,
                                "operatorMem": 100,
                                "Actual Startup Time": 5975.171,
                                "Actual Total Time": 6195.876,
                                "Actual Rows": 276,
                                "Actual Loops": 1,
                                "Output": ["object_meta.object_schema_name", "(count(DISTINCT object_meta.gp_oid))", "(count())"],
                                "Plans": [
                                    {
                                        "Node Type": "Aggregate",
                                        "Strategy": "Sorted",
                                        "Parent Relationship": "Outer",
                                        "Slice": 1,
                                        "Segments": 128,
                                        "Gang Type": "primary reader",
                                        "Startup Cost": 0.00,
                                        "Total Cost": 2247.65,
                                        "Plan Rows": 633,
                                        "Plan Width": 42,
                                        "operatorMem": 5394,
                                        "Actual Startup Time": 5975.170,
                                        "Actual Total Time": 6195.815,
                                        "Actual Rows": 276,
                                        "Actual Loops": 1,
                                        "Output": ["count(DISTINCT object_meta.gp_oid)", "count()", "object_meta.object_schema_name"],
                                        "Group Key": ["object_meta.object_schema_name"],
                                        "Executor Memory": 1590748,
                                        "Executor Memory Segments": 128,
                                        "Executor Max Memory": 13501,
                                        "Executor Max Memory Segment": 45,
                                        "work_mem": {
                                            "Used": 50182,
                                            "Segments": 128,
                                            "Max Memory": 393,
                                            "Max Memory Segment": 0
                                        },
                                        "Plans": [
                                            {
                                                "Node Type": "Sort",
                                                "Parent Relationship": "Outer",
                                                "Slice": 1,
                                                "Segments": 128,
                                                "Gang Type": "primary reader",
                                                "Startup Cost": 0.00,
                                                "Total Cost": 2235.25,
                                                "Plan Rows": 52882875,
                                                "Plan Width": 30,
                                                "operatorMem": 5394,
                                                "Actual Startup Time": 5948.041,
                                                "Actual Total Time": 6118.114,
                                                "Actual Rows": 233579,
                                                "Actual Loops": 1,
                                                "Output": ["object_meta.object_schema_name", "object_meta.gp_oid"],
                                                "Sort Key": ["object_meta.object_schema_name"],
                                                "Sort Method": "external merge",
                                                "Sort Space Used": 1094944,
                                                "Sort Space Type": "Disk",
                                                "Sort Max Segment Memory": 9184,
                                                "Sort Avg Segment Memory": 8554,
                                                "Sort Segments": 128,
                                                "Executor Memory": 1247533,
                                                "Executor Memory Segments": 128,
                                                "Executor Max Memory": 9747,
                                                "Executor Max Memory Segment": 0,
                                                "work_mem": {
                                                    "Used": 1247533,
                                                    "Segments": 128,
                                                    "Max Memory": 9747,
                                                    "Max Memory Segment": 0,
                                                    "Workfile Spilling": 128,
                                                    "Max Memory Wanted": 22611,
                                                    "Max Memory Wanted Segment": 60,
                                                    "Avg Memory Wanted": 21027,
                                                    "Segments Affected": 128
                                                },
                                                "Plans": [
                                                    {
                                                        "Node Type": "Hash Join",
                                                        "Parent Relationship": "Outer",
                                                        "Slice": 1,
                                                        "Segments": 128,
                                                        "Gang Type": "primary reader",
                                                        "Join Type": "Inner",
                                                        "Startup Cost": 0.00,
                                                        "Total Cost": 924.16,
                                                        "Plan Rows": 52882875,
                                                        "Plan Width": 30,
                                                        "operatorMem": 100,
                                                        "Actual Startup Time": 2515.104,
                                                        "Actual Total Time": 4335.514,
                                                        "Actual Rows": 233579,
                                                        "Actual Loops": 1,
                                                        "Output": ["object_meta.object_schema_name", "object_meta.gp_oid"],
                                                        "Hash Cond": "(object_meta.gp_oid = object_meta_1.gp_oid)",
                                                        "Executor Memory": 54648,
                                                        "Executor Memory Segments": 128,
                                                        "Executor Max Memory": 459,
                                                        "Executor Max Memory Segment": 60,
                                                        "work_mem": {
                                                            "Used": 54648,
                                                            "Segments": 128,
                                                            "Max Memory": 459,
                                                            "Max Memory Segment": 60,
                                                            "Workfile Spilling": 0
                                                        },
                                                        "Extra Text": [
                                                            {
                                                                "Extra Text": "(seg60)  Hash chain length 12.1 avg, 24 max, using 1612 of 32768 buckets."
                                                            }
                                                        ],
                                                        "Plans": [
                                                            {
                                                                "Node Type": "Seq Scan",
                                                                "Parent Relationship": "Outer",
                                                                "Slice": 1,
                                                                "Segments": 128,
                                                                "Gang Type": "primary reader",
                                                                "Relation Name": "object_meta",
                                                                "Schema": "gpdb",
                                                                "Alias": "object_meta",
                                                                "Startup Cost": 0.00,
                                                                "Total Cost": 434.34,
                                                                "Plan Rows": 3470206,
                                                                "Plan Width": 30,
                                                                "operatorMem": 100,
                                                                "Actual Startup Time": 351.639,
                                                                "Actual Total Time": 2114.557,
                                                                "Actual Rows": 19579,
                                                                "Actual Loops": 1,
                                                                "Output": ["object_meta.object_schema_name", "object_meta.gp_oid"]
                                                            },
                                                            {
                                                                "Node Type": "Hash",
                                                                "Parent Relationship": "Inner",
                                                                "Slice": 1,
                                                                "Segments": 128,
                                                                "Gang Type": "primary reader",
                                                                "Startup Cost": 434.34,
                                                                "Total Cost": 434.34,
                                                                "Plan Rows": 3470206,
                                                                "Plan Width": 4,
                                                                "operatorMem": 8092,
                                                                "Actual Startup Time": 2163.230,
                                                                "Actual Total Time": 2163.230,
                                                                "Actual Rows": 19579,
                                                                "Actual Loops": 1,
                                                                "Output": ["object_meta_1.gp_oid"],
                                                                "Plans": [
                                                                    {
                                                                        "Node Type": "Seq Scan",
                                                                        "Parent Relationship": "Outer",
                                                                        "Slice": 1,
                                                                        "Segments": 128,
                                                                        "Gang Type": "primary reader",
                                                                        "Relation Name": "object_meta",
                                                                        "Schema": "gpdb",
                                                                        "Alias": "object_meta_1",
                                                                        "Startup Cost": 0.00,
                                                                        "Total Cost": 434.34,
                                                                        "Plan Rows": 3470206,
                                                                        "Plan Width": 4,
                                                                        "operatorMem": 100,
                                                                        "Actual Startup Time": 347.206,
                                                                        "Actual Total Time": 2159.438,
                                                                        "Actual Rows": 19579,
                                                                        "Actual Loops": 1,
                                                                        "Output": ["object_meta_1.gp_oid"]
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "Planning Time": 36.390,
    "Triggers": [
    ],
    "Slice statistics": [
        {
            "Slice": 0,
            "Executor Memory": 308352
        },
        {
            "Slice": 1,
            "Executor Memory": {
                "Average": 24110025,
                "Workers": 128,
                "Maximum Memory Used": 25208984
            },
            "Work Maximum Memory": 9980264
        },
        {
            "Slice": 2,
            "Executor Memory": {
                "Average": 170479,
                "Workers": 128,
                "Maximum Memory Used": 171056
            }
        }
    ],
    "Statement statistics": {
        "Memory used": 16384,
        "Memory wanted": 91040
    },
    "Settings": {
        "Optimizer": "Pivotal Optimizer (GPORCA)"
    },
    "Execution Time": 6573.675
}