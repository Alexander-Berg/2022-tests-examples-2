# coding: utf-8

import pytest
import datetime as dt

import sandbox.common.types.user as ctu

import sandbox.web.server.request
from sandbox.yasandbox.database import mapping


def _user(login, is_robot=False):
    import sandbox.yasandbox.controller.user as controller
    controller.User.validated(login, is_robot=is_robot)
    return login


@pytest.fixture()
def group_obj(group_controller):
    return group_controller.create(mapping.Group(name='GROUP', users=[_user('default-group-user1')], email='mail'))


class TestUserController:
    """
    Show some usecases for User Controller
    """

    def test__allowed_api_methods(self, user_controller):
        """
        grant user access to restricted api methods
        """
        login = 'test_user'
        user_controller.create(mapping.User(login=login))
        # add method
        user_controller.add_allowed_api_method(login, 'client_ping')
        # ok
        assert user_controller.can_execute_api_method(login, 'client_ping') is True
        # invalid login
        assert user_controller.can_execute_api_method('invalid', 'client_ping') is False
        # invalid method
        assert user_controller.can_execute_api_method(login, 'client_started') is False

    def test__valid__existent(self, user_controller):
        login = 'test_user'
        user_controller.create(mapping.User(login=login, staff_validate_timestamp=dt.datetime.utcnow()))
        assert user_controller.valid(login)

    def test__valid__non_existent(self, user_controller):
        login = 'test_user'
        assert not user_controller.valid(login)

    def test__valid__old(self, user_controller):
        login = 'test_user'
        user_controller.create(
            mapping.User(
                login=login,
                staff_validate_timestamp=(
                    dt.datetime.utcnow() - dt.timedelta(days=user_controller.STAFF_CHECK_TTL) + dt.timedelta(hours=1)
                )
            )
        )
        assert user_controller.valid(login)

    def test__valid__outdated(self, user_controller):
        login = 'test_user'
        user_controller.create(
            mapping.User(
                login=login,
                staff_validate_timestamp=(
                    dt.datetime.utcnow() - dt.timedelta(days=user_controller.LONG_TERM_STAFF_TTL)
                )
            )
        )
        assert not user_controller.valid(login)

    def test__staff_info(self, user_controller, monkeypatch):
        import yasandbox.controller.user

        login = 'test_user'
        user_controller.create(
            mapping.User(
                login=login,
                staff_validate_timestamp=(
                    dt.datetime.utcnow() - dt.timedelta(days=user_controller.LONG_TERM_STAFF_TTL)
                )
            )
        )
        telegram_login = "test_user_telegram_login"
        StaffInfo = yasandbox.controller.user.User.StaffInfo
        monkeypatch.setattr(
            yasandbox.controller.user.User, "validate_login",
            classmethod(
                lambda cls, login, **__: StaffInfo(
                    login=login, telegram_login=telegram_login, uid="1120000000000000"
                )
            )
        )
        user_controller.validate(login)
        assert user_controller.valid(login)
        user = user_controller.get(login)
        assert user.telegram_login == telegram_login
        assert user.uid == "1120000000000000"

    def test__validate__existent(self, user_controller):
        login = 'test_user'
        user_controller.create(mapping.User(login=login, staff_validate_timestamp=dt.datetime.utcnow()))
        user_controller.validate(login)
        assert user_controller.valid(login)

    def test__validate__existent_by_uid(self, user_controller):
        uid = "1120000000000000"
        login = "test_user"
        user_controller.create(
            mapping.User(login=login, staff_validate_timestamp=dt.datetime.utcnow(), uid=uid)
        )
        user_controller.validate_from_uid(uid)
        assert user_controller.valid(login)

    def test__get_user_by_oauth_token__existent(self, oauth_controller):
        login = 'test_user'
        token = 'test_token'
        oauth_controller.refresh(login, token)
        assert login == oauth_controller.get(token).login

        token = 'test_token2'
        oauth_controller.refresh(login, token)
        assert token == oauth_controller.get(token).token
        assert oauth_controller.Model.objects(login=login).count() == 2

        token = 'test_token3'
        oauth_controller.refresh(login, token, app_id="12345")
        assert token == oauth_controller.get(token).token
        assert oauth_controller.Model.objects(login=login).count() == 3

        token = 'test_token4'
        oauth_controller.refresh(login, token, source=ctu.TokenSource.SSH_KEY)
        assert login == oauth_controller.get(token).login
        assert oauth_controller.Model.objects(login=login).count() == 4

        token = 'test_token5'
        oauth_controller.refresh(login, token, app_id="12345")
        assert login == oauth_controller.get(token).login
        assert token == oauth_controller.get(token).token
        assert oauth_controller.Model.objects(login=login).count() == 5

    def test__get_user_by_oauth_token__old(self, oauth_controller):
        login = 'test_user'
        token = 'test_token'
        oauth_controller.Model(
            login=login,
            token=token,
            source=ctu.TokenSource.PASSPORT,
            validated=dt.datetime.utcnow() - dt.timedelta(minutes=oauth_controller._validation_ttl - 1)
        ).save()
        assert login == oauth_controller.get(token).login

    def test__get_user_by_oauth_token_outdated_and_refresh(self, oauth_controller):
        login = 'test_user'
        token = 'test_token'
        oauth_controller.Model(
            login=login,
            token=token,
            source=ctu.TokenSource.PASSPORT,
            validated=dt.datetime.min
        ).save()
        assert oauth_controller.get(token) is None

        oauth_controller.refresh(login, token)
        assert token == oauth_controller.get(token).token
        assert oauth_controller.Model.objects(login=login).count() == 1

    def test__oauth_refresh_all(self, oauth_controller):
        caches = [
            oauth_controller.refresh("fake_user", "test_token"),
            oauth_controller.refresh("real_user", "test_token2"),
        ]

        for c in caches:
            c.validated = dt.datetime.min
            c.save()

        now = dt.datetime.utcnow()
        oauth_controller.refresh_all()
        assert all(
            [
                now - cache.validated < dt.timedelta(seconds=2)
                for cache in oauth_controller.Model.objects
            ]
        )

        exists = [_.login for _ in caches]
        oauth_controller.refresh_all(exists + ['freak_ouser'])
        assert sorted(exists) == sorted(oauth_controller.Model.objects.scalar('login'))

    def test__sessionid_cache(self, user_controller):
        login = 'test_user'
        user_controller.create(mapping.User(login=login))

        sid = u"58269de467984694b7662b6c3416ff03"  # unicode, as expected from Blackbox
        user_controller.set_session_id(login, sid)

        assert user_controller.get_login_by_sid(sid) == login
        assert not user_controller.get_login_by_sid('__invalid_sid__')


