import email

import dateutil.parser
import pytest

from taxi_tariffs.stq import get_tariffs_list_csv as stq
from taxi_tariffs.stq.utils import email as email_utils

TIMESTAMP = '2020-04-29T16:34:22.700Z'


def _remove_newline(string: str):
    return string.replace('\r', '').replace('\n', '')


def _get_file_and_text(message_str: str):
    message = email.message_from_string(message_str)

    email_text = (
        message.get_payload()[0]
        .get_payload()[0]
        .get_payload(decode=True)
        .decode('utf-8')
    )
    if len(message.get_payload()) == 2:
        email_file = (
            message.get_payload()[1].get_payload(decode=True).decode('utf-8')
        )
    else:
        email_file = None

    return email_file, email_text


def _idle_mock(*args, **kwargs):
    pass


@pytest.fixture
def mock_audit(mockserver, load_json, zones):
    req_number = 1

    @mockserver.json_handler('/audit/v1/robot/logs/retrieve/')
    async def _handler(request):
        nonlocal req_number
        _check_audit_request(request.json, req_number, zones)
        full_resp = load_json(f'audit_response.json')
        limit = request.json['limit']
        skip = request.json['skip']
        req_number += 1
        return full_resp[skip : skip + limit]

    return _handler


def _check_audit_request(request, req_number, zones):

    query = request['query']

    assert sorted(query['object_ids']) == sorted(zones)
    assert query['actions'] == ['set_tariff']
    assert dateutil.parser.parse(query['date_till']) == dateutil.parser.parse(
        TIMESTAMP,
    )

    assert request['sort'][0]['direction'] == 'desc'
    assert request['limit'] == 2

    if req_number == 1:
        assert request['skip'] == 0
    else:
        assert request['skip'] == 2


# pylint: disable=redefined-outer-name
@pytest.mark.config(
    TAXI_TARIFFS_AUDIT_REQUEST_SETTINGS={
        'audit_limit': 2,
        'zones_batch_size': 2,
    },
)
@pytest.mark.parametrize(
    ('zones', 'expected_file_name', 'expected_text'),
    [
        pytest.param(
            ['moscow', 'spb'],
            'expected_tariffs.csv',
            email_utils.TEXT_TEMPLATE.format(
                msg='tariffs information',
                add_msg=(
                    'for zones: [\'moscow\', \'spb\']\n\n'
                    'zones without categories: []'
                ),
            ),
            id='success',
        ),
        pytest.param(
            ['without_categories'],
            None,
            email_utils.TEXT_TEMPLATE.format(
                msg='tariffs information',
                add_msg=(
                    'for zones: []\n\n'
                    'zones without categories: [\'without_categories\']'
                ),
            ),
            id='with_empty_categories',
        ),
        pytest.param(
            ['without_categories', 'moscow'],
            'expected_only_moscow.csv',
            email_utils.TEXT_TEMPLATE.format(
                msg='tariffs information',
                add_msg=(
                    'for zones: [\'moscow\']\n\n'
                    'zones without categories: [\'without_categories\']'
                ),
            ),
            id='with_categories_and_without',
        ),
        pytest.param(
            ['voronezh'],
            None,
            email_utils.TEXT_TEMPLATE.format(
                msg='error', add_msg='not_found_zones: {\'voronezh\'}',
            ),
            id='error_zone_not_found',
        ),
    ],
)
async def test_sending_tariffs_csv_to_email(
        stq3_context,
        mockserver,
        monkeypatch,
        load,
        load_json,
        mock_audit,
        zones,
        expected_file_name,
        expected_text,
):
    class MockSMTP:
        body = None

        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def send_message(self, msg: email.message.Message):
            assert msg['From'] == '<noreply@yandex-team.ru>'
            assert msg['To'] == '<te@s.t>'
            MockSMTP.body = msg.as_string()

    monkeypatch.setattr('smtplib.SMTP', MockSMTP)

    await stq.task(stq3_context, 'te@s.t', zones, TIMESTAMP)

    sent_csv, sent_text = _get_file_and_text(MockSMTP.body)
    assert expected_text == sent_text

    if expected_file_name is not None:
        expected_csv = load(expected_file_name)
        assert _remove_newline(expected_csv) == _remove_newline(sent_csv)
        assert mock_audit.times_called == 2
    else:
        assert sent_csv is None
