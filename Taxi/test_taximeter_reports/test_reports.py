# pylint: disable=too-many-arguments,too-many-locals
import collections
import datetime
import operator

import freezegun
import pytest

from taxi.clients import yt

from taximeter_reports import models
from taximeter_reports import settings
from taximeter_reports.core import maker


MDS_KEY = '3232/mds_key'
MDS_XLS_KEY = '3232/mds_xls_key'
XLS_DATA = b'xls data'
TOKEN_FOR_RACES = '3731229e6e204b5f90d33f1ce8682cc4'
NOW = datetime.datetime(2018, 5, 25, 9)

HEADERS = {'YaTaxi-Api-Key': 'secret'}


class MockSession:
    async def close(self):
        pass


class _DummyMDSClient:
    def __init__(self, xls_enable):
        self.xls_is_recorded = False or not xls_enable
        self.file_json = None

    async def upload(self, file_obj, ttl):
        assert 3 * 3600 <= ttl <= 24 * 3600
        if not self.xls_is_recorded:
            self.xls_is_recorded = True
            key = MDS_XLS_KEY
        else:
            self.file_json = file_obj
            key = MDS_KEY
        return key

    async def download(self, file_key, range_start=None, range_end=None):
        if file_key == MDS_KEY:
            if range_start and range_end:
                result = self.file_json[range_start : range_end + 1]
            else:
                result = self.file_json
        else:
            result = XLS_DATA
        return result


_ReportTestCase = collections.namedtuple(
    '_ReportTestCase',
    [
        'request_data',
        'yt_rows',
        'expected_schema',
        'expected_report',
        'records_per_page',
        'xls_enable',
        'expected_yt_queries',
    ],
)


def parametrize_reports_testcase():
    additional_tests = {'order_payments_workshift_filter'}
    parameters = []

    for xls_enable in (True, False):
        parameters.append(
            (
                'drivers_2_records_per_page',
                _ReportTestCase(
                    request_data='drivers/request.json',
                    yt_rows='drivers/rows.json',
                    expected_schema='drivers/expected_schema_response.json',
                    expected_report=(
                        'drivers_2_records_per_page_expected_report.json'
                    ),
                    records_per_page=2,
                    xls_enable=xls_enable,
                    expected_yt_queries='drivers/expected_yt_queries.json',
                ),
            ),
        )
        for records_per_page in (2, 100):
            parameters.append(
                (
                    'drivers_empty_%d_records_per_page' % records_per_page,
                    _ReportTestCase(
                        request_data='drivers/request.json',
                        yt_rows=None,
                        expected_schema=(
                            'drivers_expected_schema_response_empty.json'
                        ),
                        expected_report=None,
                        records_per_page=records_per_page,
                        xls_enable=xls_enable,
                        expected_yt_queries='drivers/expected_yt_queries.json',
                    ),
                ),
            )
        for model_name in models.ALL_KWARGS.keys() | additional_tests:
            parameters.append(
                (
                    'model %s' % model_name,
                    _ReportTestCase(
                        request_data='%s/request.json' % model_name,
                        yt_rows='%s/rows.json' % model_name,
                        expected_schema=(
                            '%s/expected_schema_response.json' % model_name
                        ),
                        expected_report='%s/expected_report.json' % model_name,
                        records_per_page=100,
                        xls_enable=xls_enable,
                        expected_yt_queries=(
                            '%s/expected_yt_queries.json' % model_name
                        ),
                    ),
                ),
            )
    parameters.sort(key=operator.itemgetter(0))
    return pytest.mark.parametrize('test_case_name,test_case', parameters)


