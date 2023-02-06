import datetime
import logging
import urllib2
import re
import json

from pickle import load, dump
from os.path import getmtime, isfile

from collections import namedtuple


def get_test_results(tests, metric):
    test_results = dict()
    for test in tests:
        test_cache_path = _get_cache_path(test, metric)
        if not _is_cache_alive(test_cache_path):
            logging.info("Cache for %s not found", test)
            return _download_test_results(tests, metric)
        logging.info("Load from disk %s", test)
        with open(test_cache_path, "rb") as cache_file:
            test_results[test] = load(cache_file)
    return test_results


RevisionData = namedtuple('RevisionData', ['switched_res_id', 'value', 'value_before_switching'])


def get_values_and_resources(points, extract_task_value=None):
    data = dict()
    for point in points:
        new_res = None
        comment = point.get("comment")
        if comment is not None:
            match = re.match(r'new resources:\<br\>\<a.*?\>\s*(\d+)\s*\<\/a\>', comment)
            if match is None:
                raise RuntimeError("Cannot extract resource id from comment: %s" % comment)

            try:
                fc = point["marker"]["fillColor"]
            except KeyError:
                raise RuntimeError(
                    "Cannot extract marker.fillColor from resource switching point:\n%s" %
                    json.dumps(point, indent=4)
                )
            new_res = int(match.group(1))
            if fc == 'pink':
                logging.info("Skipping failed switching to resource %s", new_res)
                continue
            if fc != "palegreen":
                raise RuntimeError(
                    "Cannot handle unknown fillColor %s of resource switching point:\n%s" %
                    (fc, json.dumps(point, indent=4))
                )

        maybe_rev = point.get('revision')
        value = point.get('y')

        if value is None and extract_task_value is not None:
            task_id = point.get('task_id')
            if task_id is not None:
                value = extract_task_value(task_id)

        if maybe_rev is not None and value is not None:
            rev = int(maybe_rev)
            old_value = data[rev].value if int(rev) in data else None
            data[rev] = RevisionData(
                switched_res_id=new_res,
                value=value,
                value_before_switching=old_value,
            )
        elif comment is not None:
            raise RuntimeError(
                "Cannot handle success resourse switching without revision or metric value:\n%s" %
                json.dumps(point)
            )
    return __patch_values_and_resource(data)


_BASE_URL = "https://testenv.yandex-team.ru/handlers/systemInfo"
_GET_PARAMS_TEMPLATE = "?database={database}&screen_name=job_chart&screen_params=yabs-2.0&screen_params={test}"
_PERFORMANCE_PLOTTER_CACHE_PATH = "./"
_CACHE_TTL = datetime.timedelta(minutes=20)
_DATABASE = "yabs-2.0"


def _get_cache_path(test, metric):
    return "".join([
        _PERFORMANCE_PLOTTER_CACHE_PATH, test,
        "_", metric, ".cache"
    ])


def _is_cache_alive(test_cache_path):
    if not isfile(test_cache_path):
        return False

    now_time = datetime.datetime.now()
    mtime = datetime.datetime.fromtimestamp(getmtime(test_cache_path))
    return mtime > now_time - _CACHE_TTL


def _download_test_results(tests, metric):
    test_results = dict()
    for test in tests:
        url = _BASE_URL + _GET_PARAMS_TEMPLATE.format(test=test, database=_DATABASE)
        logging.info("Downloading data from %s", url)
        response = urllib2.urlopen(url).read()
        response_json = json.loads(response)

        lines = response_json['screen_data']['chart']['lines']
        for line in lines:
            if line['name'] == metric:
                test_results[test] = line['points']

                test_cache_path = _get_cache_path(test, metric)
                logging.info("Dump %s to disk path: %s", test, test_cache_path)
                with open(test_cache_path, "wb") as cache_file:
                    dump(test_results[test], cache_file)
    return test_results


def __patch_values_and_resource(data):
    INTERVALS_TO_SKIP = [
        (3040122, 3067666, True),
        (3200462, 3202210, True),   # See BSSERVER-4093
        (3326086, 3326227, True),
        (3359505, 3359507, True),  # Dirty resource switch
        (3402948, 3409658, True),
        (3414822, 3420671, True),
        (3430229, 3432642, True),
        (3452614, 3452908, True),
        (3667380, 3667382, True),  # genocide turn on
        (3680302, 3680304, True),  # static rank turn on
        (3885004, 3886278, True),
        (4270247, 4275238, True),  # testenv bug
        (5137276, 5137283, True),  # switching performance to sdk2 tasks
    ]

    skip_begin_iter = iter(sorted(INTERVALS_TO_SKIP))

    skip_begin, skip_end, add_switch = skip_begin_iter.next()

    patched_data = {}

    last_rev_before_skip = None

    for rev in sorted(data):
        if skip_begin is None or rev < skip_begin:
            patched_data[rev] = data[rev]
            last_rev_before_skip = rev
            continue

        if rev < skip_end:
            continue

        patched_data[rev] = data[rev]
        if add_switch and last_rev_before_skip:
            _, new_val, _ = data[rev]

            res, val, old_val = data[last_rev_before_skip]
            patched_data[last_rev_before_skip] = ((res or 0) + 0.5, new_val, old_val or val)
        try:
            skip_begin, skip_end, add_switch = skip_begin_iter.next()
        except StopIteration:
            skip_begin = None

    return patched_data
