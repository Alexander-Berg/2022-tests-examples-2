from aiohttp import web

from dummy.generated import models as dummy_models
from example_library.generated import models as example_lib_models

from example_service import utils
from example_service.generated.web import web_context as web_context_module


def test_extraction():
    assert utils.extract_default_data() == [1, 2, 3]


async def test_example_jobber(web_context):
    job_to_be_done = example_lib_models.Job(
        is_done=False, dummy_ref=dummy_models.DummyObject(name='ahaha'),
    )
    assert job_to_be_done.result is None
    await web_context.example_jobber.do_job(job_to_be_done)
    assert job_to_be_done.is_done
    assert job_to_be_done.result == 'RESULT'
    assert job_to_be_done.dummy_ref.name == 'ahaha'


def test_example_adder(web_context):
    assert web_context.example_adder.add(100) == 100


async def test_do_job_handler(web_app_client):
    resp = await web_app_client.post('/do-example-job')
    assert resp.status == 200
    assert await resp.json() == {
        'is_done': True,
        'result': 'result',
        'dummy_ref': {'name': 'abacaba'},
    }


async def test_client_b2p(web_context: web_context_module.Context, mockserver):
    # pylint: disable=unused-variable
    @mockserver.handler('/best2pay/webapi/Register')
    async def mock_b2p(request):
        assert request.form == {
            'sector': '6666',
            'amount': '100',
            'currency': '42',
            'description': 'test',
            'signature': 'YjgxOWRmM2NlNjEzZjM1MmYxM2Q2ZjFkZDcxODEzZDg=',
            'phone': '88005553535',
        }
        return web.Response(
            status=200, content_type='application/xml', body='',
        )

    response = await web_context.clients.best2pay.order_register(
        amount=100,
        currency=42,
        description='test',
        phone='88005553535',
        sector=6666,
        signature=web_context.clients.best2pay.SIGNATURE_SENTINEL,
    )
    assert response.status == 200
