import base64
import io
import re
import zipfile

import pytest

ID_GOOD = '0123456789abcdef'


async def test_ok(mockserver, stq_runner, stq, mongodb):
    @mockserver.json_handler('/personal/v1/emails/store')
    async def _mock_personal(request):
        assert request.json == {
            'validate': True,
            'value': 'igelbox@yandex-team.ru',
        }
        return mockserver.make_response(
            '{"id": "idid", "value": ""}', status=200,
        )

    @mockserver.json_handler('/sticker/send/')
    async def _mock_sticker(request):
        json = request.json
        assert {**json, 'attachments': None} == {
            'send_to': ['idid'],
            'idempotence_token': ID_GOOD,
            'body': (
                '<?xml version="1.0" encoding="UTF-8"?><mails><mail>'
                '<from>no-reply@taxi.yandex.ru</from>'
                '<subject>Promocodes series: test_series</subject>'
                '<body>Do not reply</body>'
                '</mail></mails>'
            ),
            'attachments': None,
        }

        attachment0, attachment1 = json['attachments']
        assert {**attachment0, 'data': None} == {
            'data': None,
            'filename': 'promocodes_test_series.txt.zip',
            'mime_type': 'application/zip',
        }
        zip_content = base64.b64decode(attachment0['data'])
        codes = {}
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zfile:
            codes = set(
                zfile.read('promocodes_test_series.txt')
                .decode('utf8')
                .split('\n'),
            )
        assert len(codes) == 10
        wrong_codes = [
            code for code in codes if not re.match('test_series\\d{6}', code)
        ]
        assert wrong_codes == []
        assert {**attachment1, 'data': None} == {
            'data': None,
            'filename': 'promocodes_test_series.xlsx.zip',
            'mime_type': 'application/zip',
        }
        assert 16000 < len(attachment1['data']) < 17000

        # for attachment in json['attachments']:
        #     with open('/tmp/' + attachment['filename'], 'wb') as afile:
        #         afile.write(base64.b64decode(attachment['data']))
        return mockserver.make_response('{}', status=200)

    await stq_runner.generate_promocodes.call(task_id='test', args=[ID_GOOD])

    # task must be completed
    assert stq.is_empty

    gen = mongodb.promocode_gen.find_one({'_id': ID_GOOD})
    assert _gen_status(gen) == ['completed']

    promocode_docs = mongodb.promocodes.find({'series_id': 'test_series'})
    promocodes = [p['code'] for p in promocode_docs]
    assert len(promocodes) == 2 + 10

    # Should skip subsequent calls silently and gracefully
    await stq_runner.generate_promocodes.call(
        task_id='test', args=[], kwargs={'gen_id': ID_GOOD},
    )
    assert stq.is_empty
    gen = mongodb.promocode_gen.find_one({'_id': ID_GOOD})
    assert _gen_status(gen) == ['completed']


ID_BAD = '0123456789abcdef01230001'


async def test_wrong_status(stq_runner, stq, mongodb):

    await stq_runner.generate_promocodes.call(
        task_id='test', args=[], kwargs={'gen_id': ID_BAD},
    )

    # task must be completed
    assert stq.is_empty

    gen = mongodb.promocode_gen.find_one({'_id': ID_BAD})
    assert _gen_status(gen) == ['processing']


@pytest.mark.parametrize(
    'prop, value, error',
    [
        ('clear_text', False, 'clear_text should be true'),
        ('is_unique', False, 'Series is non-unique'),
        ('value', 0, 'Value should be specified'),
    ],
)
async def test_validation(stq_runner, stq, mongodb, prop, value, error):
    mongodb.promocode_series.update_one(
        {'_id': 'test_series'}, {'$set': {prop: value}},
    )

    await stq_runner.generate_promocodes.call(
        task_id='test', args=[], kwargs={'gen_id': ID_GOOD},
    )

    assert stq.is_empty  # task must be completed

    gen = mongodb.promocode_gen.find_one({'_id': ID_GOOD})
    assert _gen_status(gen) == ['failed', error]


def _gen_status(gen):
    return [
        v for v in (gen.get(k, None) for k in ['status', 'error_message']) if v
    ]
