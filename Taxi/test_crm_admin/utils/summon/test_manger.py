from aiohttp import web

import generated.models.ok as ok_module


async def test_ok_client(web_context, mock_ok):
    @mock_ok('/api/approvements/')
    def create_approvement(request):
        return web.json_response({}, status=201)

    data = {
        'object_id': 'LEEMURQUEUE-9',
        'text': 'Согласуем согласование',
        'stages': [
            {'approver': 'leemurus'},
            {
                'need_all': False,
                'stages': [
                    {'approver': 'trusienkodv'},
                    {'approver': 'artemzaxarov'},
                ],
            },
        ],
    }

    body = ok_module.CreateApprovementBody.deserialize(
        data=data, allow_extra=True,
    )
    resp = await web_context.client_ok.create_approvement(body=body)

    assert resp.status == 201
    assert create_approvement.times_called == 1
