import pytest


@pytest.fixture(name='driver_payment_types')
def _driver_payment_types(mockserver):
    class Context:
        def __init__(self):
            self.mock_payment_type = 'none'
            self.last_request = None
            self.bulk_retrieve = None

    ctx = Context()

    @mockserver.json_handler('/driver-payment-types/service/v1/bulk-retrieve')
    def _service_v1_bulk_retrieve(request):
        ctx.last_request = request.json

        assert request.json['source'] == 'subventions-events-filter'
        payment_types = ['none', 'online', 'cash']

        request_item = request.json['items'][0]

        result_item = {
            'park_id': request_item['park_id'],
            'driver_profile_id': request_item['driver_profile_id'],
        }

        if ctx.mock_payment_type is not None:
            payment_type_object = [
                {
                    'active': pt == ctx.mock_payment_type,
                    'available': True,
                    'payment_type': pt,
                }
                for pt in payment_types
            ]
            result_item['payment_types'] = payment_type_object

        return {'items': [result_item]}

    ctx.bulk_retrieve = _service_v1_bulk_retrieve

    return ctx


@pytest.fixture(name='candidate_meta')
def _candidate_meta(mockserver):
    class Context:
        def __init__(self):
            self.stored_data = None

    ctx = Context()

    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/update')
    def _candidate_meta_update(request):
        ctx.stored_data = request.json
        return {}

    return ctx


@pytest.fixture(name='candidates')
def mock_candidates(mockserver):
    class CandidatesContext:
        def __init__(self):
            self.profiles = {}
            self.mock_profiles = {}

        def load_profiles(self, profiles):
            self.profiles = profiles

    context = CandidatesContext()

    @mockserver.json_handler('/candidates/profiles')
    def _mock_profiles(request):
        doc = request.json
        assert 'payment_methods' in doc['data_keys']
        return context.profiles

    context.mock_profiles = _mock_profiles

    return context


def _make_sef_settings(get_pt_from='driver-payment-types'):
    return {
        'enabled': False,
        'bulk_size': 100,
        'fetch_payment_types_from': get_pt_from,
    }


PAYMENT_TYPE_TO_PAYMENT_METHOD = {
    'none': ['cash', 'card'],
    'cash': ['cash'],
    'online': ['card'],
}


@pytest.mark.parametrize(
    'determine_payment_type_by',
    [
        pytest.param(
            by,
            marks=[
                pytest.mark.config(
                    SUBVENTIONS_EVENTS_FILTER_STQ_SUBVENTIONS_NEW_DRIVER_FOUND={  # noqa: E501
                        'determine_payment_type_by': by,
                    },
                ),
            ],
        )
        for by in ['driver_point', 'point_a']
    ],
)
@pytest.mark.parametrize('payment_type', ['online', 'cash', 'none', None])
@pytest.mark.parametrize('get_pt_from_candidates', [True, False])
async def test_stq_subventions_new_driver_found(
        stq_runner,
        driver_payment_types,
        candidate_meta,
        candidates,
        payment_type,
        taxi_config,
        determine_payment_type_by,
        get_pt_from_candidates,
):
    driver_payment_types.mock_payment_type = payment_type
    if payment_type is not None:
        candidates.load_profiles(
            {
                'drivers': [
                    {
                        'dbid': 'dbid1',
                        'position': [37.5, 55.7],
                        'uuid': 'uuid1',
                        'payment_methods': PAYMENT_TYPE_TO_PAYMENT_METHOD[
                            payment_type
                        ],
                    },
                ],
            },
        )
    else:
        candidates.load_profiles({'drivers': []})

    if get_pt_from_candidates:
        taxi_config.set_values(
            dict(
                SUBVENTIONS_EVENTS_FILTER_SETTINGS=_make_sef_settings(
                    get_pt_from='candidates',
                ),
            ),
        )

    driver_point = [37.5, 55.7]
    point_a = [37.6, 55.8]

    await stq_runner.subventions_new_driver_found.call(
        task_id='task_id',
        kwargs={
            'clid_uuid': 'clid1_uuid1',
            'dbid': 'dbid1',
            'order_id': 'order1',
            'status': 'pending',
            'driver_point': driver_point,
            'point_a': point_a,
        },
    )

    if payment_type is not None:
        assert candidate_meta.stored_data == {
            'order_id': 'order1',
            'park_id': 'dbid1',
            'driver_profile_id': 'uuid1',
            'metadata': {'payment_type_restrictions': payment_type},
        }
    else:
        assert candidate_meta.stored_data is None

    if get_pt_from_candidates:
        assert candidates.mock_profiles.times_called == 1
        assert driver_payment_types.bulk_retrieve.times_called == 0
    else:
        assert candidates.mock_profiles.times_called == 0
        assert driver_payment_types.bulk_retrieve.times_called == 1

        request_position = driver_payment_types.last_request['items'][0][
            'position'
        ]
        if determine_payment_type_by == 'driver_point':
            assert request_position == driver_point
        else:
            assert request_position == point_a
