import pytest

from crm_hub.logic.communication.user import push_utils


@pytest.mark.parametrize(
    'deeplink, campaign_id, is_regular, add_utm_marks, expected_result',
    [
        (
            'yangodeli://something/somewhere',
            '1234',
            False,
            True,
            'yangodeli://something/somewhere?'
            'utm_source=push&utm_medium=crm_once&ref=1234',
        ),
        (
            'yangodeli://something/somewhere',
            '1234',
            True,
            True,
            'yangodeli://something/somewhere?'
            'utm_source=push&utm_medium=crm_regular&ref=1234',
        ),
        (
            'yangodeli://something/somewhere?service=grocery',
            '1234',
            False,
            True,
            'yangodeli://something/somewhere?'
            'service=grocery&utm_source=push&utm_medium=crm_once&ref=1234',
        ),
        (
            'nonmarkable://something/somewhere',
            '1234',
            False,
            True,
            'nonmarkable://something/somewhere',
        ),
        (
            'yangodeli://something/somewhere?service=grocery',
            '1234',
            False,
            False,
            'yangodeli://something/somewhere?service=grocery',
        ),
    ],
)
def test_add_utm_marks_to_deeplink(
        deeplink, campaign_id, is_regular, add_utm_marks, expected_result,
):
    utm_ctx = push_utils.DeeplinkUTMContext(
        campaign_id=campaign_id,
        campaign_is_regular=is_regular,
        add_utm_marks=add_utm_marks,
    )
    result = utm_ctx.format_deeplink(deeplink)
    assert result == expected_result
