import logging
import re

from collections import defaultdict


def parse_cpc_result(output):
    """
    Args:
        output (str): output of cpc calculation

    Returns:
        dict: result

        result format: look group_result dict in add_group_to_zc_result
    """
    logging.info("Parse CPC result to JSON")

    def get_columns(table_row):
        """
        Args:
            table_row (str): "||col_1|col_2|col_3||"

        Returns:
            list[str]: ["col_1", "col_2", "col_3"]
        """
        return table_row.strip(" |").split("|")

    # output has table: #| <table> |#
    table_begin = output.find("#|") + 3
    table_end = output.rfind("|#") - 1
    table = output[table_begin:table_end].split("\n")
    result = defaultdict(lambda: defaultdict(dict))

    head = get_columns(table[0])
    for row in table[1:]:
        columns = get_columns(row)

        if len(columns) < 7:
            continue

        exp_id = re.search(r'\d+', columns[3]).group(0)
        bid_type = columns[4]

        metric_col_begin = 5
        metric_col_end = len(head) - 1
        for i in range(metric_col_begin, metric_col_end):
            result[bid_type][head[i]][exp_id] = {"val": columns[i]}

    return result


def parse_cpm_result(output):
    """
    Args:
        output (str): output of cpc calculation

    Returns:
        dict: result

        result format: look group_result dict in add_group_to_zc_result
    """
    logging.info("Parse CPM result to JSON")

    def get_columns(table_row):
        """
        Args:
            table_row (str): "|| !!** col_1 **!! | col_2 | ** col_3_a +/- col_3_b ||
        Returns:
            str: ["col_1", "col_2", "col_3_a+/-col_3_b"]
        """
        return [col.strip(" *!").replace(" ", "") for col in table_row.strip(" |").split("|")]

    def get_value_dict(element):
        """
        Args:
            element (str): "(red)1235.12+/-67.89"

        Returns:
            dict: {"val": 1235.12, "delta_val": 67.89, "color": red}
        """
        color = None

        color_begin = element.find("(")
        if color_begin != -1:
            color_end = element.find(")")
            color = element[color_begin + 1:color_end]
            element = element[color_end + 1:]

        value = element.split("+/-")[0]

        value_dict = {
            "val": value,
            # "diffprec1": delta_value
        }
        if color is not None:
            value_dict["color"] = color

        return value_dict

    # output has table: #| <table> |#
    table_begin = output.find("#|") + 3
    table_end = output.rfind("|#") - 1
    table = output[table_begin:table_end].split("\n")
    result = defaultdict(lambda: defaultdict(dict))

    head = get_columns(table[0])

    for row in table[1:]:
        columns = get_columns(row)

        if len(columns) < 2:
            continue

        exp_id = columns[0].strip(" *")
        action = columns[1].strip(" *")

        metric_col_begin = 2
        metric_col_end = len(head)
        for i in range(metric_col_begin, metric_col_end):
            result[action][head[i]][exp_id] = get_value_dict(columns[i])

    return result


def get_default_empty_zc_result():
    return {
        "task": {
            "metrics": [],
            "user": "leftmain",
            "granularity": "24"
        },
        "data": {
            "metrics": {},
        },
        "meta": {
            "group_nodes": [
                {
                    "key": "root",
                    "name": None,
                    "collapsed": False,
                    "groups": [],
                    "metrics": []
                }
            ],
            "metrics": []
        }
    }


def add_group_to_zc_result(group_result, group_name, zc_result):
    """
    Args:
        group_result (dict[str, any]): result of cpc/cpm calculation
        group_name (str): name of group
        zc_result (dict[str, any]): look zc_result initialization in _get_subtasks_results

        group_result = {
            group_name_1: {
                metric_1 { test_id_1: {"val": val1}, test_id_2: {"val": val2} },
                metric_2 { test_id_1: {"val": val3}, test_id_2: {"val": val4} }
            },
            group_name_2: {...}
        }

    Returns:
        None
    """
    zc_result["meta"]["group_nodes"][0]["groups"].append(group_name)

    group_node = {
        "key": group_name,
        "name": group_name,
        "groups": [],
        "collapsed": False,
        "metrics": []
    }
    group_list = [group_node]

    for metric_group, metric_values in group_result.items():
        group_node["groups"].append(metric_group)
        local_group = {
            "key": metric_group,
            "name": metric_group,
            "groups": [],
            "collapsed": False,
            "metrics": []
        }

        for value_name, value_dict in metric_values.items():
            metric_name = metric_group + "_" + value_name

            local_group["metrics"].append(metric_name)

            zc_result["task"]["metrics"].append(metric_name)
            zc_result["data"]["metrics"][metric_name] = []
            zc_result["meta"]["metrics"].append({
                "name": metric_name,
                "hname": value_name,
            })

            for testid in zc_result["task"]["testids"]:
                zc_result["data"]["metrics"][metric_name].append(value_dict[testid])

        group_list.append(local_group)

    zc_result["meta"]["group_nodes"] += group_list


def add_empty_metric_to_the_last_group(metric_name, zc_result):
    """
    Args:
        metric_name (str): name of group
        zc_result (dict[str, any]): look zc_result initialization in _get_subtasks_results

    Returns:
        None
    """
    zc_result["task"]["metrics"].append(metric_name)
    zc_result["meta"]["group_nodes"][-1]["metrics"].append(metric_name)
    zc_result["meta"]["metrics"].append({
        "name": metric_name,
        "hname": metric_name,
    })
    zc_result["data"]["metrics"][metric_name] = [
        {} for _ in range(len(zc_result["task"]["testids"]))
    ]
