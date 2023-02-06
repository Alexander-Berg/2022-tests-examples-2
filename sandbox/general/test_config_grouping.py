import json

import config_grouping

_TEST_DIFFS = [
    "test_diff_list1.json",
    "test_diff_list2.json",
    "test_diff_list3.json",
    "test_diff_list4.json",
]


if __name__ == "__main__":
    for diff_name in _TEST_DIFFS:
        diff_list = json.loads(open(diff_name).read())

        def name_formatter(config_name):
            return config_name.replace(".json.simplified.html", "")

        table = config_grouping.generate_table(diff_list, name_formatter)

    # print json.dumps(table, indent=4)
