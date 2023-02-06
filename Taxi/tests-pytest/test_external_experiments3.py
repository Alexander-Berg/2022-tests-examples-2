import json
import pytest

from taxi.conf import settings
from taxi.external import experiments3


@pytest.mark.parametrize(
    'args, status_code, expected_exception',
    [
        (
            [
                experiments3.ExperimentsArg(
                    'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
                ),
            ],
            200,
            None,
        ),
        (
            [
                experiments3.ExperimentsArg(
                    'version', 'application_version', '1.2.3.4.5',
                ),
            ],
            200,
            None,
        ),
        (
            [
                experiments3.ExperimentsArg(
                    'version', 'application_version', 'qwe.2.3.4.5',
                ),
            ],
            None,
            experiments3.Experiments3BadArguments,
        ),
        (
            [
                experiments3.ExperimentsArg(
                    'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
                ),
            ],
            400,
            experiments3.Experiments3ClientError,
        ),
        (
            [
                experiments3.ExperimentsArg(
                    'user_id', 'string', '8395bc9f652addd8fa174f64a0b4d848',
                ),
            ],
            500,
            experiments3.Experiments3RequestError,
        ),
    ]
)
@pytest.inline_callbacks
def test_get_values(args, status_code, expected_exception, areq_request,
                    monkeypatch):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert kwargs['headers']['YaTaxi-Api-Key'] == 'secret'
        if status_code is not None and status_code == 200:
            return areq_request.response(
                status_code, body=json.dumps(
                    {'items': [
                        {
                            'name': 'experiment_1',
                            'value': {
                                'key_1': 'value_1',
                                'key_2': 'value_2',
                            },
                        },
                    ]},
                )
            )
        else:
            return areq_request.response(status_code, body=json.dumps({}))

    monkeypatch.setattr(settings, 'TAXI_EXPERIMENTS3_API_TOKEN', 'secret')

    if expected_exception is None:
        result = yield experiments3.get_values('launch', args)
    else:
        with pytest.raises(expected_exception):
            result = yield experiments3.get_values('launch', args)

    if status_code is None:
        assert not requests_request.calls
    elif status_code == 200:
        assert len(requests_request.calls) == 1
        assert result == [
            experiments3.ExperimentsValue('experiment_1', {
                'key_1': 'value_1',
                'key_2': 'value_2',
            })
        ]
    elif status_code < 500:
        assert len(requests_request.calls) == 1
    else:
        assert len(requests_request.calls) == experiments3.DEFAULT_RETRIES
