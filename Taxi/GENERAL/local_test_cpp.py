# coding=utf-8
from __future__ import print_function

import argparse
import copy
import os
import json
import datetime

from nile.api.v1 import (
    clusters,
    files as nfl,
)
from zoo.utils import (
    time_helpers,
    geo
)
from zoo.utils.nile_helpers.ml_yt_path import MlDevPath
from zoo.suggest.v3.rec_factory_cpp import RecFactory

# hahn folders
HAHN_PATH = '//home/taxi_ml/dev/suggest/exp_offers_max_quality'
HAHN_CITIES_PATH = '//home/taxi-dwh/stg/mdb/cities/cities'
# date settings
OFFERS_DAYS_OF_MEMORY = 1
DEFAULT_OFFERS_TTL_SEC = 1800
# resources names
CITIES_PATH = 'cities'
# quality values
MIN_RELEVANCE = -1000
TARGET_RADIUS = 10


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(THIS_DIR, 'config.json')


def get_config():
    with open(CONFIG_PATH, mode='r') as f:
        data = json.load(f)
    return data


def has_hit_for_offers(offers_history, last_route):
    true_dst = last_route.get('destinations')
    if not true_dst:
        return False
    true_dst_lon = true_dst.get('lon')
    true_dst_lat = true_dst.get('lat')
    lons, lats = [], []
    for offer in offers_history:
        lons.append(offer['destinations']['lon'])
        lats.append(offer['destinations']['lat'])
    dists = geo.earth_distance(true_dst_lon, true_dst_lat, lons, lats)
    return bool((dists < TARGET_RADIUS).any())


def main(args):
    today_str = args.today.strftime('%Y-%m-%d')
    config = get_config()
    config['train_config']['working_dir'] = '/'.join((HAHN_PATH, today_str))

    get_path = MlDevPath('suggest', 'exp_offers_max_quality/{}'.format(today_str))

    cluster = clusters.yt.Hahn()

    config['candidates_extractor_config']['use_completion_point'] = True
    rec_factory = RecFactory(
        config, is_compare_exact=True, target_max_distance=TARGET_RADIUS,
        cb_path=args.cb_file_name, cities_path=CITIES_PATH,
        use_completion_point_as_target=True
    )
    model = rec_factory.create_rec_model()

    records = cluster.read(get_path('offers_test'))

    for i in range(100):
        print("Working on i =", i)
        r = records[i]
        last_route = r.last_route
        candidates = []
        curr_dest = r.last_route.get('destinations')
        if curr_dest and curr_dest.get('lon') and curr_dest.get('lat') and r.routes_info:
            # print(r)
            candidates = model(r)
        print(candidates)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--today',
        type=time_helpers.argparse_date_tuple,
        required=True,
    )
    parser.add_argument(
        '--cb_file_name',
        type=str,
        required=False,
    )
    main(parser.parse_args())
