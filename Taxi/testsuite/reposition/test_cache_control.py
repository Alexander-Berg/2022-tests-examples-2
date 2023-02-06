import datetime
import os
import shutil
import time

import flatbuffers
import pytest

from fbs.Yandex.Taxi.Reposition.EtagsCache import Etag
from fbs.Yandex.Taxi.Reposition.EtagsCache import EtagsCache
from fbs.Yandex.Taxi.Reposition.EtagsCache import EtagSince
from fbs.Yandex.Taxi.Reposition.EtagsCache import EtagSinceList


STATE_ETAGS_CACHE_DUMP_FILENAME = 'cache_etags_states_dump.bin'
MODES_ETAGS_CACHE_DUMP_FILENAME = 'cache_etags_modes_dump.bin'
OFFERED_MODES_ETAGS_CACHE_DUMP_FILENAME = 'cache_etags_offered_modes_dump.bin'

REPOSITION_ETAGS_CACHE_STATE_REFERENCE = {
    'driver_id_ids': [2, 8, 9],
    'etag_sinces': [
        {
            'list': [
                {'etag': {'revision': 1}, 'since': 1543269600000},
                {'etag': {'revision': 2}, 'since': 1543352400000},
                {'etag': {'revision': 3}, 'since': 1543784400000},
            ],
        },
        {
            'list': [
                {'etag': {'revision': 4}, 'since': 1543269600000},
                {'etag': {'revision': 5}, 'since': 1543276800000},
                {'etag': {'revision': 6}, 'since': 1543795200000},
            ],
        },
        {
            'list': [
                {'etag': {'revision': 7}, 'since': 1543269600000},
                {'etag': {'revision': 8}, 'since': 1543276800000},
                {'etag': {'revision': 9}, 'since': 1543795200000},
            ],
        },
    ],
    'revision': 9,
}

REPOSITION_ETAGS_CACHE_MODES_REFERENCE = {
    'driver_id_ids': [2, 8, 9],
    'etag_sinces': [
        {
            'list': [
                {'etag': {'revision': 1}, 'since': 1543269600000},
                {'etag': {'revision': 2}, 'since': 1543536000000},
            ],
        },
        {'list': [{'etag': {'revision': 3}, 'since': 1543269600000}]},
        {'list': [{'etag': {'revision': 4}, 'since': 1543269600000}]},
    ],
    'revision': 4,
}

REPOSITION_ETAGS_CACHE_OFFERED_MODES_REFERENCE = {
    'driver_id_ids': [2, 8, 9],
    'etag_sinces': [
        {'list': [{'etag': {'revision': 1}, 'since': 1543269600000}]},
        {'list': [{'etag': {'revision': 2}, 'since': 1543269600000}]},
        {'list': [{'etag': {'revision': 3}, 'since': 1543269600000}]},
    ],
    'revision': 3,
}


def clear_cache(cache_dump_dir):
    shutil.rmtree(cache_dump_dir, True)


def read_cache(cache_dump_file):
    with open(cache_dump_file, 'rb') as fl:
        data_fbs = fl.read()
        return data_fbs
    return None


def write_cache(cache_dump_file, data_fbs, date=None):
    os.makedirs(os.path.dirname(cache_dump_file), exist_ok=True)
    with open(cache_dump_file, 'wb') as fl:
        fl.write(data_fbs)
    if date:
        modified_time = time.mktime(date.timetuple())
        os.utime(cache_dump_file, (modified_time, modified_time))


def exist_cache(cache_dump_file):
    return os.path.isfile(cache_dump_file)


def modified_cache(cache_dump_file):
    modified_time = os.path.getmtime(cache_dump_file)
    return datetime.datetime.fromtimestamp(modified_time)


def wait_for_dump(cache_dump_file, date_after=None, timeout=20, sleep=1):
    end = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
    while datetime.datetime.now() < end:
        if exist_cache(cache_dump_file) and (
                date_after is None
                or modified_cache(cache_dump_file) > date_after
        ):
            return
        time.sleep(sleep)
    raise TimeoutError()


