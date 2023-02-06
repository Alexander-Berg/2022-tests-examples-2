import pytest

from archiving.rules.support.filters import support_filters


class _FakeLocalCtx:
    def __init__(self, config):
        self.config = config


@pytest.mark.config(
    CHATTERBOX_STATUSES_FOR_ARCHIVATION=['archived', 'exported'],
)
@pytest.mark.parametrize(
    'doc, expected',
    [
        ({'status': 'archived'}, True),
        ({'status': 'not_ready'}, False),
        ({'status': 'exported'}, True),
    ],
)
def test_chatterbox_filter(cron_context, doc, monkeypatch, expected):
    local_ctx = _FakeLocalCtx(cron_context.config)
    chatterbox_filter = support_filters.SupportChatterboxFilter(
        local_ctx, None, None,
    )
    assert chatterbox_filter.can_be_removed(doc) == expected


@pytest.mark.parametrize(
    'doc, expected',
    [
        ({'open': True, 'visible': True}, False),
        ({'open': False, 'visible': True}, False),
        ({'open': True, 'visible': False}, False),
        ({'open': False, 'visible': False}, True),
    ],
)
def test_user_chat_messages_filter(cron_context, doc, monkeypatch, expected):
    local_ctx = _FakeLocalCtx(cron_context.config)
    user_chat_messages_filter = support_filters.UserChatMessagesFilter(
        local_ctx, None, None,
    )
    assert user_chat_messages_filter.can_be_removed(doc) == expected
