import datetime

import pytest


@pytest.fixture
def rfid_labels_services_good(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
                {
                    'carnumber': 'ХЕ27477',
                    'tagbarcode': '5M-101001',
                    'codecompany': '181',
                    'dataidentifier': '01001',
                    'epc': '4E2019DA81F4800000000000',
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
                {
                    'carnumber': 'КУ71777',
                    'tagbarcode': '5M-101062',
                    'codecompany': '181',
                    'dataidentifier': '01062',
                    'epc': '4E2019DA8213400000000000',
                    'tid': 'E20034120139F80006D060DD0321013370055FFBFFFFDC50',
                    'tagtype': 'TTF',
                    'rfid': '84b4ee0c-75d1-4a95-a4e3-2eec53c8b168',
                    'period': '2017-02-18T10:52:00',
                    'status': 'inactive',
                },
                {
                    'carnumber': 'КУ71777',
                    'tagbarcode': '5M-101166',
                    'codecompany': '181',
                    'dataidentifier': '01166',
                    'epc': '4E2019DA8247400000000000',
                    'tid': 'E20034120171FA0001323B1F28040167300559FBFFFFDC70',
                    'tagtype': 'CWL E-100',
                    'rfid': 'e94a8434-1d43-46ed-897c-dfc70f77216d',
                    'period': '2017-03-31T19:19:01',
                    'status': 'active',
                },
            ],
        }

    return context


def test_cxx_jobs_test_simple_run(taxi_jobs, rfid_labels_services_good, db):
    taxi_jobs.run('rfid_labels', '--without-wrapper', '-t0')
    docs = db.distlock.find({'_id': 'taxi_maintenance.rfid_labels'})
    assert docs.count() == 1


def test_cxx_jobs_test_run_twice(taxi_jobs, db, rfid_labels_services_good):
    taxi_jobs.run('rfid_labels', '--without-wrapper', '-t0')
    docs = db.distlock.find({'_id': 'taxi_maintenance.rfid_labels'})
    assert docs.count() == 1

    taxi_jobs.run('rfid_labels', '--without-wrapper', '-t0')
    docs = db.distlock.find({'_id': 'taxi_maintenance.rfid_labels'})
    assert docs.count() == 1


@pytest.mark.now('2017-07-04T11:00:00+0300')
def test_cxx_jobs_statistic(taxi_jobs, rfid_labels_services_good, db):
    taxi_jobs.run('rfid_labels', '--without-wrapper', '-t0')
    doc = db.cron_tasks.find_one(
        {'start_time': {'$gte': datetime.datetime(2017, 7, 4, 8, 0)}},
    )
    assert doc['status'] == 'finished'


@pytest.fixture
def rfid_labels_services_bad(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return mockserver.make_response('', 500)


@pytest.mark.now('2017-07-04T11:00:00+0300')
def test_cxx_jobs_statistic_exception(taxi_jobs, rfid_labels_services_bad, db):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels', '--without-wrapper', '-t0')

    doc = db.cron_tasks.find_one(
        {'start_time': {'$gte': datetime.datetime(2017, 7, 4, 8, 0)}},
    )
    assert doc['status'] == 'exception'


def test_cxx_jobs_test_legacy_run(taxi_jobs, rfid_labels_services_good, db):
    taxi_jobs.run('rfid_labels')
    docs = db.distlock.find({'_id': 'taxi_maintenance.rfid_labels'})
    assert docs.count() == 0


def test_cxx_jobs_geoareas_request(taxi_jobs, mock_geoareas, mockserver):
    @mockserver.json_handler('/tracker/1.0/positions')
    def mock_tracker(request):
        return mockserver.make_response('', 500)

    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('drivers_geo_fencing', '--without-wrapper')

    # check if geoareas are successfully retrieved
    assert mock_geoareas.times_called == 1
    assert mock_tracker.times_called > 0