def build_etags_cache_fbs(data):
    builder = flatbuffers.Builder(0)

    assert len(data['driver_id_ids']) == len(data['etag_sinces'])

    etag_sinces = []

    for idx in range(len(data['driver_id_ids'])):
        etag_since_list = data['etag_sinces'][idx]

        fbs_list = []

        for kdx in range(len(etag_since_list['list'])):
            etag_since = etag_since_list['list'][kdx]

            etag = etag_since['etag']

            Etag.EtagStart(builder)
            Etag.EtagAddRevision(builder, etag['revision'])
            fbs_etag = Etag.EtagEnd(builder)

            EtagSince.EtagSinceStart(builder)
            EtagSince.EtagSinceAddEtag(builder, fbs_etag)
            EtagSince.EtagSinceAddSince(builder, etag_since['since'])
            fbs_etag_since = EtagSince.EtagSinceEnd(builder)

            fbs_list.append(fbs_etag_since)

        EtagSinceList.EtagSinceListStartListVector(builder, len(fbs_list))
        for fbs_etag_since in reversed(fbs_list):
            builder.PrependUOffsetTRelative(fbs_etag_since)
        fbs_etag_since_list = builder.EndVector(len(fbs_list))

        EtagSinceList.EtagSinceListStart(builder)
        EtagSinceList.EtagSinceListAddList(builder, fbs_etag_since_list)
        fbs_etag_since_list_obj = EtagSinceList.EtagSinceListEnd(builder)

        etag_sinces.append(fbs_etag_since_list_obj)

    EtagsCache.EtagsCacheStartDriverIdIdsVector(
        builder, len(data['driver_id_ids']),
    )
    for driver_id_id in reversed(data['driver_id_ids']):
        builder.PrependInt32(driver_id_id)
    fbs_driver_id_ids = builder.EndVector(len(data['driver_id_ids']))

    EtagsCache.EtagsCacheStartEtagSincesVector(builder, len(etag_sinces))
    for fbs_etag_since in reversed(etag_sinces):
        builder.PrependUOffsetTRelative(fbs_etag_since)
    fbs_etag_sinces = builder.EndVector(len(etag_sinces))

    EtagsCache.EtagsCacheStart(builder)
    EtagsCache.EtagsCacheAddRevision(builder, data['revision'])
    EtagsCache.EtagsCacheAddDriverIdIds(builder, fbs_driver_id_ids)
    EtagsCache.EtagsCacheAddEtagSinces(builder, fbs_etag_sinces)
    data_fbs = EtagsCache.EtagsCacheEnd(builder)

    builder.Finish(data_fbs)
    return builder.Output()


def parse_etags_cache_fbs(data_fbs):
    response = EtagsCache.EtagsCache.GetRootAsEtagsCache(data_fbs, 0)

    data = {
        'revision': response.Revision(),
        'driver_id_ids': [],
        'etag_sinces': [],
    }

    assert response.DriverIdIdsLength() == response.EtagSincesLength()

    for idx in range(response.DriverIdIdsLength()):
        data['driver_id_ids'].append(response.DriverIdIds(idx))
        driver_etag_sinces = response.EtagSinces(idx)

        etag_since_list = {'list': []}

        for jdx in range(driver_etag_sinces.ListLength()):
            etag_since = driver_etag_sinces.List(jdx)

            etag = etag_since.Etag()
            since = etag_since.Since()

            etag_since = {
                'etag': {'revision': etag.Revision()},
                'since': since,
            }

            etag_since_list['list'].append(etag_since)

        data['etag_sinces'].append(etag_since_list)

    sorted_data_content = sorted(
        zip(data['driver_id_ids'], data['etag_sinces']),
    )
    data['driver_id_ids'] = [e for e, _ in sorted_data_content]
    data['etag_sinces'] = [e for _, e in sorted_data_content]

    return data


