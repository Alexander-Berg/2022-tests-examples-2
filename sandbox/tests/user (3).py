import pytest

import yasandbox.api.xmlrpc.tests


@pytest.mark.usefixtures("server")
class TestGroup(yasandbox.api.xmlrpc.tests.TestXmlrpcBase):
    @staticmethod
    def __user(login):
        from yasandbox.database import mapping
        import yasandbox.controller.user as controller

        mapping.User(login=login).save()
        controller.User.validated(login)
        return login

    @classmethod
    def _group(cls, group_controller, name=None, users=None):
        if not name:
            name = 'group'
        from yasandbox.database import mapping
        return group_controller.create(mapping.Group(name=name, users=users or [cls.__user('user')], email='mail'))

    def test__list_groups(self, api_su_session, group_controller):
        g1, g2, g3 = (self._group(group_controller, name='g' + str(i)) for i in xrange(3))
        gr = api_su_session.list_groups()
        assert len(gr) == 5  # 2 groups from res_session and api_su_session
        assert g1.name in gr
        assert g2.name in gr
        assert g3.name in gr

    def test__create_group(self, api_su_session, group_controller):
        g = api_su_session.create_group('GROUP', 'mail', [self.__user('user')])
        assert g == 'GROUP'

    def test__delete_group(self, api_su_session, group_controller):
        g1, g2 = (self._group(group_controller, name='g' + str(i)) for i in xrange(2))
        gr = api_su_session.list_groups()
        assert len(gr) == 4  # 2 groups from res_session and api_su_session
        api_su_session.delete_group(g2.name)
        gr = api_su_session.list_groups()
        assert len(gr) == 3  # 2 groups from res_session and api_su_session
        assert g1.name in gr

    def test__get_group_users(self, api_su_session, group_controller):
        u1, u2, u3 = (self.__user('u' + str(i)) for i in xrange(3))
        g1 = self._group(group_controller, name='g1', users=[u1, u2])
        self._group(group_controller, name='g2', users=[u2, u3])
        us = api_su_session.get_group_users(g1.name)
        assert len(us) == 2
        assert u1 in us
        assert u2 in us

    def test__get_user_groups(self, api_su_session, group_controller):
        u1, u2, u3 = (self.__user('u' + str(i)) for i in xrange(3))
        g1 = self._group(group_controller, name='g1', users=[u1, u2])
        g2 = self._group(group_controller, name='g2', users=[u2, u3])
        gr = api_su_session.get_user_groups(u2)
        assert len(gr) == 2
        assert g1.name in gr
        assert g2.name in gr

    def test__add_user_to_group(self, api_su_session, group_controller):
        g = self._group(group_controller)
        u = self.__user('user2')
        api_su_session.add_user_to_group(g.name, u)
        us = api_su_session.get_group_users(g.name)
        assert len(us) == 2
        assert u in us

    def test__remove_user_from_group(self, api_su_session, group_controller):
        u1, u2 = (self.__user('user' + str(i)) for i in xrange(2))
        g = self._group(group_controller, users=[u1, u2])
        api_su_session.remove_user_from_group(g.name, u2)
        us = api_su_session.get_group_users(g.name)
        assert len(us) == 1
        assert u2 not in us
