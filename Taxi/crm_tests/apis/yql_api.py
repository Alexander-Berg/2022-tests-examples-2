import allure
import datetime
import json
import time

crm_admin = '//home/taxi/testing/features/crm-admin'


def path_to_logs(api_type):
    if api_type == 'unstable':
        logs = {'Driver': f"{crm_admin}/experiments/drivers/unstable/experiments",
                'User': f"{crm_admin}/experiments/unstable/experiments",
                'EatsUser': f"{crm_admin}/experiments/eda/unstable/experiments",
                'LavkaUser': f"{crm_admin}/experiments/lavka/unstable/experiments",
                'Geo': f"{crm_admin}/experiments/geo/unstable/experiments"}
    elif api_type == 'testing':
        logs = {'Driver': f"{crm_admin}/experiments/drivers/test/experiments",
                'User': f"{crm_admin}/experiments/test/experiments",
                'EatsUser': f"{crm_admin}/experiments/eda/test/experiments",
                'LavkaUser': f"{crm_admin}/experiments/lavka/test/experiments",
                'Geo': f"{crm_admin}/experiments/geo/test/experiments"}

    return logs


def yql_campaign_log(yql_url, yql_session, api_type, campaign_id, group_names, group_channels, resolution):
    yql_api = YqlApi(yql_url, yql_session)
    query = f'use hahn;' \
            f'\n$campaign_log_path = "{crm_admin}/robot-crm-efficiency/{api_type}/campaign_log";' \
            f'\ninsert into $campaign_log_path' \
            f'\n(campaign_id, group_name, channel_type, resolution)' \
            f'\nVALUES'
    for i, group_name in enumerate(group_names):
        query += f'\n("{campaign_id}", "{group_name}", "{group_channels[i]}", {resolution}),'

    query = query[:-1] + f';\nCOMMIT;'

    yql_api.yql_request(query)


def yql_add_extra_data(yql_url, yql_session, api_type, campaign_id, column_name, new_column):
    yql_api = YqlApi(yql_url, yql_session)

    str_id = f'{campaign_id}'

    # тут надо узнать текущие значения для колонки column_name в сегменте. пока ручки нет
    # пока вместо этого yql запрос в таблицу с сегментом
    column_value = yql_select_distinct(yql_url, yql_session, api_type, campaign_id, column_name)

    query = f'use hahn;' \
            f'\n$extra_data = "{crm_admin}/segments/{api_type}/cmp_{str_id}_extra_data";' \
            f'\ninsert into $extra_data' \
            f'\n({column_name}, {new_column})' \
            f'\nVALUES'
    for i in range(len(column_value)):
        # доработать, чтобы передавать список параметром в метод. пока список значений доп параметра генерится тут
        query += f'\n("{column_value[i]}", "{new_column}{i}")'
        if i != len(column_value) - 1:
            query += f','
        else:
            query += f';'

    query += f'\nCOMMIT;'

    operation_id = yql_api.yql_request(query)
    return yql_api.yql_response(operation_id)


def yql_select_distinct(yql_url, yql_session, api_type, campaign_id, column, column_value=[]):
    # возвращает уникальные значения столбца из сегмента кампании
    yql_api = YqlApi(yql_url, yql_session)
    query = f'use hahn;' \
            f'\n$segment = "{crm_admin}/segments/{api_type}/cmp_{campaign_id}_seg";' \
            f'\nselect distinct {column} from  $segment'
    operation_id = yql_api.yql_request(query)
    response = yql_api.yql_response(operation_id)
    assert column == response.json()['data'][0]['Write'][0]['Type'][1][1][0][0]

    column_len = len(response.json()['data'][0]['Write'][0]['Data'])

    for i in range(column_len):
        column_value.insert(i, response.json()['data'][0]['Write'][0]['Data'][i][0][0])

    return column_value


