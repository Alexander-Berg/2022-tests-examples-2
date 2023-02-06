import pytest


@pytest.mark.processing_queue_config(
    'handler.yaml', scope='testsuite', queue='example',
)
@pytest.mark.parametrize('lb_alias', ['topic-a', 'topic-b'])
async def test_lb_dynamic_alias(processing, testpoint, lb_alias):
    @testpoint('logbroker_publish')
    def logbroker_tp(data):
        assert data['name'] == lb_alias

    await processing.testsuite.example.send_event(
        '1234', payload={'lb-alias': lb_alias},
    )
    assert logbroker_tp.times_called == 1
