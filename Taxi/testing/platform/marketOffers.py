import copy
import time
import requests
import argparse
import json
import numpy as np

TM = int(time.time())
TM_DAY_START = TM - TM % 86400 + 86400
TM_DAY_SEVEN = TM_DAY_START + 7 * 3600

SOURCE = {
    "type": "market_station",
    "market_station": {
        "lms_id": 10002777824
    },
    "interval": {
        "from": TM_DAY_START,
        "to": TM_DAY_START
    }
}

DESTINATION = {
    "type": "custom_location",
    "custom_location": {
        "latitude": 55.723967,
        "longitude": 37.568408
    },
    "interval": {
        "from": 0,
        "to": 0
    }
}

PAYLOAD = {
    "item": {
        "weight": 5000,
        "dx": 100,
        "dy": 70,
        "dz": 20,
    },
    "last_mile_policy": "time_interval",
}

CREATE_URL = 'http://logistic-platform.taxi.yandex.net/api/platform/offers/check'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='market_handler_bulk')
    parser.add_argument('-r', '--requests_count', type=int, default=1)
    parser.add_argument('-e', '--eventlog', action='store_true')
    parser.add_argument('-c', '--create_offers', action='store_true')
    parser.add_argument('-t', '--timings', action='store_true')
    parser.add_argument('-d', '--days', type=int, default=5)
    parser.add_argument('-s', '--slots', type=int, default=12)
    args = parser.parse_args()

    if args.eventlog == True:
        CREATE_URL += '?dump=eventlog'
        print(CREATE_URL)
    
    payload = copy.deepcopy(PAYLOAD)
    payload["create_offers"] = args.create_offers
    
    offers = []
    for i in range(args.days):
        for j in range(args.slots):
            source = copy.deepcopy(SOURCE)
            dest = copy.deepcopy(DESTINATION)
        
            ifrom = TM_DAY_SEVEN + i * 86400 + j * 3600
            print(i, j, ifrom)
            ito = ifrom + 3600
        
            dest["interval"]["from"] = ifrom
            dest["interval"]["to"] = ito

            offer = {}
            offer["source"] = source
            offer["destination"] = dest
            offers.append(offer)
    payload["offers"] = offers

    times = []
    total_time = 0
    print(payload)
    for i in range(args.requests_count):
        time_before_request = time.time()
        r = requests.post(
            CREATE_URL,
            json=payload
        )
        time_elapsed = time.time() - time_before_request
        total_time += time_elapsed
        times.append(time_elapsed)
        times.sort()
        if (args.timings):
            print(i, ': time elapsed:', time_elapsed, '| avg: ', total_time / (i + 1))
    
    if (args.timings):
        print('TOTAL: time elapsed:', total_time, '| avg:', total_time / args.requests_count)
        print('95 percentil: ', np.percentile(times, 95))
        print('80 percentil: ', np.percentile(times, 80))
        print('50 percentil: ', np.percentile(times, 50))
    if args.eventlog == True:
        with open('eventlog', 'w+') as f:
            f.write(str(json.dumps(r.json(), sort_keys=True, indent=4)))
            print('results moved to \'eventlog\'')
            print(r.status_code, r.headers)
    else:
        print(r.status_code, r.json(), r.headers)