def is_table_exist(yql_url, yql_session, table_name):
    # проверяю существование таблицы, скорее всего можно проще
    # можно передавать весь путь до таблицы и хранить его в конфигах, если пригодится для других таблиц
    yql_api = YqlApi(yql_url, yql_session)
    query = f'use hahn;' \
            f'\n$table = "//{table_name}";' \
            f'\nselect * from $table'

    operation_id = yql_api.yql_request(query)
    response = yql_api.yql_response(operation_id)
    if response.json()['errors']:
        if "does not exist" in response.json()['errors'][3]['message']:
            return False
        else:
            # TODO подумать какая еще может быть другая ошибка
            return False
    else:
        return True


def count_comms_segments_to_send(yql_url, yql_session, campaign_id, groups_id, table_name):
    yql_api = YqlApi(yql_url, yql_session)
    query = f'use hahn;' \
            f'\n$table = "//{table_name}";' \
            f'\nselect count(*) from $table' \
            f'\nwhere campaign_id="{campaign_id}" and ('
    for group_id in groups_id:
        query += f'\ngroup_id_id = {group_id} or'
    query = query.rpartition(' ')[0] + f')'

    operation_id = yql_api.yql_request(query)
    response = yql_api.yql_response(operation_id)
    return response.json()['data'][0]['Write'][0]['Data'][0][0]


def wait_for_table(yql_url, yql_session, table_name, n=20, timeout=60):
    result = 0
    total_secs = n * timeout
    while not result and n >= 0:
        time.sleep(timeout)
        n -= 1
        result = is_table_exist(yql_url, yql_session, table_name)
    if n < 0:
        raise TimeoutError(f"There is no table that you are waiting for. Waited for {total_secs} seconds.")
    return result


def find_table(yql_url, yql_session, now_time, folder, table_name=''):
    # возвращает список таблиц сформированых позже указанного времени

    now_yql_datetime = now_time.strftime('%Y-%m-%dT%H:%M:%SZ')

    query = f'use hahn;' \
            f'\n$parse1 = DateTime::Parse("%Y-%m-%dT%H:%M:%SZ");' \
            f'\n$now = DateTime::MakeDatetime($parse1("{now_yql_datetime}"));' \
            f'\nSELECT Path, DateTime::MakeDatetime($parse1(Yson::ConvertToString(Attributes.creation_time))) as creation_time' \
            f'\nFROM FOLDER("{folder}", "creation_time")' \
            f'\nWHERE DateTime::MakeDatetime($parse1(Yson::ConvertToString(Attributes.creation_time))) > $now' \
            f'\nAND Path like "%{table_name}%"' \
            f'\nORDER by creation_time'

    response = yql_select(yql_url, yql_session, query, column_value=[])
    return response


def yql_select(yql_url, yql_session, query, column_value=[]):
    yql_api = YqlApi(yql_url, yql_session)
    operation_id = yql_api.yql_request(query)
    response = yql_api.yql_response(operation_id)
    rows = response.json()['data'][0]['Write'][0]['Data']

    for row in rows:
        column_value.append(row)

    return column_value


def segments_to_send_with_comms(yql_url, yql_session, api_type, campaign_id, groups_id, now_time_next):
    table_name = "segments_to_send_input"
    # список path таблиц сформированных позже now_time
    tmp = 0
    # этот while очень не нравится, но пока не придумала, что сделать
    while True:
        now_time = now_time_next
        # во втором цикле и дальше не будем просматривать таблицы, которые уже смотрели
        now_time_next = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=10)

        time.sleep(180)
        # список таблиц
        folder = f"{crm_admin}/robot-crm-efficiency/{api_type}"
        list_found_table_name = find_table(yql_url, yql_session, now_time, folder, table_name)
        tmp += 1
        print(f'количество попыток найти нужную таблицу segments_to_send_first = {tmp}')
        if list_found_table_name:
            for found_table_name in list_found_table_name:
                # попали ли коммуникации из кампании/группы в таблицу
                count_comms = count_comms_segments_to_send(yql_url, yql_session, campaign_id, groups_id,
                                                           found_table_name[0])
                if count_comms != '0':
                    return [found_table_name[0], count_comms]
        if tmp > 15:
            raise TimeoutError(f"There is no table that you are looking for. Number of attempts: {tmp}.")


