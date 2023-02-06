import argparse
import json
from functools import partial
import logging


def calc_sensors_stat(data_old, data_new):
    from scipy import stats
    import numpy as np
    from statsmodels.stats.weightstats import zconfint
    from sensors_loader import unite_sensors_keys

    def extract_stats(a):
        return {
            'trim_mean': stats.trim_mean(a, 0.05) if a.size > 0 else 'na',
            'mean': a.mean() if a.size > 0 else 'na',
            'zconfint': zconfint(a) if a.size > 0 else 'na',
            'median': np.quantile(a, 0.5) if a.size > 0 else 'na',
            'q99': np.quantile(a, 0.99) if a.size > 0 else 'na'
        }
    unite_sensors_keys(data_old, data_new)
    res = dict()
    for k in data_old:
        array_old = np.array(data_old[k]['value'])
        array_new = np.array(data_new[k]['value'])
        try:
            pvalue = stats.mannwhitneyu(array_old, array_new).pvalue

            res[k] = {
                'u_test_pvalue': pvalue,
                'stable': extract_stats(array_old),
                'test': extract_stats(array_new)
            }
        except Exception, exc:
            logging.info('Skipped {} sensor. Error message: {}'.format(k, str(exc)))
    return res


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--service', choices=['vins', 'megamind'])
    parser.add_argument('--stable-sensors-path', required=True)
    parser.add_argument('--test-sensors-path', required=True)
    parser.add_argument('--sensors-stats-path', required=True)
    args = parser.parse_args()

    import sensors_loader

    if args.service == 'vins':
        loader = partial(sensors_loader.load_data, date_parser=sensors_loader.parse_date_vins,
                         sensor_filter=sensors_loader.sensor_filter_vins,
                         name_extractor=sensors_loader.extract_name_vins)
    elif args.service == 'megamind':
        loader = partial(sensors_loader.load_data, date_parser=sensors_loader.parse_date_mm,
                         sensor_filter=sensors_loader.sensor_filter_mm, name_extractor=sensors_loader.extract_name_mm)

    res = calc_sensors_stat(loader(args.stable_sensors_path, filter_warm_up=True),
                            loader(args.test_sensors_path, filter_warm_up=True))
    with open(args.sensors_stats_path, 'wb') as f:
        json.dump(res, f)
