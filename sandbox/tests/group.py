import pytest
import httplib
import datetime as dt

import sandbox.web.response

import sandbox.common.types.misc as ctm
import sandbox.common.types.user as ctu
import sandbox.common.types.notification as ctn

import sandbox.yasandbox.database.mapping as mp
import sandbox.yasandbox
import yasandbox.controller.user
import yasandbox.controller.tests.user
import yasandbox.controller.dispatch

from sandbox.tests.common.abc import abc_simulator  # noqa


def _equal_groups(g1, *rest):
    def filt(group):
        return filter(None, (_.strip() for _ in group.split(",")))

    return all(sorted(filt(g1)) == sorted(filt(g2)) for g2 in rest)


class TestRESTAPIGroup(object):
    @pytest.mark.usefixtures("serviceq", "abc_simulator")
    def test__group_create(
        self, rest_session, rest_session2, rest_noauth_session,
        rest_session_login, rest_session_login2, group_controller, monkeypatch
    ):
        existing_users = list(map(
            yasandbox.controller.tests.user._user,
            [rest_session_login, rest_session_login2]
        ))
        for source in ctu.GroupSource:
            monkeypatch.setitem(yasandbox.controller.user.Group.SYNC_SOURCES, source, lambda x: [x])

        data = {
            "name": "TGROUP",
            "sources": [{"source": ctu.GroupSource.USER, "group": existing_users[0]}],
            "abc": "tgroup",
            "messenger_chat_id": "test_chat_id",
            "telegram_chat_id": "telegram_chat_id",
            "juggler_settings": {
                "default_host": "test.namespace",
                "default_service": "service",
                "checks": {
                    ctn.JugglerCheck.MDS_QUOTA_EXCEEDED: {
                        "host": "test_host",
                        "service": "test_service"
                    }
                }
            },
            "mds_strong_mode": True,
            "mds_transfer_resources": True
        }

        with pytest.raises(rest_session2.HTTPError) as ex:
            rest_session2.group(data)
        assert ex.value.status == httplib.FORBIDDEN

        with pytest.raises(rest_noauth_session.HTTPError) as ex:
            rest_noauth_session.group(data)
        assert ex.value.status == httplib.UNAUTHORIZED

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.group({})
        assert ex.value.status == httplib.BAD_REQUEST
        assert "name" in ex.value.response.json()["reason"], "Required field name not presented in reason msg."

        assert rest_session.group(data)
        group = group_controller.get(data["name"])
        assert group.name == data["name"]
        assert group.users == [rest_session_login]
        assert group.email is None
        assert len(group.sources) == 1
        assert group.sources[0]["source"] == data["sources"][0]["source"]
        assert group.sources[0]["group"] == data["sources"][0]["group"]
        assert group.messenger_chat_id == data["messenger_chat_id"]
        assert group.telegram_chat_id == data["telegram_chat_id"]
        assert group.juggler_settings["default_host"] == data["juggler_settings"]["default_host"]
        assert group.juggler_settings["default_service"] == data["juggler_settings"]["default_service"]
        assert len(group.juggler_settings["checks"]) == len(data["juggler_settings"]["checks"])
        assert (
            group.juggler_settings["checks"][ctn.JugglerCheck.MDS_QUOTA_EXCEEDED]["host"] ==
            data["juggler_settings"]["checks"][ctn.JugglerCheck.MDS_QUOTA_EXCEEDED]["host"]
        )
        assert (
            group.juggler_settings["checks"][ctn.JugglerCheck.MDS_QUOTA_EXCEEDED]["service"] ==
            data["juggler_settings"]["checks"][ctn.JugglerCheck.MDS_QUOTA_EXCEEDED]["service"]
        )
        assert group.mds_strong_mode == data["mds_strong_mode"]
        assert group.mds_transfer_resources == data["mds_transfer_resources"]

        with pytest.raises(rest_session.HTTPError) as ex:
            assert rest_session.group(data)
        assert ex.value.status == httplib.BAD_REQUEST
        assert "already exists" in ex.value.response.json()["reason"]

        data["name"] = "TGROUP2"
        data["email"] = "tgroup@yandex-team.ru"
        assert rest_session.group(data)
        group = group_controller.get(data["name"])
        assert group.email == data["email"]

        data["name"] = "TGROUP3"
        data["sources"] = [{"source": "QWER", "group": existing_users[1]}]
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.group(data)
        assert ex.value.status == httplib.BAD_REQUEST

        data["sources"][0]["source"] = ctu.GroupSource.STAFF
        assert rest_session.group(data)
        group = group_controller.get(data["name"])
        assert len(group.sources) == 2
        assert group
        assert group.sources[0].source == ctu.GroupSource.USER
        assert group.sources[0].group == rest_session_login
        assert group.sources[1].source == ctu.GroupSource.STAFF
        assert group.sources[1].group == data["sources"][0]["group"]

    @pytest.mark.usefixtures("serviceq", "abc_simulator")
    def test__comma_separated_usernames_and_groups(
        self, rest_session, rest_session_login, monkeypatch,
        rest_session_login2, gui_su_session_login, group_controller
    ):
        external_users = map(
            yasandbox.controller.tests.user._user,
            ["user_{}".format(i) for i in xrange(1, 7)]
        )
        existing_users = map(
            yasandbox.controller.tests.user._user,
            [rest_session_login2, gui_su_session_login, rest_session_login]
        )

        def external_src_getter(group_name):
            if group_name in existing_users:
                return [group_name]
            return {
                "test1": external_users[0:3],
                "test2": external_users[3:]
            }.get(group_name, [])

        # imitate reply from Staff, which returns None for non-existent users
        staff_info = yasandbox.controller.user.User.StaffInfo(telegram_login="test_login")
        monkeypatch.setattr(
            yasandbox.controller.user.User, "validate_login",
            classmethod(lambda cls, login, **__: staff_info if login in external_users + existing_users else None)
        )
        for source in ctu.GroupSource:
            monkeypatch.setitem(
                yasandbox.controller.user.Group.SYNC_SOURCES, source, external_src_getter
            )

        sync_group_names = ["test1", "test2"]
        initial_groups = ", ".join(existing_users[2:])
        data = {
            "name": "TEST_GROUP",
            "abc": "test_group",
            "sources": [
                {"source": ctu.GroupSource.USER, "group": ", ".join([rest_session_login] + existing_users[0:2])},
                {"source": ctu.GroupSource.RB, "group": initial_groups}
            ]
        }

        group = rest_session.group(data)

        # for users, reflect changes in UI immediately
        assert set(group["members"]) == set([rest_session_login] + existing_users)
        assert _equal_groups(
            group["sync"]["group"],
            group["sources"][0]["group"],
            ", ".join(existing_users)
        )

        group = group_controller.get("TEST_GROUP")
        group.sources[0].group += ", test1"
        group_controller.sync(group)
        synced = group_controller.get("TEST_GROUP")
        assert set(synced.users) == set(existing_users + external_src_getter(sync_group_names[0]))

    @pytest.mark.usefixtures("serviceq", "abc_simulator")
    def test__group_get(
        self, rest_session, rest_su_session, rest_noauth_session,
        rest_session_login, rest_session_login2, monkeypatch
    ):
        existing_users = list(map(
            yasandbox.controller.tests.user._user,
            [rest_session_login, rest_session_login2]
        ))
        for source in ctu.GroupSource:
            monkeypatch.setitem(yasandbox.controller.user.Group.SYNC_SOURCES, source, lambda x: [x])

        existed_groups = rest_session.group[:10].get("items")
        existed_group_names = set(g.get("name") for g in existed_groups)
        data = {
            "name": "TGROUP",
            "email": "tgroup@yandex-team.ru",
            "abc": "tgroup",
            "sources": [
                {"source": ctu.GroupSource.RB, "group": existing_users[0]},
                {"source": ctu.GroupSource.USER, "group": existing_users[1]}
            ]
        }

        group = rest_session.group(data)
        group = rest_session.group[group["name"]][:]
        assert group["name"] == data["name"]
        assert set(group["members"]) == set(existing_users)
        assert group["email"] == data["email"]
        assert group["abc"] == data["abc"]

        assert group["sources"][0]["source"] == data["sources"][0]["source"]
        assert group["sources"][0]["group"] == data["sources"][0]["group"]
        assert group["sources"][1]["source"] == data["sources"][1]["source"]
        assert group["sources"][1]["group"] == data["sources"][1]["group"]

        assert group["rights"] == ctu.Rights.WRITE

        ret = rest_session.group[:10]
        assert ret["total"] == len(ret["items"]) == len(existed_group_names) + 1
        assert ret["limit"] == 10
        assert set(g["name"] for g in ret["items"]) == {"TGROUP"} | existed_group_names

        subgrp = {"name": "TGROUP2", "abc": "tgroup2", "members": [rest_session_login]}

        rest_session.group(subgrp)
        mp.Group.objects.with_id(subgrp["name"]).update(set__parent=group["name"])

        assert rest_session.group[subgrp["name"]][:]["parent"] == group["name"]

        ret = rest_session.group[:10]
        assert ret["total"] == len(ret["items"]) == len(existed_group_names) + 2
        assert ret["limit"] == 10
        assert set(g["name"] for g in ret["items"]) == {"TGROUP", "TGROUP2"} | existed_group_names

        ret = rest_session.group[1:10]
        assert ret["total"] == len(existed_group_names) + 2
        assert len(ret["items"]) == len(existed_group_names) + 1

        group_su = rest_su_session.group[group["name"]][:]
        assert group == group_su

        with pytest.raises(rest_noauth_session.HTTPError) as ex:
            rest_noauth_session.group[group["name"]].read()
        assert ex.value.status == httplib.UNAUTHORIZED

        ret = rest_session.group.read(name="TGROUP", limit=10)
        assert ret["total"] == len(ret["items"]) == 1
        assert ret["items"][0]["name"] == "TGROUP"

        ret = rest_session.group.read(parent="TGROUP", limit=10)
        assert ret["total"] == len(ret["items"]) == 1
        assert ret["items"][0]["parent"] == "TGROUP"
        assert ret["items"][0]["name"] == "TGROUP2"

        ret = rest_session.group.read(user=rest_session_login, limit=10)
        rest_session_existed_groups = set([g["name"] for g in existed_groups if rest_session_login in g["members"]])
        assert ret["total"] == len(ret["items"]) == 2 + len(rest_session_existed_groups)
        assert ret["limit"] == 10
        assert set(g["name"] for g in ret["items"]) == {"TGROUP", "TGROUP2"} | rest_session_existed_groups

        ret = rest_session.group.read(user="unknown_user", limit=10)
        assert ret["total"] == len(ret["items"]) == 0

        ret = rest_session.group.read(abc='tgroup', limit=10)
        assert ret["total"] == len(ret["items"]) == 1
        assert ret["items"][0]["name"] == "TGROUP"

        ret = rest_session.group.read(abc='tgroup2', limit=10)
        assert ret["total"] == len(ret["items"]) == 1
        assert ret["items"][0]["name"] == "TGROUP2"

    @pytest.mark.usefixtures("serviceq", "abc_simulator")
    def test__group_update(
        self, rest_session, rest_su_session, rest_noauth_session,
        rest_session_login, rest_su_session_login, group_controller, rest_session2, rest_session_login2
    ):
        data = {
            "name": "TGROUP", "sources": [{"source": ctu.GroupSource.USER, "group": rest_session_login}],
            "abc": "tgroup", "email": "tgroup@yandex-team.ru", "user_tags": ["USER_TEST1", "USER_TEST2"]
        }
        group = rest_session.group(data)
        ret = rest_session.group[group["name"]][:]
        assert ret["name"] == data["name"]
        assert sorted(ret["user_tags"]) == sorted(data["user_tags"])

        groups = rest_session.group.read(user_tag="USER_TEST1", limit=1)
        assert len(groups["items"]) == 1
        assert groups["items"][0]["name"] == "TGROUP"
        groups = rest_session.group.read(user_tag="USER_TEST3", limit=1)
        assert len(groups["items"]) == 0

        update_users = ", ".join([rest_session_login, rest_su_session_login])
        data_update = {
            "sources": [
                {"source": ctu.GroupSource.USER, "group": update_users}
            ],
            "abc": "tgroup",
            "messenger_chat_id": "test_chat",
            "telegram_chat_id": "test_telegram_char",
            "juggler_settings": {
                "default_host": "test.namespace",
                "default_service": "service",
                "checks": {
                    ctn.JugglerCheck.MDS_QUOTA_EXCEEDED: {
                        "host": "test_host",
                        "service": "test_service"
                    }
                }
            },
            "mds_strong_mode": True,
            "mds_transfer_resources": True
        }

        rest_session.group[group["name"]] = data_update
        ret = rest_session.group[group["name"]][:]
        assert sorted(ret["members"]) == sorted([rest_session_login, rest_su_session_login])
        assert ret["email"] == data["email"]
        updated_group = group_controller.get(data["name"])
        assert updated_group.messenger_chat_id == data_update["messenger_chat_id"]
        assert updated_group.telegram_chat_id == data_update["telegram_chat_id"]
        assert (
            updated_group.juggler_settings["default_host"] == data_update["juggler_settings"]["default_host"]
        )
        assert (
            updated_group.juggler_settings["default_service"] == data_update["juggler_settings"]["default_service"]
        )

        assert len(updated_group.juggler_settings["checks"]) == len(data_update["juggler_settings"]["checks"])
        assert (
            updated_group.juggler_settings["checks"][ctn.JugglerCheck.MDS_QUOTA_EXCEEDED]["host"] ==
            data_update["juggler_settings"]["checks"][ctn.JugglerCheck.MDS_QUOTA_EXCEEDED]["host"]
        )
        assert (
            updated_group.juggler_settings["checks"][ctn.JugglerCheck.MDS_QUOTA_EXCEEDED]["service"] ==
            data_update["juggler_settings"]["checks"][ctn.JugglerCheck.MDS_QUOTA_EXCEEDED]["service"]
        )
        assert group_controller.get(data["name"]).mds_strong_mode == data_update["mds_strong_mode"]
        assert group_controller.get(data["name"]).mds_transfer_resources == data_update["mds_transfer_resources"]

        header = rest_session.HEADERS({ctm.HTTPHeader.WANT_UPDATED_DATA: "1"})
        data_update = {
            "sources": [{"source": ctu.GroupSource.USER, "group": rest_session_login}]
        }
        new_data = (rest_session << header).group[group["name"]].update(data_update)
        assert new_data["members"] == [rest_session_login]
        assert data["email"] == new_data["email"]

        data_update = {"sources": [{"source": ctu.GroupSource.USER, "group": rest_su_session_login}]}
        rest_su_session.group[group["name"]].update(data_update)
        data_update = {"sources": [{"source": ctu.GroupSource.USER, "group": rest_session_login}]}
        rest_su_session.group[group["name"]].update(data_update)

        group_controller.Model(
            name="TGROUP2", users=[rest_session_login], user_tags=[group_controller.Model.UserTag(name="USER_TEST3")]
        ).save()

        update_user_tags = {"user_tags": ["USER_TEST1", "USER_TEST2", "USER_TEST3"]}
        with pytest.raises(rest_su_session.HTTPError) as ex:
            rest_su_session.group[group["name"]] = update_user_tags
        assert ex.value.status == httplib.BAD_REQUEST

        update_user_tags = {"user_tags": ["R_TEST1"]}
        with pytest.raises(rest_su_session.HTTPError) as ex:
            rest_su_session.group[group["name"]] = update_user_tags
        assert ex.value.status == httplib.BAD_REQUEST

        update_user_tags = {"user_tags": ["USER_Test"]}
        with pytest.raises(rest_su_session.HTTPError) as ex:
            rest_su_session.group[group["name"]] = update_user_tags
        assert ex.value.status == httplib.BAD_REQUEST

        data_update = {"sources": [{"source": ctu.GroupSource.USER, "group": rest_session_login}]}
        with pytest.raises(rest_noauth_session.HTTPError) as ex:
            rest_noauth_session.group[group["name"]] = data_update
        assert ex.value.status == httplib.UNAUTHORIZED

        data_update = {"sources": [{"source": ctu.GroupSource.USER, "group": rest_su_session_login}]}
        rest_su_session.group[group["name"]] = data_update
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.group[group["name"]] = data_update
        assert ex.value.status == httplib.FORBIDDEN

        data_update = {"sources": [{"source": "QWER", "group": rest_session_login}]}
        with pytest.raises(rest_su_session.HTTPError) as ex:
            rest_su_session.group[group["name"]] = data_update
        assert ex.value.status == httplib.BAD_REQUEST

        data_update = {"sources": [{"source": ctu.GroupSource.STAFF, "group": rest_session_login}]}
        rest_su_session.group[group["name"]] = data_update
        assert rest_su_session.group[group["name"]][:]["sources"][0]["source"] == data_update["sources"][0]["source"]
        assert rest_su_session.group[group["name"]][:]["sources"][0]["group"] == data_update["sources"][0]["group"]

        data_update = {
            "sources": [
                {"source": ctu.GroupSource.USER, "group": rest_session_login},
                {"source": ctu.GroupSource.USER, "group": rest_session_login2}
            ]
        }
        rest_su_session.group[group["name"]] = data_update

        data_update = {
            "abc": "tgroup",
            "email": "tgroup2@yandex-team.ru"
        }
        rest_session2.group[group["name"]] = data_update
        assert rest_su_session.group[group["name"]][:]["email"] == data_update["email"]

        data_update = {"abc": "tgroup2"}
        with pytest.raises(rest_session2.HTTPError) as ex:
            rest_session2.group[group["name"]] = data_update
        assert ex.value.status == httplib.FORBIDDEN

    @pytest.mark.usefixtures("serviceq", "abc_simulator")
    def test__group_delete(self, rest_session, rest_session_login, group_controller):
        data = {"name": "TGROUP", "abc": "tgroup", "members": [rest_session_login], "email": "tgroup@yandex-team.ru"}
        group = rest_session.group(data)

        ret = rest_session.group[:10]
        assert ret["total"] == len(ret["items"]) == 3  # 2 groups from rest_session and test_robot_api
        del rest_session.group[group["name"]]

        ret = rest_session.group[:10]
        assert ret["total"] == len(ret["items"]) == 2  # 2 groups from res_session and api_su_session

    @pytest.mark.usefixtures("group_controller", "abc_simulator")
    def test__create_with_dismissed(self, dispatched_rest_session, rest_session_login, monkeypatch):
        to_be_dismissed = ["first"]
        StaffInfo = yasandbox.controller.user.User.StaffInfo

        monkeypatch.setattr(
            yasandbox.controller.user.User, "validate_login",
            classmethod(lambda cls, login, **__: StaffInfo(is_dismissed=True, is_robot=True))
        )

        map(yasandbox.controller.user.User.validate, to_be_dismissed)
        data = {
            "name": "GROUP1",
            "abc": "group1",
            "members": to_be_dismissed + [rest_session_login],
            "email": "test_email@yandex-team.ru",
        }

        with pytest.raises(sandbox.web.response.HttpErrorResponse) as ex:
            dispatched_rest_session.group(data)
        assert ex.value.code == httplib.BAD_REQUEST

    @pytest.mark.usefixtures("group_controller", "serviceq", "abc_simulator")
    def test__update_with_dismissed(self, dispatched_rest_session, rest_session_login, monkeypatch):
        to_be_dismissed = ["first", "second", "third", "fourth"]
        StaffInfo = yasandbox.controller.user.User.StaffInfo

        monkeypatch.setattr(
            yasandbox.controller.user.User, "validate_login",
            classmethod(lambda cls, login, **__: StaffInfo(login=login))
        )

        map(yasandbox.controller.user.User.validate, to_be_dismissed)
        data = {
            "name": "GROUP1",
            "abc": "group1",
            "members": to_be_dismissed + [rest_session_login],
            "email": "test_email@yandex-team.ru",
        }
        dispatched_rest_session.group(data)
        members = dispatched_rest_session.group[data["name"]][:]["members"]
        assert set(members) == set(to_be_dismissed + [rest_session_login])

        # this should expire logins validation status, forcing server to re-validate them
        yasandbox.controller.User.Model.objects(login__in=to_be_dismissed).update(
            set__staff_validate_timestamp=dt.datetime.min
        )
        monkeypatch.setattr(
            yasandbox.controller.user.User, "validate_login",
            classmethod(lambda cls, login, **__: StaffInfo(is_dismissed=(login in to_be_dismissed)))
        )
        dispatched_rest_session.group[data["name"]].update(data)
        group = dispatched_rest_session.group[data["name"]][:]
        assert group["members"] == [rest_session_login]  # dismissed users which exist in the group are removed silently

        with pytest.raises(sandbox.web.response.HttpErrorResponse) as ex:
            dispatched_rest_session.group[data["name"]].update(data)  # dismissed users being added are causing an error
        assert ex.value.code == httplib.BAD_REQUEST

    @pytest.mark.usefixtures("serviceq", "abc_simulator")
    def test__group_parent_add(
        self, rest_session, rest_su_session, rest_noauth_session,
        rest_session_login, rest_session_login2
    ):
        group_data = {
            "name": "TGROUP",
            "email": "tgroup@yandex-team.ru",
            "abc": "tgroup",
        }

        rest_session.group(group_data)

        subgroup_data = {"name": "TGROUP2", "abc": "tgroup2", "members": [rest_session_login]}

        rest_session.group(subgroup_data)

        rest_su_session.group["TGROUP2"].parent.update(parent="TGROUP")

        tgroup2 = rest_session.group["TGROUP2"][:]

        assert tgroup2["parent"] == "TGROUP"