def comms_in_logs_experiments(yql_url, yql_session, ticket_id, table, audience, group_num):
    grp_id = str(group_num) + '_test'
    if audience == 'Driver':
        query = f'use hahn;' \
                f'\n$table = "//{table}";' \
                f'\nSELECT group_id, grp_id, count(*) as cnt' \
                f'\nFROM $table' \
                f'\nWHERE experiment_id = "{ticket_id}" and grp_id = "{grp_id}"' \
                f'\ngroup  by group_id, Yson::ConvertToString(properties[\'group_id\']) as grp_id;'

    elif audience == 'User':
        query = f'PRAGMA yson.DisableStrict;' \
                f'use hahn;' \
                f'\n$table = "//{table}";' \
                f'\nSELECT group_id, grp_id, count(*) as cnt' \
                f'\nFROM $table' \
                f'\nWHERE experiment_id = "{ticket_id}" and grp_id = "{grp_id}"' \
                f'\ngroup  by group_id, DictLookup(properties, \'group_id\') as grp_id'

    elif audience == 'LavkaUser':
        query = f'use hahn;' \
                f'\n$table = "//{table}";' \
                f'\nSELECT group_id, grp_id, count(*) as cnt' \
                f'\nFROM $table' \
                f'\nWHERE experiment_id = "{ticket_id}" and grp_id = "{grp_id}"' \
                f'\ngroup  by group_id, Yson::ConvertToString(properties[\'group_id\']) as grp_id;'

    elif audience == 'Geo':
        query = f'PRAGMA yson.DisableStrict;' \
                f'use hahn;' \
                f'\n$table = "//{table}";' \
                f'\nSELECT group_id, grp_id, count(*) as cnt' \
                f'\nFROM $table' \
                f'\nWHERE experiment_id = "{ticket_id}" and grp_id = "{grp_id}"' \
                f'\ngroup by group_id, Yson::ConvertToString(properties[\'group_id\']) as grp_id'

    else:
        query = f'PRAGMA yson.DisableStrict;' \
                f'use hahn;' \
                f'\n$table = "//{table}";' \
                f'\nSELECT group_id, grp_id, count(*) as cnt' \
                f'\nFROM $table' \
                f'\nWHERE issue_id = "{ticket_id}" and grp_id = "{grp_id}"' \
                f'\ngroup  by group_id, DictLookup(properties, \'group_id\') as grp_id'

    response = yql_select(yql_url, yql_session, query, column_value=[])
    return response


class YqlApi:
    # OAUTH_TOKEN_YQL = os.environ['YQL_TOKEN']

    def __init__(self, yql_url, yql_session):
        self.yql_url = yql_url
        self.yql_session = yql_session

    def yql_request(self, query):
        body = {
            "content": query,
            "action": "RUN",
            "type": "SQLv1"
        }

        r1 = self.yql_session.post(self.yql_url, data=json.dumps(body))

        dic1 = json.loads(r1.text)

        time.sleep(30)

        print(dic1['id'])

        return dic1['id']

    def yql_response(self, operation_id):
        tries = 10
        sum = 0
        response = self.yql_session.get(self.yql_url + operation_id + '/' + "results", params={"filters": "DATA"})
        for i in range(1, tries):
            res_status = response.json()['status']
            if res_status == 'ERROR':
                response_info = f'''
                        Request URL: {response.url}
                        Request Body: {response.request.body}
                        Response code: {response.status_code}
                        Response body: {response.text}
                        '''
                allure.attach(body=response_info, name="Response log", attachment_type=allure.attachment_type.TEXT)
                assert res_status != 'ERROR', f"Запрос YQL {operation_id} обработался с ошибкой"
            if res_status == "RUNNING":
                time.sleep(i * 10)
                sum += i * 10
                print(f"ждем ответа на запрос YQL {operation_id} уже {sum} секунд")
                response = self.yql_session.get(self.yql_url + operation_id + '/' + "results",
                                                params={"filters": "DATA"})
            elif res_status == "COMPLETED":
                break

        assert response.json()['status'] != 'RUNNING', f"Запрос YQL {operation_id} обрабатывается слишком долго"
        return response
