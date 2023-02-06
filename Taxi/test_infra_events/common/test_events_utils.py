import pytest

from infra_events.common import events_utils
from infra_events.generated.service.swagger.models import api as models


@pytest.mark.parametrize(
    ['staff_login', 'src_service_name'],
    [
        ('test_user', 'test_service'),
        (None, 'test_service'),
        ('test_user', None),
        (None, None),
    ],
)
async def test_events_post(web_context, staff_login, src_service_name):
    await events_utils.post(
        web_context,
        events=[
            models.NewEvent(
                body='test_body',
                header='test_header',
                tags=['test_0'],
                views=['__all__'],
            ),
        ],
        source='test_source',
        staff_login=staff_login,
        src_service_name=src_service_name,
    )

    event = await web_context.mongo.lenta_events.find_one({})
    assert event['header'] == 'test_header'
    assert event['body'] == 'test_body'
    assert event['source'] == 'test_source'
    tags = {'test_0'}
    if staff_login:
        tags.add(f'staff:{staff_login}')
    if src_service_name:
        tags.add(f'src_service_name:{src_service_name}')

    assert set(event['tags']) == tags
