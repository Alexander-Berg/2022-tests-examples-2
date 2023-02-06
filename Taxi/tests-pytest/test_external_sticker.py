import json

import pytest

from taxi.external import sticker


@pytest.inline_callbacks
def test_get_mail_request_status(areq_request):
    @areq_request
    def sticker_request(*args, **kwargs):
        print args, kwargs
        assert kwargs['params'] == {
            'idempotence_token': 'idempotence_token',
            'recipient_personal_id': 'email_personal_id',
        }
        return areq_request.response(
            200,
            body=json.dumps({'status': 'SCHEDULED'}),
        )

    result = yield sticker.get_mail_request_status(
        'idempotence_token', 'email_personal_id',
    )
    assert result['status'] == 'SCHEDULED'
