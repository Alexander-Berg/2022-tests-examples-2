import datetime
import random

import pytest

from test_hiring_candidates import conftest

ROUTE = '/v1/activity-check/bulk/drivers'


@pytest.mark.usefixtures('fill_initial_data')
async def test_activity_check_bulk(taxi_hiring_candidates_web):
    def get_sample(k):
        return random.sample(driver_ids_list, k=k)

    async def make_request(data, code=200):
        params = {'consumer': 'hiring_candidates'}
        response = await taxi_hiring_candidates_web.post(
            ROUTE, json=data, params=params,
        )
        assert response.status == code
        return response

    async def make_successful_request(driver_ids, interval):
        data = {'driver_ids': driver_ids, 'interval': interval}
        resp = await make_request(data)
        response_data = await resp.json()
        response_ids = {
            doc['driver_id'] for doc in response_data['driver_ids']
        }
        for id_ in driver_ids:
            assert id_ in response_ids
        return split_by_activity(response_data)

    def split_by_activity(response_data):
        lists = ([], [])
        for doc in response_data['driver_ids']:
            lists[doc['is_active']].append(doc)
        return lists

    async def check_sample(k=30, interval=45):
        not_active, active = await make_successful_request(
            get_sample(k), interval,
        )
        assert not not_active
        assert len(active) == k

    async def check_not_active():
        driver_ids = get_sample(30)
        not_existing = [
            conftest.hex_uuid() + '_' + conftest.hex_uuid() for _ in range(10)
        ]
        driver_ids.extend(not_existing)
        not_active, active = await make_successful_request(driver_ids, 45)
        assert len(not_active) == len(not_existing)
        assert len(active) == 30

    async def check_intervals():
        id_ = get_sample(1)[0]
        driver_doc = db_drivers[id_]
        last = datetime.datetime.utcfromtimestamp(driver_doc['last_ride'])
        now = datetime.datetime.utcnow()
        diff = (now - last).days + 1
        not_active, active = await make_successful_request([id_], diff)
        assert active
        not_active, active = await make_successful_request([id_], diff - 1)
        assert not_active

    generator = conftest.ActiveDriversGenerator.get_instance()
    db_drivers = generator.drivers_dict
    driver_ids_list = list(db_drivers)
    await check_sample(30, 45)
    await check_sample(15000, 45)
    await check_not_active()
    for _ in range(10):
        await check_intervals()
