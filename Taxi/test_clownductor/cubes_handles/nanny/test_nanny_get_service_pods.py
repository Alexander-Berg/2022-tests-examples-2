import pytest

CUBE_NAME = 'NannyGetServicePods'


@pytest.fixture(name='nanny_yp_list_pods')
def _nanny_yp_list_pods(mockserver):
    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _handler(request):
        data = request.json
        assert data['cluster'] in ['MAN', 'VLA', 'SAS', 'IVA', 'MYT']
        if data['cluster'] in ['IVA', 'SAS']:
            return {'total': 0, 'pods': []}
        return {
            'total': 1,
            'pods': [
                {
                    'status': {
                        'agent': {
                            'iss': {
                                'currentStates': [{'currentState': 'ACTIVE'}],
                            },
                        },
                    },
                    'meta': {
                        'creationTime': '1628931000883990',
                        'id': f'{data["cluster"].lower()}-pod-id-1',
                    },
                },
            ],
        }

    return _handler


@pytest.mark.parametrize(
    'file_name', ['simple', 'only_active', 'empty_nanny_service'],
)
async def test_cube_handler(
        load_json,
        mockserver,
        nanny_mockserver,
        nanny_yp_list_pods,
        call_cube_handle,
        file_name,
):
    @mockserver.json_handler(
        '/client-nanny/v2/services/'
        'balancer_taxi_kitty_unstable/runtime_attrs/',
    )
    def _handler(request):
        assert request.method == 'GET'
        return {
            '_id': '5c26609053b7c34a9ad5a283f48ae03c79853d58',
            'content': {
                'instances': {
                    'yp_pod_ids': {
                        'pods': [
                            {'cluster': 'MYT', 'pod_id': 'myt-pod-id-1'},
                            {'cluster': 'VLA', 'pod_id': 'vla-pod-id-1'},
                            {'cluster': 'MAN', 'pod_id': 'man-pod-id-1'},
                        ],
                    },
                },
            },
        }

    await call_cube_handle(CUBE_NAME, load_json(f'{file_name}.json'))
