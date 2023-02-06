import pytest

from taxi_buildagent import slack_tools


def test_json_slack_errors_are_handled(monkeypatch, patch_requests):
    monkeypatch.setenv('SLACK_BOT_TOKEN', 'foo')

    @patch_requests(slack_tools.SLACK_POST_URL)
    def _handle_request(method, url, **kwargs):
        return patch_requests.response(
            200, json={'ok': False, 'error': 'fatal_error'},
        )

    with pytest.raises(slack_tools.SlackError, match='Slack request failed'):
        slack_tools.send_slack_message(
            'foobar', '{"this"; "that"}', slack_tools.COLOR_GOOD,
        )


def test_http_errors_are_handled(monkeypatch, patch_requests):
    monkeypatch.setenv('SLACK_BOT_TOKEN', 'foo')

    @patch_requests(slack_tools.SLACK_POST_URL)
    def _handle_request(method, url, **kwargs):
        return patch_requests.response(502, content='gateway timeout')

    with pytest.raises(
            slack_tools.SlackError,
            match='Slack returned error 502: gateway timeout',
    ):
        slack_tools.send_slack_message(
            'foobar', '{"this"; "that"}', slack_tools.COLOR_GOOD,
        )
