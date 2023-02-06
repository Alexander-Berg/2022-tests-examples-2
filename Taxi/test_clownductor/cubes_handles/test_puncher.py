import pytest


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'fqdn_from_service': True,
        'punch_network': True,
        'puncher_check_requests': True,
    },
)
@pytest.mark.parametrize(
    'cube_name, file_name',
    [
        ('MetaCubePunchBalancers', 'PunchStable.json'),
        ('MetaCubePunchBalancers', 'PunchCustom.json'),
        ('PunchFirewall', 'PunchFirewall.json'),
        ('PunchFirewall', 'PunchFirewall_with_ticket.json'),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_task_processor_puncher(
        load_json,
        patch,
        puncher_mockserver,
        mock_clowny_balancer,
        call_cube_handle,
        cube_name,
        file_name,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert True

    @mock_clowny_balancer('/v1/entry-points/fqdn/search/')
    async def search_fqdn(request):
        return {'fqdns': ['aa']}

    punch_mock = puncher_mockserver()

    json_data = load_json(file_name)
    await call_cube_handle(cube_name, json_data)

    if cube_name == 'MetaCubePunchBalancers':
        assert len(create_comment.calls) == 1
        assert search_fqdn.times_called == 1
        assert punch_mock.times_called == 4

    if cube_name == 'PunchFirewall':
        assert (
            len(create_comment.calls)
            == json_data['extras']['create_comment_calls']
        )
        assert punch_mock.times_called == 1
