import csv
import json
import os


def convert_field(field):
    converts = {
        'amount': 'cast(amount as TEXT) as amount',
        'client_id': 'cast(client_id as TEXT) as client_id',
    }
    return converts.get(field, field)


def convert_fields(fields):
    return ','.join(map(convert_field, fields))


async def run(fixtures, test_file):
    cur_dir = os.path.dirname(os.path.realpath(test_file))

    default_config = os.path.join(
        os.path.dirname(__file__), 'static', 'default', 'config.json',
    )
    if os.path.isfile(default_config):
        config_data = json.load(open(default_config))
        fixtures.taxi_config.set_values(config_data)

    config = os.path.join(cur_dir, 'config.json')
    if os.path.isfile(config):
        config_data = json.load(open(config))
        fixtures.taxi_config.set_values(config_data)

    business_rules = {}
    business_rules_path = os.path.join(cur_dir, 'business_rules.json')
    if os.path.isfile(business_rules_path):
        business_rules = json.load(open(business_rules_path))
    commissions = (
        business_rules['commissions']
        if 'commissions' in business_rules.keys()
        else {}
    )
    fines = business_rules['fines'] if 'fines' in business_rules.keys() else {}
    client_info = (
        business_rules['client_info']
        if 'client_info' in business_rules.keys()
        else {}
    )
    fixtures.business_rules_mock(commissions, fines)
    fixtures.client_info_mock(client_info)

    input_requests = json.load(open(os.path.join(cur_dir, 'input.json')))
    for request in input_requests:
        response = await fixtures.taxi_eats_billing_processor.post(
            '/v1/create', json=request,
        )
        assert response.status == 200

    call_info = fixtures.stq.eats_billing_processor_transformer.next_call()
    await fixtures.stq_runner.eats_billing_processor_transformer.call(
        task_id=call_info['id'], kwargs=call_info['kwargs'],
    )
    call_info = (
        fixtures.stq.eats_billing_processor_billing_processor.next_call()
    )
    await fixtures.stq_runner.eats_billing_processor_billing_processor.call(
        task_id=call_info['id'], kwargs=call_info['kwargs'],
    )

    fields = []
    expects = []
    with open(os.path.join(cur_dir, 'transfers_columns.csv'), 'r') as f_csv:
        reader = csv.reader(f_csv, quoting=csv.QUOTE_NONE)
        fields = next(reader)
        expects = list(reader)
    cursor = fixtures.pgsql['eats_billing_processor'].cursor()
    cursor.execute(
        f"""
        select {convert_fields(fields)} from eats_billing_processor.transfers
        """,
    )
    transfers = list(list(x) for x in cursor)
    assert transfers == expects
