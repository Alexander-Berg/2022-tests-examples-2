import pytest


_REQUEST = {'user_id': 'user_id1', 'phone_id': 'phone_id1'}


@pytest.mark.parametrize(
    'uid,device_id,login_id,new_login_id',
    [
        ('yandex_uid1', 'device_id1', 'login_id1', 'login_id_new1'),
        ('yandex_uid2', None, 'login_id2', 'login_id_new2'),
    ],
)
async def test_base(
        taxi_uantifraud,
        mongodb,
        testpoint,
        uid,
        device_id,
        login_id,
        new_login_id,
):
    @testpoint('uafs_v1_events_protocol_launch_store_complete')
    def _uafs_v1_events_protocol_launch_store_complete_tp(_):
        pass

    request = {**_REQUEST, **{'yandex_uid': uid}}

    if device_id is not None:
        request['device_id'] = device_id

    async def make_request(req_login_id):
        return await taxi_uantifraud.post(
            '/v1/events/protocol/launch',
            json=request,
            headers={
                'X-YaTaxi-UserId': request['user_id'],
                'X-Yandex-UID': request['yandex_uid'],
                'X-Login-Id': req_login_id,
            },
        )

    def check_login_id_in_db(key, expected_login_id):
        assert (
            mongodb.antifraud_mdb_uuid_device_to_login_id_mapping.find_one(
                key,
            )['login_id']
            == expected_login_id
        )

    for local_login_id in (login_id, new_login_id):
        resp = await make_request(local_login_id)

        assert resp.status_code == 200
        assert resp.json() == {}

        assert (
            await _uafs_v1_events_protocol_launch_store_complete_tp.wait_call()
        )

        assert (
            mongodb.antifraud_mdb_uuid_device_to_login_id_mapping.count()
            == (2 if device_id is not None else 1)
        )

        check_login_id_in_db(request['yandex_uid'], local_login_id)

        if device_id is not None:
            check_login_id_in_db(
                f'{request["yandex_uid"]}_{device_id}', local_login_id,
            )
