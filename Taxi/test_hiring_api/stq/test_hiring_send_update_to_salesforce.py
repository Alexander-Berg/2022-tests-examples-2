import uuid

from aiohttp import web
import pytest

LEAD_ID = 'ID1'
EXPECTED_YT_DATA_TABLE = 'expected_yt_data.json'
YT_STQ_TABLE = '//home/test/stq_table'


@pytest.mark.now('2022-09-15T10:00:00Z')
@pytest.mark.config(HIRING_FAILED_STQ_TABLE_PATH=YT_STQ_TABLE)
@pytest.mark.parametrize('case', ['204', '400'])
async def test_salesforce_update(
        load_json,
        stq_runner,
        stq3_context,
        simple_secdist,
        mock_salesforce_auth,
        mock_salesforce_update,
        mock_territories_api,
        yt_client,
        case,
):
    request = load_json('ticket_data.json')[case]
    assert isinstance(request['errors'], list)
    handler_salesforce = mock_salesforce_update(
        LEAD_ID, int(case), request['success'], request['errors'],
    )
    await stq_runner.hiring_send_update_to_salesforce.call(
        task_id='1',
        args=(),
        kwargs={'lead_id': LEAD_ID, 'body': request['data']},
    )
    assert handler_salesforce.has_calls

    if case == '400':
        expected_yt_data = load_json(EXPECTED_YT_DATA_TABLE)
        rows = list(yt_client.read_table(YT_STQ_TABLE))
        assert rows[-1] == expected_yt_data


@pytest.mark.config(
    HIRING_API_PERSONAL_DATA_FIELDS={
        'FIELDS_WITH_PERSONAL_DATA': [],
        'FIELDS_WITH_PERSONAL_IDS': [
            {
                'converted_name': 'phone',
                'name': 'personal_phone_id',
                'type': 'phones',
            },
            {
                'converted_name': 'driver_license',
                'name': 'personal_license_id',
                'type': 'driver_licenses',
            },
            {
                'converted_name': 'contact_email',
                'name': 'personal_contact_email_id',
                'type': 'emails',
            },
        ],
    },
)
@pytest.mark.config(
    TVM_RULES=[{'dst': 'personal', 'src': 'hiring-api'}], TVM_ENABLED=False,
)
async def test_salesforce_update_with_personal_fields(
        stq_runner,
        stq3_context,
        mock_salesforce_auth,
        mock_salesforce,
        mock_territories_api,
        mock_personal_api,
        load_json,
):
    @mock_salesforce(f'/services/data/v46.0/sobjects/Lead/{LEAD_ID}')
    async def handler(request):
        assert request.json['Phone'] == '+79998887766'
        assert request.json['Email'] == 'email@email.com'
        return web.json_response(
            {'id': uuid.uuid4().hex, 'success': True, 'errors': []},
            status=204,
        )

    request = load_json('ticket_data_with_personal_ids.json')
    await stq_runner.hiring_send_update_to_salesforce.call(
        task_id='1', args=(), kwargs={'lead_id': LEAD_ID, 'body': request},
    )
    assert handler.has_calls
