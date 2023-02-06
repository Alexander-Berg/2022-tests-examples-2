import pytest

from taxi.clients import stq_agent


@pytest.mark.parametrize(
    ['park_id', 'driver_profile_id', 'return_code', 'stq_put_called'],
    (
        pytest.param('park_id', 'driver_profile_id', 200, True, id='ok'),
        pytest.param(None, None, 400, False, id='bad_request'),
    ),
)
async def test_add_driver_photo_stq_mds(
        web_app_client,
        mock,
        patch,
        park_id,
        driver_profile_id,
        return_code,
        stq_put_called,
):
    @mock
    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    input_params = {
        'mds_photo_path': '1138/bc4be874-757b-44bc-a10d-17bb7420f2b7',
        'park_id': park_id,
        'driver_profile_id': driver_profile_id,
    }
    response = await web_app_client.post(
        f'/driver-photos/v1/photos/upload_mds',
        params={'idempotency_key': 123456},
        json=input_params,
    )
    assert response.status == return_code
    if return_code == 200:
        content = await response.json()
        assert content == {}

    # Check the correct data was added to the STQ queue
    # pylint: disable=no-member
    if stq_put_called:
        call = stq_agent.StqAgentClient.put_task.call
        assert isinstance(call['kwargs'].pop('log_extra', None), dict)
        assert call['kwargs'] == {
            'park_id': 'park_id',
            'driver_profile_id': 'driver_profile_id',
            'source_type': 'MDS',
            'source': '1138/bc4be874-757b-44bc-a10d-17bb7420f2b7',
            'idempotency_key': '123456',
            'priority': 'taximeter',
        }
    # No more calls were made
    assert not stq_agent.StqAgentClient.put_task.call