@parametrize_reports_testcase()
async def test_reports(
        monkeypatch,
        load,
        load_json,
        taximeter_reports_client,
        taximeter_reports_app,
        test_case_name,
        test_case,
):
    _patch_yt_clients(
        monkeypatch,
        load_json,
        taximeter_reports_app,
        test_case.yt_rows,
        test_case.records_per_page,
        test_case.xls_enable,
    )
    _mds_client(
        monkeypatch, taximeter_reports_app, xls_enable=test_case.xls_enable,
    )

    response = await taximeter_reports_client.post(
        '/reports', data=load(test_case.request_data), headers=HEADERS,
    )
    assert response.status == 200
    report_info = await (
        taximeter_reports_app.db.taximeter_reports_requests.find_one()
    )
    with freezegun.freeze_time(NOW, ignore=['']):
        await maker.init_and_build(taximeter_reports_app, report_info['_id'])
    assert taximeter_reports_app.yt_clients['seneca-sas'].queries == load_json(
        test_case.expected_yt_queries,
    )

    report_info = await (
        taximeter_reports_app.db.taximeter_reports_requests.find_one()
    )
    assert report_info['status'] == 'success'
    assert report_info['attempts'] == 1
    assert report_info['mds_xls_key'] == (
        MDS_XLS_KEY if test_case.xls_enable else None
    )

    expected_schema_response = load_json(test_case.expected_schema)
    assert report_info['report_schema'] == expected_schema_response['schema']

    token = report_info['confirmation_token']
    assert (await response.json()) == (
        {'report_id': token, 'status': 'in_progress'}
    )

    expected_schema_response['report_id'] = token
    expected_schema_response['records_per_page'] = test_case.records_per_page
    page_mapper = report_info['page_mapper']
    if page_mapper:
        expected_schema_response['page_count'] = len(page_mapper)
        expected_report_data = load_json(test_case.expected_report)
        for page_num in range(1, len(page_mapper) + 1):
            await _check_pages_response(
                taximeter_reports_client,
                '{}/pages/{}'.format(token, page_num),
                expected_report_data[page_num - 1 : page_num],
                test_case='%s, page=%d: ' % (test_case_name, page_num),
            )
            await _check_pages_response(
                taximeter_reports_client,
                '{}/pages/1,{}'.format(token, page_num),
                expected_report_data[0:page_num],
                test_case='%s, pages=%d-%d: ' % (test_case_name, 1, page_num),
            )
            await _check_pages_response(
                taximeter_reports_client,
                '{}/pages/{},{}'.format(token, page_num, page_num + 2),
                expected_report_data[page_num - 1 : page_num + 2],
                test_case='%s, pages=%d-%d: '
                % (test_case_name, page_num, page_num + 2),
            )
            await _check_pages_response(
                taximeter_reports_client,
                '{}/pages/{},{}'.format(token, page_num, page_num - 1),
                '{} is not correct page for report {}'.format(
                    page_num - 1, token,
                ),
                error=True,
            )

    schema_response = await taximeter_reports_client.get(
        '/reports/{}/status'.format(token), headers=HEADERS,
    )
    assert expected_schema_response == (await schema_response.json())

    response = await taximeter_reports_client.get(
        '/reports/{}/pages/1'.format(token), headers=HEADERS,
    )
    if test_case.expected_report is None:
        assert report_info['mds_key'] is None
        assert response.status == 404
        assert (await response.text()) == (
            '1 is not correct page for report {}'.format(token)
        )
    else:
        assert report_info['mds_key'] == MDS_KEY
        _objects_check(
            result=(await response.json()),
            expected=load_json(test_case.expected_report)[0:1],
            path=test_case_name,
        )

    await taximeter_reports_app.db.taximeter_reports_requests.remove(
        report_info['_id'],
    )


async def _check_pages_response(
        taximeter_reports_client,
        query,
        expected_data,
        error=False,
        test_case='',
):
    response = await taximeter_reports_client.get(
        '/reports/%s' % query, headers=HEADERS,
    )
    if error:
        response_data = await response.text()
    else:
        response_data = await response.json()
    _objects_check(response_data, expected_data, path=test_case)


def _objects_check(result, expected, path=''):
    if isinstance(result, list):
        assert len(result) == len(expected), (
            '%s: len(result)=%d != len(expected)=%d'
            % (path, len(result), len(expected))
        )
        for num, result_el, expected_el in zip(
                range(len(result)), result, expected,
        ):
            _objects_check(
                result_el, expected_el, path='.'.join((path, str(num))),
            )
    elif isinstance(result, dict):
        keys = sorted(result.keys())
        expected_keys = sorted(expected.keys())
        for key in keys:
            assert key in expected_keys, (
                '%s: key=%s not in expected keys: %s'
                % (path, key, ' '.join(expected_keys))
            )
            _objects_check(
                result[key], expected[key], path='.'.join((path, str(key))),
            )
        assert len(keys) == len(expected_keys), (
            '%s: len(keys)=%d != len(expected_keys)=%d, diff: %s'
            % (
                path,
                len(keys),
                len(expected_keys),
                [key for key in expected_keys if key not in keys],
            )
        )
    assert result == expected, '%s: result=%s != expected=%s' % (
        path,
        result,
        expected,
    )


def _mds_client(monkeypatch, taximeter_reports_app, xls_enable=False):
    mds_client = _DummyMDSClient(xls_enable)
    monkeypatch.setattr(taximeter_reports_app, 'mds_client', mds_client)
    return mds_client


