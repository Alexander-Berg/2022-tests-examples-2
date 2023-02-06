import json
import pytest

from taxi import config
from taxi.core import arequests
from taxi.core import db
from taxi_maintenance.stuff import import_frequent_permits
from taxi_tasks.permit import _base
from taxi_tasks.permit import handlers
from taxi_tasks.permit import moscow


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
@pytest.mark.config(
    TAXOMOTOR_URL='http://taxomotor.srvdev.ru'
)
@pytest.mark.parametrize(
    'enable_taxomotor_permits_check', [False, True]
)
@pytest.mark.parametrize(
    'frequent_permits_areas', [[], ['moscow', 'moscow_oblast']]
)
@pytest.mark.parametrize(
    'taxomotor_code, taxomotor_message',
    [(200, None), (403, 'Forbidden'), (500, 'Internal error')]
)
def test_import_frequent_permits(
        mock, patch, load, enable_taxomotor_permits_check,
        frequent_permits_areas, taxomotor_code, taxomotor_message,
):
    good_stat = _base.ImportPermitsStat()
    bad_stat = _base.ImportPermitsStat()
    bad_stat.failed_count = 1

    @mock
    def import_permits_moscow(*args, **kwargs):
        if enable_taxomotor_permits_check:
            return moscow.import_permits_moscow()

        return good_stat

    @mock
    def import_permits_moscow_oblast(*args, **kwargs):
        return good_stat

    @patch('taxi.core.arequests.post')
    def taxomotor_request(url, **kwargs):
        assert(
            url == 'http://taxomotor.srvdev.ru/LicenseRegistry/GetAllLicense'
        )
        headers = kwargs.get('headers')
        assert headers == {
            'Authorization': 'yandex_taxi:password',
            'Content-Type': 'application/json',
        }

        if taxomotor_message is not None:
            data = {'code': 1, 'message': taxomotor_message}
        else:
            data = json.loads(load('taxomotor_data.json'))
        return arequests.Response(
            status_code=taxomotor_code, content=json.dumps(data),
        )

    handlers.PERMIT_HANDLERS = {
        'moscow': import_permits_moscow,
        'moscow_oblast': import_permits_moscow_oblast,
    }
    yield config.save(
        'ENABLE_MOSCOW_PERMITS_CHECK_BY_TAXOMOTOR',
        enable_taxomotor_permits_check
    )
    yield config.save(
        'FREQUENT_PERMITS_AREAS',
        frequent_permits_areas
    )

    moscow_enabled = 'moscow' in frequent_permits_areas
    has_new_calls = moscow_enabled and enable_taxomotor_permits_check

    try:
        import_frequent_permits.do_stuff()
        if has_new_calls:
            assert taxomotor_code == 200
    except handlers.ImportPermitsError as exc:
        assert has_new_calls
        assert taxomotor_code != 200
        assert str(exc) == 'Failed import permits for moscow'

    moscow_calls = 1 if moscow_enabled else 0

    assert len(import_permits_moscow.calls) == moscow_calls
    assert (len(import_permits_moscow_oblast.calls) > 0) == (
        'moscow_oblast' in frequent_permits_areas
    )
    assert (len(taxomotor_request.calls) > 0) == (
        enable_taxomotor_permits_check and moscow_enabled
    )

    permits = list(db.permits._collection.find())
    if has_new_calls and taxomotor_code == 200:
        expected_permits = 2
    else:
        expected_permits = 0
    assert len(permits) == expected_permits

    for permit in permits:
        assert permit['_state'] == 'active'
        assert permit['issuer_id'] == 3
