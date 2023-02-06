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
                    'last_activity': None,
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
                    'last_activity': '2017-03-31T19:19:02',
                    'status': 'active',
                },
                {
                    'carnumber': 'КУ71779',
                    'tagbarcode': '5M-101166',
                    'codecompany': '181',
                    'dataidentifier': '01166',
                    'epc': '4E2019DA8247400000000000',
                    'tid': 'E20034120171FA0001323B1F28040167300559FBFFFFDC70',
                    'tagtype': 'CWL E-100',
                    'rfid': 'e94a8434-1d43-46ed-897c-dfc70f77216d',
                    'period': '2017-03-31T19:19:01',
                    'status': 'inactive',
                },
            ],
        }

    return context


#
# Вставляем в пустую базу 3 метки (одну для одной машины,
# и две других для # второй) и убеждаемся, что они правильно легли в базу.
#
def test_rfid_labels_ok(taxi_jobs, rfid_labels_services_good, db):
    taxi_jobs.run('rfid_labels')

    entries_a = db.rfid_labels.find({'_id': 'ХЕ27477'})
    assert entries_a.count() == 1
    entry_a = entries_a[0]
    assert entry_a['_id'] == 'ХЕ27477'
    labels_a = entry_a['labels']
    assert len(labels_a) == 1
    label = labels_a[0]
    del label['updated']
    assert label['tagbarcode'] == '5M-101001'
    assert label['codecompany'] == '181'
    assert label['dataidentifier'] == '01001'
    assert label['epc'] == '4E2019DA81F4800000000000'
    assert label['tid'] == 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60'
    assert label['tagtype'] == 'TTF'
    assert label['rfid'] == '5675e700-bd8c-407f-bb67-29f17ece802b'
    assert label['status'] == 'active'
    assert label['period'] == '2017-02-14T10:00:46'
    assert label['zones'] == []
    assert 'last_activity' not in label

    entries_b = db.rfid_labels.find({'_id': 'КУ71777'})
    assert entries_b.count() == 1
    entry_b = entries_b[0]
    assert entry_b['_id'] == 'КУ71777'
    labels_b = entry_b['labels']
    assert len(labels_b) == 1
    label = labels_b[0]
    del label['updated']
    assert label['tagbarcode'] == '5M-101166'
    assert label['codecompany'] == '181'
    assert label['dataidentifier'] == '01166'
    assert label['epc'] == '4E2019DA8247400000000000'
    assert label['tid'] == 'E20034120171FA0001323B1F28040167300559FBFFFFDC70'
    assert label['tagtype'] == 'CWL E-100'
    assert label['rfid'] == 'e94a8434-1d43-46ed-897c-dfc70f77216d'
    assert label['status'] == 'active'
    assert label['period'] == '2017-03-31T19:19:01'
    assert label['last_activity'] == '2017-03-31T19:19:02'
    assert label['zones'] == []


def test_rfid_labels_invalid_argument(taxi_jobs):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('not_rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_carnumber(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
                {
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
            ],
        }

    return context


