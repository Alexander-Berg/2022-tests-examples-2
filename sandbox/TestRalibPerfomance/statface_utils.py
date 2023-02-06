import datetime
import json
import requests

STATFACE_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
BRANCH_DATETIME_FORMAT = "%Y-%m-%d"

MAIN_GRAPH_NAME = 'Adhoc/Adhoc/gavrgavr/RALib_perfomance'


def get_dates_sent_earlier(task, sorted_branches_dates_strs):
    dates = []

    url = "https://stat.yandex-team.ru/{}?scale=d&date_min={}&date_max={}&_type=json".format(MAIN_GRAPH_NAME, sorted_branches_dates_strs[0], sorted_branches_dates_strs[-1])
    result = requests.get(url, headers={'Authorization': 'OAuth {}'.format(task.GetStafaceToken())})
    if result.status_code != 200:
        raise Exception(("Later relaunch by pressing 'Run'-button might help, if this is temporary problem. Problem: "
                         "GET-request with url {url} failed. It is equal to {status_code}".format(url=url, status_code=result.status_code)))

    points_dicts_array = result.json()['values']
    for point_dict_array in points_dicts_array:
        statface_date_str = point_dict_array['fielddate']
        datetime_dt = datetime.datetime.strptime(statface_date_str, STATFACE_DATETIME_FORMAT)
        branch_date_str = datetime.datetime.strftime(datetime_dt, BRANCH_DATETIME_FORMAT)
        dates.append(branch_date_str)

    return dates


def do_send(task, statface_json):
    resp = requests.post(
        'https://upload.stat.yandex-team.ru/_api/report/data',
        headers={'Authorization': 'OAuth {}'.format(task.GetStafaceToken())},
        data=statface_json,
    )

    if resp.status_code != 200:
        dumped_json = json.dumps(statface_json)
        raise Exception(("Later relaunch by pressing 'Run'-button might help, if this is temporary problem. Problem: "
                         "POST-request with json {dumped_json} failed. It is equal to {status_code}".format(dumped_json=dumped_json, status_code=resp.status_code)))


def send_new_vals_to_statface(task, our_branch_to_launch_index_to_result_str_json, branch_date_to_input_uncomressed_terabytes_size, is_release_machine, date_for_graph):
    import json
    if not is_release_machine:
        dates = get_dates_sent_earlier(task, task.ctx["our_branches"])
    data = []
    for our_branch, launch_idx_to_result_str_json in our_branch_to_launch_index_to_result_str_json.iteritems():
        if not is_release_machine:
            if our_branch in dates:
                raise Exception("The date {} has been already send to statface earlier!".format(our_branch))
        datetime_dt = None
        if is_release_machine and date_for_graph:
            datetime_dt = datetime.datetime.strptime(date_for_graph, BRANCH_DATETIME_FORMAT)
        else:
            datetime_dt = datetime.datetime.strptime(our_branch, BRANCH_DATETIME_FORMAT)
        data_item = {'fielddate': datetime.datetime.strftime(datetime_dt, STATFACE_DATETIME_FORMAT)}
        result_str_json = launch_idx_to_result_str_json[0]
        result = json.loads(result_str_json)
        data_item["cpu_hours"] = result["cpu"]["seconds"] * float(100) / float(3600)
        data_item["cpu_hours_per_tb"] = data_item["cpu_hours"] / (float(branch_date_to_input_uncomressed_terabytes_size[our_branch]) * float(100))
        data_item["ram_max_gb"] = result["ram"]["max_bytes"] / float(1024 ** 3)

        data_item["big_users_cpu_miliseconds_per_mb_95percentile"] = result["cpu"]["0.95"] * 1000
        data_item["big_users_cpu_miliseconds_per_mb_90percentile"] = result["cpu"]["0.9"] * 1000
        data_item["big_users_cpu_miliseconds_per_mb_85percentile"] = result["cpu"]["0.85"] * 1000

        data_item["big_users_ram_per_byte_95percentile"] = result["ram"]["0.95"]
        data_item["big_users_ram_per_byte_90percentile"] = result["ram"]["0.9"]
        data_item["big_users_ram_per_byte_85percentile"] = result["ram"]["0.85"]

        data.append(data_item)

    statface_json = {
        'name': MAIN_GRAPH_NAME,
        'scale': 'd',
        'data': json.dumps({'values': data}),
    }

    do_send(task, statface_json)
