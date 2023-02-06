import pytest


@pytest.mark.config(
    MESSENGER_SERVICES={
        'chatterbox': {
            'accounts': ['premium_support'],
            'description': 'chatterbox description',
        },
    },
)
async def test_task(taxi_messenger, mockserver, stq_runner):
    @mockserver.handler('/some_file.ext')
    def _mock_media_server(request):
        return mockserver.make_response('Some data', 200)

    await stq_runner.messenger_media_download.call(
        task_id='sample_task',
        kwargs={
            'service': 'chatterbox',
            'account': 'premium_support',
            'url': mockserver.url('some_file.ext'),
            'media_id': 'media_000',
            'file_name': 'some_file.ext',
            'client_name': 'whatsapp',
        },
        expect_fail=False,
    )