@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'sample_etags_data.sql'],
)
def test_etags_cache_dump(taxi_reposition, etags_cache_path, config):
    STATE_DUMP = etags_cache_path + '/' + STATE_ETAGS_CACHE_DUMP_FILENAME
    MODES_DUMP = etags_cache_path + '/' + MODES_ETAGS_CACHE_DUMP_FILENAME
    OFFERED_MODES_DUMP = (
        etags_cache_path + '/' + OFFERED_MODES_ETAGS_CACHE_DUMP_FILENAME
    )

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200

    clear_cache(etags_cache_path)
    config.set_values(
        dict(
            REPOSITION_ETAGS_CACHES_DUMP_RESTORE_SETTINGS={
                'enabled': True,
                'dump_ttl': 300,
                'dump_interval': 5,
            },
        ),
    )

    now = datetime.datetime.now()

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200

    wait_for_dump(STATE_DUMP, now)
    wait_for_dump(MODES_DUMP, now)
    wait_for_dump(OFFERED_MODES_DUMP, now)

    data_fbs = read_cache(STATE_DUMP)
    data = parse_etags_cache_fbs(data_fbs)
    assert data == REPOSITION_ETAGS_CACHE_STATE_REFERENCE

    data_fbs = read_cache(MODES_DUMP)
    data = parse_etags_cache_fbs(data_fbs)
    assert data == REPOSITION_ETAGS_CACHE_MODES_REFERENCE

    data_fbs = read_cache(OFFERED_MODES_DUMP)
    data = parse_etags_cache_fbs(data_fbs)
    assert data == REPOSITION_ETAGS_CACHE_OFFERED_MODES_REFERENCE

    clear_cache(etags_cache_path)


@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'sample_etags_data.sql'],
)
def test_etags_cache_restore(taxi_reposition, etags_cache_path, config):
    STATE_DUMP = etags_cache_path + '/' + STATE_ETAGS_CACHE_DUMP_FILENAME
    MODES_DUMP = etags_cache_path + '/' + MODES_ETAGS_CACHE_DUMP_FILENAME
    OFFERED_MODES_DUMP = (
        etags_cache_path + '/' + OFFERED_MODES_ETAGS_CACHE_DUMP_FILENAME
    )

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200

    data = {
        'driver_id_ids': [2, 8],
        'etag_sinces': [
            {
                'list': [
                    {'etag': {'revision': 1}, 'since': 1543269600000},
                    {'etag': {'revision': 2}, 'since': 1543352400000},
                    {'etag': {'revision': 3}, 'since': 1543784400000},
                ],
            },
            {
                'list': [
                    {'etag': {'revision': 4}, 'since': 1543269600000},
                    {'etag': {'revision': 5}, 'since': 1543276800000},
                    {'etag': {'revision': 6}, 'since': 1543795200000},
                ],
            },
        ],
        'revision': 6,
    }

    fbs_data = build_etags_cache_fbs(data)
    write_cache(STATE_DUMP, fbs_data)

    data = {
        'driver_id_ids': [2, 8],
        'etag_sinces': [
            {
                'list': [
                    {'etag': {'revision': 1}, 'since': 1543269600000},
                    {'etag': {'revision': 2}, 'since': 1543536000000},
                ],
            },
            {'list': [{'etag': {'revision': 3}, 'since': 1543269600000}]},
        ],
        'revision': 3,
    }

    fbs_data = build_etags_cache_fbs(data)
    write_cache(MODES_DUMP, fbs_data)

    data = {
        'driver_id_ids': [2, 8],
        'etag_sinces': [
            {'list': [{'etag': {'revision': 1}, 'since': 1543269600000}]},
            {'list': [{'etag': {'revision': 2}, 'since': 1543269600000}]},
        ],
        'revision': 2,
    }

    fbs_data = build_etags_cache_fbs(data)
    write_cache(OFFERED_MODES_DUMP, fbs_data)

    config.set_values(
        dict(
            REPOSITION_ETAGS_CACHES_DUMP_RESTORE_SETTINGS={
                'enabled': True,
                'dump_ttl': 300,
                'dump_interval': 5,
            },
        ),
    )

    now = datetime.datetime.now()

    response = taxi_reposition.post(
        'tests/control', {'invalidate_caches': True},
    )
    assert response.status_code == 200

    wait_for_dump(STATE_DUMP, now)
    wait_for_dump(MODES_DUMP, now)
    wait_for_dump(OFFERED_MODES_DUMP, now)

    data_fbs = read_cache(STATE_DUMP)
    data = parse_etags_cache_fbs(data_fbs)
    assert data == REPOSITION_ETAGS_CACHE_STATE_REFERENCE

    data_fbs = read_cache(MODES_DUMP)
    data = parse_etags_cache_fbs(data_fbs)
    assert data == REPOSITION_ETAGS_CACHE_MODES_REFERENCE

    data_fbs = read_cache(OFFERED_MODES_DUMP)
    data = parse_etags_cache_fbs(data_fbs)
    assert data == REPOSITION_ETAGS_CACHE_OFFERED_MODES_REFERENCE

    clear_cache(etags_cache_path)
