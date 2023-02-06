import datetime

import pytest
import pytz


def do_select_from(cursor, now, keys, table):
    select_keys = ', '.join(keys)
    cursor.execute(f'SELECT {select_keys} FROM {table}')
    result = []
    for item in cursor.fetchall():
        push = {}
        for i, value in enumerate(item):
            push[keys[i]] = value
        updated = push['updated'].astimezone(pytz.UTC).replace(tzinfo=None)
        updated = (updated - now) < datetime.timedelta(seconds=5)
        push['updated'] = updated
        result.append(push)
    return result


def get_company_wms(cursor, now):
    keys = [
        'company_id',
        'updated',
        'external_id',
        'ownership',
        'title',
        'fullname',
        'legal_address',
        'actual_address',
        'address',
        'phone',
        'email',
        'psrn',
        'tin',
        'ies',
        'okpo',
        'okved',
        'pay_account',
        'cor_account',
        'bic',
        'bank_info',
    ]
    result = do_select_from(cursor, now, keys, 'depots_wms.companies')
    return sorted(result, key=lambda k: k['company_id'])


@pytest.mark.suspend_periodic_tasks('wms-companies-sync-periodic')
async def test_companies_wms_import(
        taxi_grocery_depots, mockserver, pgsql, load_json,
):
    now = datetime.datetime.now()

    @mockserver.json_handler('/grocery-wms/api/external/companies/v1/list')
    def mock_wms_companies_response(request):
        if request.json['cursor'] == '':
            return load_json('wms_companies_response.json')
        if request.json['cursor'] == 'last-cursor':
            return load_json('wms_companies_response_last.json')
        return {}

    await taxi_grocery_depots.run_periodic_task('wms-companies-sync-periodic')

    db = pgsql['grocery_depots']
    cursor = db.cursor()

    result = get_company_wms(cursor, now)
    expected_companies = load_json('companies_wms_from_db.json')['answer']
    assert result == expected_companies
    assert mock_wms_companies_response.times_called == 2