def test_rfid_labels_missing_carnumber(
        taxi_jobs, rfid_labels_services_missing_carnumber,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_carnumber(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
                {
                    'carnumber': 25560,
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
            ],
        }

    return context


def test_rfid_labels_invalid_type_carnumber(
        taxi_jobs, rfid_labels_services_invalid_type_carnumber,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_tagbarcode(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
                {
                    'carnumber': 'ХЕ27477',
                    'codecompany': '181',
                    'dataidentifier': '01001',
                    'epc': '4E2019DA81F4800000000000',
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_missing_tagbarcode(
        taxi_jobs, rfid_labels_services_missing_tagbarcode,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_tagbarcode(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
                {
                    'carnumber': 'ХЕ27477',
                    'tagbarcode': 557,
                    'codecompany': '181',
                    'dataidentifier': '01001',
                    'epc': '4E2019DA81F4800000000000',
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_invalid_type_tagbarcode(
        taxi_jobs, rfid_labels_services_invalid_type_tagbarcode,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_codecompany(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
                {
                    'carnumber': 'ХЕ27477',
                    'tagbarcode': '5M-101001',
                    'dataidentifier': '01001',
                    'epc': '4E2019DA81F4800000000000',
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_missing_codecompany(
        taxi_jobs, rfid_labels_services_missing_codecompany,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_codecompany(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
                {
                    'carnumber': 'ХЕ27477',
                    'tagbarcode': '5M-101001',
                    'codecompany': 181,
                    'dataidentifier': '01001',
                    'epc': '4E2019DA81F4800000000000',
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_invalid_type_codecompany(
        taxi_jobs, rfid_labels_services_invalid_type_codecompany,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_dataidentifier(mockserver):
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
                    'epc': '4E2019DA81F4800000000000',
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_missing_dataidentifier(
        taxi_jobs, rfid_labels_services_missing_dataidentifier,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_dataidentifier(mockserver):
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
                    'dataidentifier': 1001,
                    'epc': '4E2019DA81F4800000000000',
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_invalid_type_dataidentifier(
        taxi_jobs, rfid_labels_services_invalid_type_dataidentifier,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_epc(mockserver):
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
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_missing_epc(taxi_jobs, rfid_labels_services_missing_epc):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_epc(mockserver):
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
                    'epc': 48000001,
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_invalid_type_epc(
        taxi_jobs, rfid_labels_services_invalid_type_epc,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_tid(mockserver):
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
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_missing_tid(taxi_jobs, rfid_labels_services_missing_tid):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_tid(mockserver):
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
                    'tid': 502526,
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_invalid_type_tid(
        taxi_jobs, rfid_labels_services_invalid_type_tid,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_tagtype(mockserver):
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
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_missing_tagtype(
        taxi_jobs, rfid_labels_services_missing_tagtype,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_tagtype(mockserver):
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
                    'tagtype': 25,
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_invalid_type_tagtype(
        taxi_jobs, rfid_labels_services_invalid_type_tagtype,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_rfid(mockserver):
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
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_missing_rfid(
        taxi_jobs, rfid_labels_services_missing_rfid,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_rfid(mockserver):
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
                    'rfid': 5675,
                    'period': '2017-02-14T10:00:46',
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_invalid_type_rfid(
        taxi_jobs, rfid_labels_services_invalid_type_rfid,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_period(mockserver):
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
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_missing_period(
        taxi_jobs, rfid_labels_services_missing_period,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_period(mockserver):
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
                    'period': 2017,
                    'status': 'active',
                },
            ],
        }

    return context


def test_rfid_labels_invalid_type_period(
        taxi_jobs, rfid_labels_services_invalid_type_period,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_missing_status(mockserver):
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
                },
            ],
        }

    return context


def test_rfid_labels_missing_status(
        taxi_jobs, rfid_labels_services_missing_status,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_invalid_type_status(mockserver):
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
                    'status': 0,
                },
            ],
        }

    return context


def test_rfid_labels_invalid_type_status(
        taxi_jobs, rfid_labels_services_invalid_type_status,
):
    with pytest.raises(taxi_jobs.ExitCodeError):
        taxi_jobs.run('rfid_labels')


@pytest.fixture
def rfid_labels_services_two_labels_active(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
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
                    'status': 'active',
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


#
# Вставка двух активных меток для одного автомобиля (один и тот же гос. номер)
# - остается метка с более новым period
#
def test_rfid_labels_two_labels_active(
        taxi_jobs, rfid_labels_services_two_labels_active, db,
):
    taxi_jobs.run('rfid_labels')

    entries = db.rfid_labels.find({'_id': 'КУ71777'})
    assert entries.count() == 1
    entry = entries[0]
    assert entry['_id'] == 'КУ71777'
    labels = entry['labels']
    assert len(labels) == 1
    label = labels[0]
    assert label['tagbarcode'] == '5M-101166'
    assert label['codecompany'] == '181'
    assert label['dataidentifier'] == '01166'
    assert label['epc'] == '4E2019DA8247400000000000'
    assert label['tid'] == 'E20034120171FA0001323B1F28040167300559FBFFFFDC70'
    assert label['tagtype'] == 'CWL E-100'
    assert label['rfid'] == 'e94a8434-1d43-46ed-897c-dfc70f77216d'
    assert label['status'] == 'active'
    assert label['period'] == '2017-03-31T19:19:01'
    assert 'last_activity' not in label


@pytest.fixture
def rfid_labels_services_two_labels_active_different_order(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
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
                    'status': 'active',
                },
            ],
        }

    return context


#
# Вставка двух активных меток для одного автомобиля (один и тот же гос. номер)
# - остается метка с более новым period
#
def test_rfid_labels_two_labels_active_different_order(
        taxi_jobs, rfid_labels_services_two_labels_active_different_order, db,
):
    taxi_jobs.run('rfid_labels')

    entries = db.rfid_labels.find({'_id': 'КУ71777'})
    assert entries.count() == 1
    entry = entries[0]
    assert entry['_id'] == 'КУ71777'
    labels = entry['labels']
    assert len(labels) == 1
    label = labels[0]
    assert label['tagbarcode'] == '5M-101166'
    assert label['codecompany'] == '181'
    assert label['dataidentifier'] == '01166'
    assert label['epc'] == '4E2019DA8247400000000000'
    assert label['tid'] == 'E20034120171FA0001323B1F28040167300559FBFFFFDC70'
    assert label['tagtype'] == 'CWL E-100'
    assert label['rfid'] == 'e94a8434-1d43-46ed-897c-dfc70f77216d'
    assert label['status'] == 'active'
    assert label['period'] == '2017-03-31T19:19:01'
    assert 'last_activity' not in label


@pytest.fixture
def rfid_labels_services_good_one_a(mockserver):
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
                    'period': '2017-03-31T19:19:50',
                    'status': 'active',
                },
            ],
        }

    return context


#
# Вставка точно такой же записи - тот же номер автомобиля, все параметры те же.
# Должна только обновиться дата updated.
#
@pytest.mark.filldb(rfid_labels='one')
def test_rfid_labels_insert_existing_label(
        taxi_jobs, rfid_labels_services_good_one_a, db,
):
    taxi_jobs.run('rfid_labels')

    entries = db.rfid_labels.find({'_id': 'ХЕ27477'})
    assert entries.count() == 1
    entry = entries[0]
    assert entry['_id'] == 'ХЕ27477'
    labels = entry['labels']
    assert len(labels) == 1
    label = labels[0]
    assert label['tagbarcode'] == '5M-101001'
    assert label['codecompany'] == '181'
    assert label['dataidentifier'] == '01001'
    assert label['epc'] == '4E2019DA81F4800000000000'
    assert label['tid'] == 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60'
    assert label['tagtype'] == 'TTF'
    assert label['rfid'] == '5675e700-bd8c-407f-bb67-29f17ece802b'
    assert label['status'] == 'active'
    assert label['period'] == '2017-03-31T19:19:50'
    assert 'last_activity' not in label


@pytest.fixture
def rfid_labels_services_good_one_b(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
                {
                    'carnumber': 'ХЕ27477',
                    'tagbarcode': '5M-101001-A',
                    'codecompany': '181',
                    'dataidentifier': '01001',
                    'epc': '4E2019DA81F4800000000000',
                    'tid': 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60',
                    'tagtype': 'TTF',
                    'rfid': '5675e700-bd8c-407f-bb67-29f17ece802b',
                    'period': '2017-03-31T19:19:50',
                    'status': 'active',
                },
            ],
        }

    return context


#
# Вставка записи - тот же номер автомобиля, но другие параметры (отличается
# tagbarcode). Должна создаться новая запись, а у старая удаляться
#
@pytest.mark.filldb(rfid_labels='one')
def test_rfid_labels_insert_label_with_same_number(
        taxi_jobs, rfid_labels_services_good_one_b, db,
):
    taxi_jobs.run('rfid_labels')

    entries = db.rfid_labels.find({'_id': 'ХЕ27477'})
    assert entries.count() == 1
    entry = entries[0]
    assert entry['_id'] == 'ХЕ27477'
    labels = entry['labels']
    assert len(labels) == 1
    label = labels[0]
    assert label['tagbarcode'] == '5M-101001-A'
    assert label['codecompany'] == '181'
    assert label['dataidentifier'] == '01001'
    assert label['epc'] == '4E2019DA81F4800000000000'
    assert label['tid'] == 'E20034120133F80006D0375A0220012B70055FFBFFFFDC60'
    assert label['tagtype'] == 'TTF'
    assert label['rfid'] == '5675e700-bd8c-407f-bb67-29f17ece802b'
    assert label['status'] == 'active'
    assert label['period'] == '2017-03-31T19:19:50'
    assert 'last_activity' not in label


@pytest.fixture
def rfid_labels_services_good_one_c(mockserver):
    class context:
        uid = '123'

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {
            'RFIDs': [
                {
                    'carnumber': 'ХР76877',
                    'tagbarcode': '5M-101010',
                    'codecompany': '181',
                    'dataidentifier': '01010',
                    'epc': '4E2019DA81F9400000000000',
                    'tid': 'E20034120130F80006D01B2F1F20012970055FFBFFFFDC50',
                    'tagtype': 'TTF',
                    'rfid': '3f7668e1-e023-4307-a8cd-91bb88f983b8',
                    'period': '2017-04-21T19:19:43',
                    'status': 'active',
                },
            ],
        }

    return context


#
# Вставка другой записи - другой номер автомобиля, другие параметры.
# Должна создаться новая запись, а старая удалиться, т.к.
# её нет среди новых актуальных.
#
@pytest.mark.filldb(rfid_labels='one')
def test_rfid_labels_insert_label_with_diff_number(
        taxi_jobs, rfid_labels_services_good_one_c, db,
):
    taxi_jobs.run('rfid_labels')

    entries_a = db.rfid_labels.find({'_id': 'ХЕ27477'})
    assert entries_a.count() == 0

    entries_b = db.rfid_labels.find({'_id': 'ХР76877'})
    assert entries_b.count() == 1
    entry_b = entries_b[0]
    assert entry_b['_id'] == 'ХР76877'
    labels_b = entry_b['labels']
    assert len(labels_b) == 1
    label = labels_b[0]
    assert label['tagbarcode'] == '5M-101010'
    assert label['codecompany'] == '181'
    assert label['dataidentifier'] == '01010'
    assert label['epc'] == '4E2019DA81F9400000000000'
    assert label['tid'] == 'E20034120130F80006D01B2F1F20012970055FFBFFFFDC50'
    assert label['tagtype'] == 'TTF'
    assert label['rfid'] == '3f7668e1-e023-4307-a8cd-91bb88f983b8'
    assert label['status'] == 'active'
    assert label['period'] == '2017-04-21T19:19:43'


@pytest.fixture
def rfid_labels_services_good_one_d(mockserver):
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
                    'period': '2017-03-31T19:19:50',
                    'status': 'inactive',
                },
            ],
        }

    return context


#
# Вставка точно такой же записи - тот же номер автомобиля, все параметры те же,
# но со статусом inactive.
# Запись должна удалиться, тк ее нет среди новых актуальных.
#
@pytest.mark.filldb(rfid_labels='one')
def test_rfid_labels_insert_existing_label_diff_status(
        taxi_jobs, rfid_labels_services_good_one_d, db,
):
    taxi_jobs.run('rfid_labels')

    entries = db.rfid_labels.find({'_id': 'ХЕ27477'})
    assert entries.count() == 0


@pytest.mark.filldb(rfid_labels='two')
def test_rfid_labels_sorting(taxi_jobs, rfid_labels_services_good, db):
    taxi_jobs.run('rfid_labels')

    entries = db.rfid_labels.find({'_id': 'КУ71777'})
    assert entries.count() == 1
    entry = entries[0]
    assert entry['_id'] == 'КУ71777'
    labels = entry['labels']
    assert len(labels) == 1
    label = labels[0]
    del label['updated']
    assert label['tagbarcode'] == '5M-101166'
    assert label['codecompany'] == '181'
    assert label['dataidentifier'] == '01166'
    assert label['epc'] == '4E2019DA8247400000000000'
    assert label['tid'] == 'E20034120171FA0001323B1F28040167300559FBFFFFDC70'
    assert label['tagtype'] == 'CWL E-100'
    assert label['rfid'] == 'e94a8434-1d43-46ed-897c-dfc70f77216d'
    assert label['status'] == 'active'
    assert label['period'] == '2017-03-31T19:19:01'
    assert label['last_activity'] == '2017-03-31T19:19:02'
    assert label['zones'] == []

    entries = db.rfid_labels.find({'_id': 'КУ71779'})
    assert entries.count() == 0


@pytest.mark.filldb(rfid_labels='two')
def test_zone(taxi_jobs, db, mockserver):
    request_labels = [
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
            'zones': ['moscow', 'spb'],
        },
    ]

    @mockserver.json_handler('/ListRFID/GetListPOST')
    def mock_get_labels(request):
        return {'RFIDs': request_labels}

    taxi_jobs.run('rfid_labels', '--debug', '--without-lock')
    labels = db.rfid_labels.find_one({'_id': 'КУ71777'})['labels']
    assert len(labels) == 1
    current_label = labels[0]
    assert current_label['status'] == 'active', current_label
    assert set(current_label['zones']) == {'moscow', 'spb'}, current_label

    # deactivate
    request_labels[0]['status'] = 'inactive'
    taxi_jobs.run('rfid_labels', '--debug', '--without-lock')
    entries = db.rfid_labels.find_one({'_id': 'КУ71777'})
    assert not entries

    # activate again & will get new record
    request_labels[0]['status'] = 'active'
    taxi_jobs.run('rfid_labels', '--debug', '--without-lock')
    labels = db.rfid_labels.find_one({'_id': 'КУ71777'})['labels']
    assert len(labels) == 1
    current_label = labels[0]
    assert current_label['status'] == 'active', current_label
    assert set(current_label['zones']) == {'moscow', 'spb'}, current_label