class TestGroupController:
    """
    Show some usecases for Group Controller
    """

    def test__create(self, group_controller):
        u = _user('user')
        g = group_controller.create(mapping.Group(name='GROUP', users=[u], email='mail'))
        assert g.name == 'GROUP'
        assert u in g.users
        assert g.email == 'mail'

    def test__create_with_robot_only(self, group_controller):
        u = _user('user')
        r = _user('robot', is_robot=True)
        with pytest.raises(ValueError):
            group_controller.create(mapping.Group(name='GROUP', users=[r]))
        g = group_controller.create(mapping.Group(name='GROUP', users=[u, r]))
        assert g.name == 'GROUP'
        assert set(g.users) == {u, r}

    def test__create__existent(self, group_controller, monkeypatch):
        import yasandbox.controller.user as user_controller
        monkeypatch.setattr(
            user_controller.User, "validate_login",
            classmethod(lambda *_, **__: True)
        )
        u = _user('user')
        group_controller.create(mapping.Group(name='GROUP', users=[u], email='mail'))
        pytest.raises(ValueError, group_controller.create, mapping.Group(
            name='GROUP', users=[_user('user2')], email='mail2'
        ))

    def test__edit(self, group_controller, group_obj):
        u = _user('user2')
        g = group_controller.edit(mapping.Group(name=group_obj.name, users=[u], email='mail2'))
        assert u in g.users
        assert g.email == 'mail2'

    def test__edit_with_robot_only(self, group_controller, group_obj):
        u = _user('user')
        r = _user('robot', is_robot=True)
        with pytest.raises(ValueError):
            group_controller.edit(mapping.Group(name=group_obj.name, users=[r]))
        g = group_controller.edit(mapping.Group(name=group_obj.name, users=[u, r]))
        assert set(g.users) == {u, r}

    def test__edit__nonexistent(self, group_controller):
        pytest.raises(ValueError, group_controller.edit, mapping.Group(
            name='GROUP', users=[_user('user')], email='mail'
        ))

    def test__get(self, group_controller, group_obj):
        g = group_controller.get('GROUP')
        assert g.name == 'GROUP'
        assert group_obj.users[0] in g.users
        assert g.email == 'mail'

    def test__get__nonexistent(self, group_controller):
        pytest.raises(ValueError, group_controller.get, 'GROUP')

    def test__exists(self, group_controller, group_obj):
        assert group_controller.exists(group_obj.name)

    def test__exists__nonexistent(self, group_controller):
        assert not group_controller.exists('NONE')

    def test__list(self, group_controller):
        u = _user('user')
        g1 = group_controller.create(mapping.Group(name='GROUP1', users=[u], email='mail'))
        g2 = group_controller.create(mapping.Group(name='GROUP2', users=[u], email='mail'))
        res = group_controller.list()
        assert len(res) == 2
        assert res[0].name == g1.name
        assert res[1].name == g2.name

    def test__unpack(self, group_controller):
        u1, u2, u3, u4, u5 = (_user("user" + str(i)) for i in xrange(5))
        g1 = group_controller.create(mapping.Group(name='GROUP1', users=[u1, u2], email='mail'))
        g2 = group_controller.create(mapping.Group(name='GROUP2', users=[u2, u3], email='mail'))
        res = group_controller.unpack([g1.name, u5, g2.name])
        assert set(res) == set([u1, u2, u3, u5])

    def test__get_user_groups(self, group_controller):
        u1, u2, u3 = (_user('user' + str(i)) for i in xrange(3))
        group_controller.create(mapping.Group(name='GROUP1', users=[u1, u2], email='mail'))
        group_controller.create(mapping.Group(name='GROUP2', users=[u2, u3], email='mail'))
        group_controller.create(mapping.Group(name='GROUP3', users=[u3], email='mail'))
        res = group_controller.get_user_groups(u3)
        assert 'GROUP1' not in res
        assert 'GROUP2' in res
        assert 'GROUP3' in res

    def test__delete(self, group_controller, group_obj):
        group_controller.delete('GROUP')
        pytest.raises(ValueError, group_controller.get, 'GROUP')

    def test__delete__nonexistent(self, group_controller):
        pytest.raises(ValueError, group_controller.delete, 'GROUP')

    def test__add_user(self, group_controller, group_obj):
        u = _user('user2')
        group_controller.add_user('GROUP', u)
        assert u in group_controller.get('GROUP').users

    def test__add_user__nonexistent(self, group_controller):
        pytest.raises(ValueError, group_controller.add_user, 'GROUP', 'user')

    def test__remove_user(self, group_controller, group_obj):
        group_controller.remove_user('GROUP', group_obj.users[0])
        assert 'user' not in group_controller.get('GROUP').users

    def test__remove_user__nonexistent_group(self, group_controller):
        pytest.raises(ValueError, group_controller.remove_user, 'GROUP', 'user')

    def test__remove_user__nonexistent_user(self, group_controller, group_obj):
        pytest.raises(ValueError, group_controller.remove_user, 'GROUP', 'user2')

    def test__change_email(self, group_controller, group_obj):
        group_controller.change_email('GROUP', 'mail2')
        assert group_controller.get('GROUP').email == 'mail2'

    def test__change_email__nonexistent(self, group_controller):
        pytest.raises(ValueError, group_controller.change_email, 'GROUP', 'mail2')

    def test__validate_abc(self, group_controller, monkeypatch):
        from sandbox import common

        def mock_response(_, path, params, *args, **kwargs):
            if params.get("slug") == "sandbox":
                return {"results": [{"id": 42}]}
            return {"results": []}

        monkeypatch.setattr(common.rest.Client, "read", mock_response)

        assert group_controller.validate_abc("????") is False

        assert group_controller.validate_abc("sandbox")

        assert group_controller.validate_abc("non-sandbox") is False

    def test__allowed_priority(self, user_controller, group_controller, group_obj):
        _SU_PL = ctu.SU_PRIORITY_LIMITS
        _PL = ctu.DEFAULT_PRIORITY_LIMITS

        request = sandbox.web.server.request.SandboxRequest(None, {}, "", "", "", ("https", "sb.y-t"))
        request.source = request.Source.WEB
        request.user = user_controller.get(group_obj.users[0])
        assert group_controller.allowed_priority(request, group_obj.name) == _PL.ui
        request.source = request.Source.RPC
        assert group_controller.allowed_priority(request, group_obj.name) == _PL.api
        request.source = request.Source.API
        request.token_source = ctu.TokenSource.PASSPORT
        assert group_controller.allowed_priority(request, group_obj.name) == _PL.api
        request.token_source = ctu.TokenSource.SSH_KEY
        assert group_controller.allowed_priority(request, group_obj.name) == _PL.ui.prev

        ui_tpl = _PL.ui.next
        api_tpl = _PL.api.next
        group_obj.priority_limits = mapping.Group.PriorityLimits(ui=int(ui_tpl), api=int(api_tpl))
        group_obj.save()
        request.token_source = None
        request.source = request.Source.WEB
        assert group_controller.allowed_priority(request, group_obj.name) == ui_tpl
        request.source = request.Source.API
        request.token_source = ctu.TokenSource.PASSPORT
        assert group_controller.allowed_priority(request, group_obj.name) == api_tpl
        request.token_source = ctu.TokenSource.SSH_KEY
        assert group_controller.allowed_priority(request, group_obj.name) == ui_tpl.prev

        request.token_source = None
        request.source = request.Source.WEB
        request.user = user_controller.create(mapping.User(login='su_user', super_user=True))
        assert group_controller.allowed_priority(request, group_obj.name) == _SU_PL.ui
        request.source = request.Source.API
        request.token_source = ctu.TokenSource.PASSPORT
        assert group_controller.allowed_priority(request, group_obj.name) == _SU_PL.api
