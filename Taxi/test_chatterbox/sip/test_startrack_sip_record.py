import pytest


@pytest.mark.parametrize(
    'record_id, expected_status',
    [('0', 200), ('1', 200), ('2', 400), ('-1', 400)],
)
async def test_startrack_sip_record(cbox, record_id, expected_status):
    await cbox.query('/v1/startrek/sip_record/my_call/{}'.format(record_id))
    assert cbox.status == expected_status
    if expected_status == 200:
        assert (
            cbox.headers['X-Accel-Redirect']
            == '/telphin_record/telphin/storage/'
            'record-id_{}?disposition=inline'.format(record_id)
        )


async def test_not_permitted_sip_record(cbox, patch_auth):
    patch_auth(login='not_superuser', superuser=False)
    await cbox.query('/v1/startrek/sip_record/my_call_id/1')
    assert cbox.status == 403
    assert cbox.body_data == {
        'code': 'permission_forbidden',
        'message': 'User has no required permissions',
        'status': 'error',
    }
