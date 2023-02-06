import os
import datetime


# считаем до какого времени бронируем девайс
def reservation_time(duration):
    current_date = datetime.datetime.now()
    future_date = current_date + datetime.timedelta(hours=duration)
    print("Current date: %s " % current_date)
    print("Future date: %s " % future_date)
    return round(future_date.timestamp() * 1000)


# Забронировать свободное устройство на основе фильтров
def occupy_some_device(kolhoz_token, device_id, duration):
    occupy_options = {
        'devicesCount': 1,
        'toTs': reservation_time(duration)
    }
    device_filter = {
        'deviceIds': device_id
    }
    return http_post_request(
        kolhoz_token,
        "https://kolhoz.yandex-team.ru/api/public/v1/devices/occupy",
        {'filter': device_filter, 'options': occupy_options}).json()


def get_host_ip_for_connect():
    all_ip = os.popen('hostname --all-ip-addresses')
    return all_ip.read().strip().split(' ')


# Включить удаленный доступ к устройству
def enable_remote_connect(kolhoz_token, device_id):
    return http_post_request(kolhoz_token,
                             'https://kolhoz.yandex-team.ru/api/public/v1/devices/' + device_id + '/connect',
                             {"allowedClients": get_host_ip_for_connect()}).json()


# Отмена бронирования устройств
def release_device(kolhoz_token, device_id):
    http_post_request(kolhoz_token, 'https://kolhoz.yandex-team.ru/api/public/v1/devices/' + device_id + '/release')
    if os.path.exists('deviceId.txt'):
        os.remove('deviceId.txt')


def http_post_request(kolhoz_token, url_value, json=None):
    import requests
    headers = {
        'Authorization': f'OAuth {kolhoz_token}',
        'Content-Type': 'application/json',
    }
    request_log = 'POST %s' % url_value
    request_log2 = 'JSON %s' % json
    print('\n' + request_log)
    print(request_log2 + '\n')
    response = requests.post(url=url_value, headers=headers, json=json)
    if response.status_code == 200:
        print(response.text)
        return response
    else:
        print(response.json())
        raise Exception("Unexpected status-code [%s] during http-request: [%s]" % (response.status_code, request_log))


def print_output(name, output_value):
    stdout_str = str(output_value)
    if output_value is not None and len(stdout_str.strip()) > 0:
        print('%s:\n-------\n%s\n-------' % (name, stdout_str))
    return stdout_str


def get_device_host_with_port(kolhoz_token, device_id):
    remote_connect_settings = enable_remote_connect(kolhoz_token, device_id)
    if remote_connect_settings['enabled']:
        device_serial = remote_connect_settings['hostname'] + ':' + str(remote_connect_settings['port'])
        print('Remote connect successfully enabled on device: %s' % device_id)
        print('\nDevice serial: %s' % device_serial)
        return device_serial
    else:
        raise Exception("enabled = false, after enableRemoteConnect(%s)" % device_id)


def connect_device(kolhoz_token, device_id, duration_of_occupy_in_hours):
    occupy_res = occupy_some_device(kolhoz_token, device_id, duration_of_occupy_in_hours)
    if len(occupy_res['results']) > 0:
        adb_device_id = occupy_res['results'][0]['device']['id']
        model_name = occupy_res['results'][0]['device']['modelName']
        print("Device successfully occupied: %s / %s " % (model_name, adb_device_id))
        return adb_device_id
    else:
        raise Exception("no devices after occupy-request")


def occupy_device(kolhoz_token, device_id, duration_of_occupy_in_hours):
    adb_device_id = connect_device(kolhoz_token, device_id, duration_of_occupy_in_hours)
    device_serial = get_device_host_with_port(kolhoz_token, adb_device_id)
    return device_serial