def _patch_yt_clients(
        monkeypatch,
        load_json,
        taximeter_reports_app,
        yt_rows,
        records_per_page,
        xls_enable,
):
    class MockYTCLient:
        config = {'prefix': 'env_prefix/'}
        session = MockSession()
        name = 'seneca-ok'

        def __init__(self):
            self.queries = []
            self._need_to_return = True

        async def select_rows(self, query, *args, **kwargs):
            self.queries.append(query)
            if self._need_to_return and yt_rows:
                self._need_to_return = False
                rows = load_json(yt_rows)
            else:
                rows = []
            return rows

    class FailYTCLient:
        config = {'prefix': 'prefix'}
        session = MockSession()
        name = 'seneca-bad'

        async def select_rows(self, *args, **kwargs):
            raise yt.YtRequestError()

    monkeypatch.setattr(
        settings, 'YT_TAXIMETER_RECORDS_PER_PAGE', records_per_page,
    )
    monkeypatch.setattr(settings, 'YT_TAXIMETER_XLS_ENABLE', xls_enable)

    monkeypatch.setattr(
        taximeter_reports_app,
        'yt_clients',
        {
            'seneca-man': FailYTCLient(),
            'seneca-sas': MockYTCLient(),
            'seneca-vla': MockYTCLient(),
        },
    )


async def _dummy_build(*args, **kwargs):
    pass


async def _check_count(taximeter_reports_app):
    count = await taximeter_reports_app.db.taximeter_reports_requests.count()
    assert count == 8


def _patch_api(monkeypatch, xls_enable=True):
    monkeypatch.setattr('taximeter_reports.core.maker._build', _dummy_build)
    monkeypatch.setattr(settings, 'YT_TAXIMETER_MAX_ATTEMPTS', 5)
    monkeypatch.setattr(settings, 'YT_TAXIMETER_XLS_ENABLE', xls_enable)


@pytest.mark.filldb(taximeter_reports_requests='test_api')
@pytest.mark.parametrize(
    'token,expected_data,expected_attempts,expected_status,'
    'expected_db_status,expected_xls_data',
    [
        (  # success report
            '3731229e6e204b5f90d33f1ce8682cc7',
            {
                'status': 'success',
                'report_id': '3731229e6e204b5f90d33f1ce8682cc7',
                'page_count': 1,
                'schema': [],
            },
            1,
            200,
            'success',
            (200, XLS_DATA.decode()),
        ),
        (  # forbidden, bad api_token
            None,
            'Invalid token YaTaxi-Api-Key or X-YaTaxi-Api-Key: \'bad_token\'',
            None,
            403,
            None,
            None,
        ),
        (  # success report, xls disabled
            '3731229e6e204b5f90d33f1ce8682cc8',
            {
                'status': 'success',
                'report_id': '3731229e6e204b5f90d33f1ce8682cc8',
                'page_count': 1,
                'schema': [],
            },
            1,
            200,
            'success',
            (
                404,
                'xls for report 3731229e6e204b5f90d33f1ce8682cc8 '
                'not found (disabled)',
            ),
        ),
        (  # empty report
            '3731229e6e204b5f90d33f1ce8682cc9',
            {
                'status': 'success',
                'report_id': '3731229e6e204b5f90d33f1ce8682cc9',
                'page_count': 0,
                'schema': [],
            },
            1,
            200,
            'success',
            (
                404,
                'xls for report 3731229e6e204b5f90d33f1ce8682cc9 '
                'not found (disabled)',
            ),
        ),
        (  # in_progress report
            '3731229e6e204b5f90d33f1ce8682cc0',
            {
                'status': 'in_progress',
                'report_id': '3731229e6e204b5f90d33f1ce8682cc0',
            },
            1,
            200,
            'in_progress',
            (404, 'xls for report 3731229e6e204b5f90d33f1ce8682cc0 not found'),
        ),
        (  # double with confirmation_token
            None,
            {
                'status': 'in_progress',
                'report_id': '3731229e6e204b5f90d33f1ce8682cc1',
            },
            3,
            200,
            'in_progress',
            (404, 'xls for report 3731229e6e204b5f90d33f1ce8682cc1 not found'),
        ),
        (  # in_progress
            '3731229e6e204b5f90d33f1ce8682cc1',
            {
                'status': 'in_progress',
                'report_id': '3731229e6e204b5f90d33f1ce8682cc1',
            },
            3,
            200,
            'in_progress',
            (404, 'xls for report 3731229e6e204b5f90d33f1ce8682cc1 not found'),
        ),
        (  # not found
            '3731229e6e204b5f90d33f1ce86821c1',
            'report 3731229e6e204b5f90d33f1ce86821c1 not found',
            None,
            404,
            None,
            (404, 'report 3731229e6e204b5f90d33f1ce86821c1 not found'),
        ),
        (  # not valid confirmation token
            None,
            'not_valid_token is not valid confirmation token',
            None,
            400,
            None,
            (404, 'report not_valid_token not found'),
        ),
        (  # already failed
            '3731229e6e204b5f90d33f1ce8682cc3',
            {
                'status': 'failed',
                'report_id': '3731229e6e204b5f90d33f1ce8682cc3',
            },
            5,
            200,
            'failed',
            (404, 'xls for report 3731229e6e204b5f90d33f1ce8682cc3 not found'),
        ),
    ],
)
async def test_api(
        monkeypatch,
        load,
        taximeter_reports_client,
        taximeter_reports_app,
        token,
        expected_data,
        expected_attempts,
        expected_status,
        expected_db_status,
        expected_xls_data,
):
    _patch_api(monkeypatch)
    _mds_client(monkeypatch, taximeter_reports_app, xls_enable=True)
    await _check_count(taximeter_reports_app)

    if token:
        response = await taximeter_reports_client.get(
            '/reports/{}/status'.format(token), headers=HEADERS,
        )
        xls_response = await taximeter_reports_client.get(
            '/reports/{}/xls'.format(token), headers=HEADERS,
        )
        assert expected_xls_data == (
            xls_response.status,
            await xls_response.text(),
        )
    else:
        headers = HEADERS
        if expected_status != 400:
            data = load('drivers/request.json')
            if expected_status == 403:
                headers = {'YaTaxi-Api-Key': 'bad_token'}
        else:
            data = load('not_valid_request.json')
        response = await taximeter_reports_client.post(
            '/reports', data=data, headers=headers,
        )

    if expected_attempts is None:
        response_data = await response.text()
    else:
        response_data = await response.json()
        if token is None:
            token = response_data['report_id']

        doc = await (
            taximeter_reports_app.db.taximeter_reports_requests.find_one(
                {'confirmation_token': token},
            )
        )
        assert doc['attempts'] == expected_attempts
        assert doc['status'] == expected_db_status

    assert response_data == expected_data
    assert response.status == expected_status

    await _check_count(taximeter_reports_app)


