import pytest


@pytest.fixture()
def check_yt_logging(testpoint):
    class Context:
        messages = []

    context = Context()

    @testpoint('yt_tracking_info_log')
    def _testpoint_yt_tracking_info_log(message):
        context.messages.append(message)

    return context
