from __future__ import print_function

import argparse
import json


DEFAULT_QUANTILES = ','.join(map(str, [q / 100.0 for q in [50, 75, 80, 85, 90, 95, 98, 99]]))
DEFAULT_BOOTSTRAP_ITERATIONS = 10000
DEFAULT_CONFINT_P = 0.99


def make_timings_url(shooting_id):
    """
    Generates url to get timings for a given shooting.

    Parameters
    ----------
    shooting_id : string or int
        Id of a shooting

    Returns
    -------
    Url that can be used to get timings
    """
    return 'https://lunapark.yandex-team.ru/api/job/{}/dist/times.json'.format(
        shooting_id)


def download_shooting_timings(shooting_id):
    """
    Downloads timings from a shooting.

    Parameters
    ----------
    shooting_id : string or int
        Id of a shooting

    Returns
    -------
    List of shooting timings
    """

    import requests

    result = requests.get(make_timings_url(shooting_id))
    data = json.loads(result.text)

    samples = []
    for item in data:
        value, count = item["ms"], item["count"]
        samples.extend([value] * count)
    return samples


def download_shootings_timings(shooting_ids):
    """
    Downloads timings from a shootings.

    Parameters
    ----------
    shooting_ids : list of string or int
        Ids of shootings

    Returns
    -------
    List of shooting timings
    """
    result = []
    for shooting_id in shooting_ids:
        result.extend(download_shooting_timings(shooting_id))
    return result


def confidence_interval(data, quantile, p, iterations):
    """
    Bootstraps confidence interval for a given quantile

    Parameters
    ----------
    data : list of floats
    quantile : float
        Quantile, between 0 and 1
    p : float
        Confidence interval width, between 0 and 1
    iterations : int
        Number of bootstrap iterations

    Returns
    -------
    Dict in the following form:
    {
        'left': confidence interval left bound,
        'right': confidence interval right bound,
        'center': confidence interval center
    }
    """

    import numpy as np

    q = np.quantile(data, quantile)
    deltas = []
    for iteration in xrange(iterations):
        sample = np.random.choice(a=data, size=len(data))
        deltas.append(np.quantile(a=sample, q=quantile) - q)

    lo = np.clip((1 - p) / 2.0, 0, 1)
    hi = np.clip((1 + p) / 2.0, 0, 1)
    confint = np.quantile(deltas, [lo, hi]) + q
    return {
        'left': confint[0],
        'right': confint[1],
        'center': q
    }


def confidence_intervals(lhs, rhs, quantiles, p, iterations):
    result = {}
    for q in quantiles:
        result[q] = {
            'lhs': confidence_interval(data=lhs, quantile=q, p=p, iterations=iterations),
            'rhs': confidence_interval(data=rhs, quantile=q, p=p, iterations=iterations)
        }
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--lhs',
        type=str,
        required=True,
        help='Comma-separated list of shootings')
    parser.add_argument(
        '--rhs',
        type=str,
        required=True,
        help='Comma-separated list of shootings')
    parser.add_argument(
        '--quantiles',
        type=str,
        default=DEFAULT_QUANTILES,
        help='Comma-separated list of quantiles')
    parser.add_argument(
        '--bootstrap-iterations',
        type=int,
        default=DEFAULT_BOOTSTRAP_ITERATIONS,
        help='Number of bootstrap iterations for confidence intervals building')
    parser.add_argument(
        '--confint-p',
        type=float,
        default=DEFAULT_CONFINT_P,
        help='Confidence intervals width')

    args = parser.parse_args()

    lhs = download_shootings_timings(args.lhs.split(','))
    rhs = download_shootings_timings(args.rhs.split(','))
    quantiles = map(float, args.quantiles.split(','))

    result = confidence_intervals(lhs=lhs,
                                  rhs=rhs,
                                  quantiles=quantiles,
                                  p=args.confint_p,
                                  iterations=args.bootstrap_iterations)
    print(json.dumps(result, indent=True, sort_keys=True))
