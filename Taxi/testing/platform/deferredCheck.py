import time
import requests
import json

CHECK_URL = 'http://logistic-platform.taxi.tst.yandex.net/platform/requests/deferred/check?dump=eventlog'


def get_start_of_day_utc():
    current_ts = int(time.time())
    return current_ts - current_ts % (24 * 60 * 60)


PAYLOAD = {
    "time_intervals": [
        {
            "input_intervals": [
                {"from": get_start_of_day_utc() + 86400 + 36000, "to": get_start_of_day_utc() + 86400 + 50400}
            ],
            "output_intervals": [
                {"from": get_start_of_day_utc() + 86400 + 43200, "to": get_start_of_day_utc() + 86400 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 2 + 43200, "to": get_start_of_day_utc() + 86400 * 2 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 3 + 43200, "to": get_start_of_day_utc() + 86400 * 3 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 4 + 43200, "to": get_start_of_day_utc() + 86400 * 4 + 59400},
            ],
        },
        {
            "input_intervals": [
                {"from": get_start_of_day_utc() + 86400 * 2 + 36000, "to": get_start_of_day_utc() + 86400 * 2 + 50400}
            ],
            "output_intervals": [
                {"from": get_start_of_day_utc() + 86400 * 2 + 43200, "to": get_start_of_day_utc() + 86400 * 2 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 3 + 43200, "to": get_start_of_day_utc() + 86400 * 3 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 4 + 43200, "to": get_start_of_day_utc() + 86400 * 4 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 5 + 43200, "to": get_start_of_day_utc() + 86400 * 5 + 59400},
            ],
        },
        {
            "input_intervals": [
                {"from": get_start_of_day_utc() + 86400 * 3 + 36000, "to": get_start_of_day_utc() + 86400 * 3 + 50400}
            ],
            "output_intervals": [
                {"from": get_start_of_day_utc() + 86400 * 3 + 43200, "to": get_start_of_day_utc() + 86400 * 3 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 4 + 43200, "to": get_start_of_day_utc() + 86400 * 4 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 5 + 43200, "to": get_start_of_day_utc() + 86400 * 5 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 6 + 43200, "to": get_start_of_day_utc() + 86400 * 6 + 59400},
            ],
        },
        {
            "input_intervals": [
                {"from": get_start_of_day_utc() + 86400 * 4 + 36000, "to": get_start_of_day_utc() + 86400 * 4 + 50400}
            ],
            "output_intervals": [
                {"from": get_start_of_day_utc() + 86400 * 4 + 43200, "to": get_start_of_day_utc() + 86400 * 4 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 5 + 43200, "to": get_start_of_day_utc() + 86400 * 5 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 6 + 43200, "to": get_start_of_day_utc() + 86400 * 6 + 59400},
                {"from": get_start_of_day_utc() + 86400 * 7 + 43200, "to": get_start_of_day_utc() + 86400 * 7 + 59400},
            ],
        },
    ],
    "resource_features": [
        {
            "class_name": "physical",
            "resource_physical_feature": {"weight": 1000, "d_x": 11, "d_y": 22, "d_z": 33, "rotatable": True},
        }
    ],
    "coord": {"lat": 55.737116478776905, "lon": 37.652103599572555},
}


if __name__ == '__main__':
    for _ in range(100000):
        r = requests.post(
            CHECK_URL,
            headers={
                'Authorization': 'beru',
            },
            json=PAYLOAD,
        )
        if float(r.json()['__event_log'][-1]['t']) > 500.:
            print(r.elapsed)
            with open('log.json', 'w') as f:
                f.write(json.dumps(r.json(), indent=4))
            r.raise_for_status()
#            break

