import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.internal import parks_activation


@pytest.mark.config(
    API_OVER_DATA_WORK_MODE_EXTERNAL_CRITERION={
        '__default__': {'__default__': {}},
        'parks-activation-client': {
            '__default__': {},
            'admin': {
                'parks_activation_clusterization': {
                    'threshold': 25.0,
                    'old_way_on_default': True,
                },
            },
        }
    },
)
@pytest.mark.parametrize(
    'work_mode',
    ['oldway', 'dryrun', 'tryout', 'newway'],
)
@pytest.inline_callbacks
def test_context(patch, monkeypatch, areq_request, work_mode):
    monkeypatch.setattr(config.API_OVER_DATA_WORK_MODE, 'get', lambda: {
        '__default__': {'__default__': {}},
        'parks-activation-client': {
            '__default__': 'oldway',
            'admin': work_mode,
        }
    })

    @patch('taxi.external.parks_activation._request')
    @async.inline_callbacks
    def _request(*args, **kwargs):
        yield
        async.return_value({
            'parks_activation': [
                {
                    'park_id': '400302122323',
                    'data': {
                        'deactivated': True,
                        'deactivated_reason': 'low_balance',
                        'can_corp': False,
                        'can_coupon': True,
                    },
                }
            ],
        })

    use_old_value = work_mode in ['oldway', 'dryrun']
    parks = yield db.parks.find().run()
    assert len(parks) == 4
    pa_context = yield parks_activation.AdminContext().run(
        park_ids=(park['_id'] for park in parks),
    )
    for old_value in (True, False):
        assert pa_context.get_deactivated(
            park_id='400000127852',
            old_value=old_value,
        ) is old_value
        assert pa_context.get_deactivated(
            park_id='400302122323',
            old_value=old_value,
        ) is (old_value if use_old_value else True)
    assert pa_context.get_deactivated_reason(
        park_id='400302122323',
        old_value='unknown_reason',
    ) == ('unknown_reason' if use_old_value else 'low_balance')
    assert pa_context.get_req_corp(
        park_id='400302122323',
        old_value=True,
    ) == (True if use_old_value else False)
    assert pa_context.get_req_coupon(
        park_id='400302122323',
        old_value=False,
    ) is (False if use_old_value else True)
    request_calls = list(_request.calls)
    if work_mode != 'oldway':
        assert len(request_calls) == 1
        assert set(request_calls[0]['kwargs']['json']['ids_in_set']) == {
            '400001131210', '400302122323',
        }
    else:
        assert len(request_calls) == 0
