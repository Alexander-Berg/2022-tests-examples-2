import pytest

from taxi.core import async
from taxi.external import staff as external_staff
from taxi.internal import staff


@pytest.inline_callbacks
def test_get_staff_by_yandex_team_login(patch):
    user = yield staff.get_staff_by_yandex_team_login('foo.bar')
    assert user._id == 'id-foo-bar'

    user = yield staff.get_staff_by_yandex_team_login('foo-bar')
    assert user._id == 'id-foo-bar'

    user = yield staff.get_staff_by_yandex_team_login('unknown-user')
    assert not user._id


@pytest.inline_callbacks
def test_get_staff_by_yandex_login(patch):
    @patch('taxi.external.staff.search_staff_by_yandex_login')
    @async.inline_callbacks
    def staff_by_yandex_login(yandex_login, **unused):
        raise external_staff.StaffNotFoundError()

    # Well known user
    for login_variant in ['well-known-yandex-user', 'well.known.yandex.user']:
        user = yield staff.get_staff_by_yandex_login(login_variant)
        assert user._id == 'id-well-known-user'
        assert user.yandex_team_login == 'well-known-team-user'
        assert user.yandex_login == 'well-known-yandex-user'
        assert user.admin_groups == ['foo', 'bar']
        assert user.access_to_cabinet
        assert user.admin_superuser

    # Unknown user
    for login_variant in ['unknown-yandex-user', 'unknown.yandex.user']:
        user = yield staff.get_staff_by_yandex_login(login_variant)
        assert not user._id
        assert not user.yandex_team_login
        assert user.admin_groups == []
        assert not user.access_to_cabinet
        assert not user.admin_superuser
