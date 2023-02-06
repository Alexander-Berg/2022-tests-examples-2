from aiohttp import web

import dummy
from dummy.generated import models as dummy_models

from example_library import dummy_utils
from example_library import yas_utils
from example_library.generated import models


def test_happy_path():
    assert dummy_utils.extract_data(dummy.Dummy()) == [1, 2, 3]


async def test_client_usage(mock_yet_another_service, library_context):
    client = library_context.clients.yet_another_service

    @mock_yet_another_service('/talk')
    async def handler(request):
        return web.Response(text='aaaa')

    assert await yas_utils.small_talk(client) == 'TALK: aaaa'
    assert handler.times_called == 1


async def test_example_component(library_context):
    job_to_be_done = models.Job(
        is_done=False, dummy_ref=dummy_models.DummyObject(name='bacbac'),
    )
    assert not job_to_be_done.is_done
    assert job_to_be_done.result is None
    await library_context.example_jobber.do_job(job_to_be_done)
    assert job_to_be_done.is_done
    assert job_to_be_done.result == 'RESULT'


def test_default_adder(library_context):
    assert library_context.example_adder.add(11) == 53


def test_dummy_component(library_context):
    assert library_context.dummy_component.get_parameters() == ['hello']
