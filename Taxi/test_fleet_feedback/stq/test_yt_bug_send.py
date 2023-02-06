from fleet_feedback.generated.stq3 import stq_context as context
from fleet_feedback.stq import yt_bug_event


async def test_success(stq3_context: context.Context, patch):
    @patch('taxi.yt_wrapper.YtClient.create')
    def _create(*args, **kwargs):
        return '1234-4321-2345-5432'

    @patch('taxi.yt_wrapper.YtClient.exists')
    def _exists(*args, **kwargs):
        return False

    @patch('taxi.yt_wrapper.YtClient.write_table')
    def _write_table(*args, **kwargs):
        return

    await yt_bug_event.task(
        context=stq3_context,
        email_data={
            'park_id': 'test',
            'text': 'test',
            'label': 'test',
            'created_at': 'test',
            'url': 'test',
            'support_url': 'test',
            'passport_uid': 'test',
            'is_superuser': 'test',
            'city': 'test',
            'browser': 'test',
            'screen_width': 'test',
            'screen_height': 'test',
        },
    )
