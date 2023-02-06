# pylint: disable=unused-variable
import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'


@pytest.fixture(name='mock_eda_candidates_list_by_ids')
def _mock_eda_candidates_list_by_ids(mockserver):
    @mockserver.json_handler('/eda-candidates/list-by-ids')
    def _handler_eda_candidates_list_by_ids(request):
        assert len(request.json['ids']) == 1
        mock_response = {'candidates': [{'position': [20.22, 10.11]}]}
        return mockserver.make_response(json=mock_response, status=200)


@pytest.mark.now('2020-10-28T18:20:00.00+00:00')
@pytest.mark.pgsql('eats_orders_tracking', files=['green_flow_payload.sql'])
@pytest.mark.experiments3(filename='exp3_banners.json')
@pytest.mark.parametrize(
    'param_eater,param_expected_banners',
    [
        pytest.param(
            'eater1',
            {
                'banners': [
                    {
                        'appLink': None,
                        'id': 2,
                        'images': [],
                        'kind': 'collection',
                        'payload': {'badge': {}},
                        'shortcuts': [],
                        'url': 'https://test-url-2',
                        'wide_and_short': [
                            {
                                'platform': 'mobile',
                                'theme': 'light',
                                'url': 'https://test-image-url-2',
                            },
                        ],
                    },
                ],
                'design': 'wide_and_short',
            },
            id='show_banner',
        ),
        pytest.param(
            'eater2',
            {
                'banners': [
                    {
                        'appLink': None,
                        'id': 1,
                        'images': [],
                        'kind': 'info',
                        'payload': {'badge': {}},
                        'shortcuts': [],
                        'url': 'https://test-url-1',
                        'wide_and_short': [
                            {
                                'platform': 'mobile',
                                'theme': 'light',
                                'url': 'https://test-image-url-1',
                            },
                        ],
                    },
                ],
                'design': 'wide_and_short',
            },
            id='show_rover',
        ),
        pytest.param('eater3', None, id='no_banner'),
    ],
)
async def test_banners(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_eda_candidates_list_by_ids,
        param_eater,
        param_expected_banners,
):
    headers = make_tracking_headers(eater_id=param_eater)
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=headers,
    )
    assert response.status_code == 200
    order = response.json()['payload']['trackedOrders'][0]

    if param_expected_banners is None:
        assert 'banners' not in order
    else:
        assert order['banners'] == param_expected_banners
