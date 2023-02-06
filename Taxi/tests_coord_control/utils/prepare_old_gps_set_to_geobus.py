import datetime as dt
import json

# Table with logs
# https://yt.yandex-team.ru/hahn/navigation
# ?path=//home/taxi-analytics/olyagnilova/spoofing_examples/spoofing_raw_data
# type = json lines
# columns = [driverId, list-lon, list-lat, list-provider, timestamp_]
SOURCE_MAP = {
    'gps': 'AndroidGps',
    'network': 'AndroidNetwork',
    'fused': 'AndroidFused',
    'passive': 'AndroidPassive',
    'lbs-wifi': 'YandexLbsWifi',
    'lbs-gsm': 'YandexLbsGsm',
    'lbs-ip': 'YandexLbsIp',
}


def make_signal_v2(
        driver_id: str, lon: float, lat: float, source: str, timestamp: int,
) -> dict:
    return {
        'accuracy': 0,
        'altitude': 0,
        'direction': 0,
        'driver_id': driver_id,
        'position': [lon, lat],
        'source': source,
        'speed': 0,
        'unix_time': timestamp,
    }


def ts_to_datetime(ts_ms: int) -> dt.datetime:
    timestamp = int(str(ts_ms)[:-3])
    return dt.datetime.utcfromtimestamp(timestamp)


def str_to_ts(ts_str: str) -> int:
    return (
        int(dt.datetime.strptime(ts_str, '%Y-%m-%d %H:%M:%S').timestamp())
        * 1000
    )


def main(file_name: str):
    signals = []
    sources = set()
    with open(file_name, 'r') as file:
        for line in file:
            json_line = json.loads(line)

            coords = zip(
                json_line['list_lon'].split(','),
                json_line['list_lat'].split(','),
                json_line['list_provider'].split(','),
            )

            for coord in coords:
                sources.add(coord[2])
                signals.append(
                    make_signal_v2(
                        'dbid_' + json_line['driverId'],
                        float(coord[0]),
                        float(coord[1]),
                        SOURCE_MAP[coord[2]],
                        str_to_ts(json_line['timestamp_']),
                    ),
                )

    signals.sort(key=lambda x: x['unix_time'])
    print('Found sources: ', sources)
    print('Made signals: ', len(signals))
    print(
        f'Signals from '
        f'{ts_to_datetime(signals[0]["unix_time"])}'
        f' to {ts_to_datetime(signals[-1]["unix_time"])}',
    )

    with open(
            f'../static/test_gps_jump_by_history/geobus_{file_name}', 'w',
    ) as file:
        json.dump(signals, file)


if __name__ == '__main__':
    main('spoofing_raw_data.json')