@pytest.mark.filldb(taximeter_reports_requests='test_api')
@pytest.mark.parametrize(
    'unexpected_update,expected_data,expected_attempts',
    [
        (  # already failed race
            {'$set': {'status': 'failed'}},
            {'status': 'failed', 'report_id': TOKEN_FOR_RACES},
            1,
        ),
        (  # already success race
            {'$set': {'status': 'success'}},
            {
                'status': 'success',
                'report_id': TOKEN_FOR_RACES,
                'page_count': 1,
                'schema': [],
            },
            1,
        ),
        (  # attempts race
            {'$inc': {'attempts': 4}},
            {'status': 'failed', 'report_id': TOKEN_FOR_RACES},
            5,
        ),
    ],
)
async def test_api_races(
        monkeypatch,
        taximeter_reports_client,
        taximeter_reports_app,
        unexpected_update,
        expected_data,
        expected_attempts,
):
    _patch_api(monkeypatch)
    await _check_count(taximeter_reports_app)

    class Check:
        was_first_update = False

    db_reports = taximeter_reports_app.db.taximeter_reports_requests

    async def _db_update(query, to_update):
        if not Check.was_first_update:
            await db_reports.update(query, unexpected_update)
            Check.was_first_update = True
            return {'nModified': 0}
        return await db_reports.update(query, to_update)

    monkeypatch.setattr(
        taximeter_reports_app['report_handler'], '_db_update', _db_update,
    )

    await maker.init_and_build(taximeter_reports_app, 'report_7_races')

    response = await taximeter_reports_client.get(
        '/reports/{}/status'.format(TOKEN_FOR_RACES), headers=HEADERS,
    )
    response_data = await response.json()
    assert response_data == expected_data
    assert response.status == 200

    doc = await taximeter_reports_app.db.taximeter_reports_requests.find_one(
        {'confirmation_token': TOKEN_FOR_RACES},
    )
    assert doc['attempts'] == expected_attempts
    assert doc['status'] == expected_data['status']

    await _check_count(taximeter_reports_app)
