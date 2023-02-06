import re
import typing
from copy import deepcopy

import pytest

from django.db.models import Q

from l3mgr.utils.process_groups_legacy import process_groups as process_groups_old_method
from l3mgr.utils.process_groups import process_groups as process_groups_new_method, RealServer


already_existing_gencfg_groups = [
    "@mtn:MSK_MYT_BIGB_BALANCER_0/stable-125-r1606",
    "@mtn:SAS_BIGB_BALANCER_2/stable-125-r446",
    "@mtn:VLA_BIGB_BALANCER_1/stable-125-r446",
]
already_existing_gencfg_groups_plus_fqdn = [
    "@mtn:MSK_MYT_BIGB_BALANCER_0/stable-125-r1606",
    "@mtn:SAS_BIGB_BALANCER_2/stable-125-r446",
    "@mtn:VLA_BIGB_BALANCER_1/stable-125-r446",
    "sas1-1892-sas-test-rcssint-balancer-15200.gencfg-c.yandex.net=2a02:6b8:c08:2ea2:10b:52b1:0:3b60",
]

already_existing_gencfg_groups_plus_fqdn_exclude_groups = [
    "-@mtn:MSK_MYT_BIGB_BALANCER_0/stable-125-r1606",
    "-@mtn:SAS_BIGB_BALANCER_2/stable-125-r446",
    "@mtn:VLA_BIGB_BALANCER_1/stable-125-r446",
    "sas1-1892-sas-test-rcssint-balancer-15200.gencfg-c.yandex.net=2a02:6b8:c08:2ea2:10b:52b1:0:3b60",
]

already_existing_racktables_and_conductor_groups = ["$kino-bko", "%kino-test-back"]

# RS from %taxi_api group has changed IP from '2a02:6b8:c02:d62:0:1315:b23f:f249' to '2a02:6b8:c02:7c6:0:1315:603f:f249'
# So it should be added to DB
already_existing_conductor_groups_but_host_changed_ip__plus__existing_fqdn = [
    "%taxi_api",
    "taxi-api07h.taxi.yandex.net=2a02:6b8:c02:428:0:1315:20ad:447b",
]

exclude_fqdn_as_group = {"@mtn:MSK_MYT_BIGB_BALANCER_0/stable-125-r1606"}
exclude_fqdn_as_group_and_groups_not_matching_input_groups = {"@hbf:SAS_SANITIZER"}
exclude_fqdn_as_fqdn = {
    "sas1-1892-sas-test-rcssint-balancer-15200.gencfg-c.yandex.net=2a02:6b8:c08:2ea2:10b:52b1:0:3b60"
}

groups_to_delete_during_test = ["@hbf:SAS_SANITIZER"]

incorrect_gencfg_group = ["@incorrect"]
incorrect_fqdn = ["incorrect"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fqdns,ipv6only,exclude_fqdn,groups_to_delete_during_test",
    [
        # TESTS WITHOUT DATABASE UPDATE
        # test gencfg groups already existing in DB
        (already_existing_gencfg_groups, True, None, None),
        # test gencfg groups and fqdn already existing in DB
        (already_existing_gencfg_groups_plus_fqdn, True, None, None),
        # test gencfg groups and fqdn already existing in DB and exclude parameter "-" is in input
        (already_existing_gencfg_groups_plus_fqdn_exclude_groups, True, None, None),
        # test gencfg groups and fqdn already existing in DB
        # and exclude parameter "-" is in input. Also set ipv6only to False
        (already_existing_gencfg_groups_plus_fqdn_exclude_groups, False, None, None),
        # test gencfg groups and fqdn already existing in DB
        # and exclude parameter "-" is in input. Also set ipv6only to False
        (already_existing_gencfg_groups_plus_fqdn_exclude_groups, False, deepcopy(exclude_fqdn_as_group), None),
        # test gencfg groups and fqdn already existing in DB
        # and exclude parameter "-" is in input. Also set ipv6only to False
        (
            already_existing_gencfg_groups_plus_fqdn_exclude_groups,
            False,
            deepcopy(exclude_fqdn_as_group_and_groups_not_matching_input_groups),
            None,
        ),
        # # test gencfg groups and fqdn already existing in DB
        # # and exclude parameter "-" is in input. Also set ipv6only to False
        # # Also, add fqdn to exclude
        # # It seems like a bug in old method https://paste.yandex-team.ru/1029542
        # (already_existing_gencfg_groups_plus_fqdn_exclude_groups, False, deepcopy(exclude_fqdn_as_fqdn), None),
        # # test gencfg groups and fqdn already existing in DB
        # # and exclude parameter "-" is in input. Also set ipv6only to False
        # # Also, add fqdn and group to exclude
        # # It seems like the same bug in old method https://paste.yandex-team.ru/1029559
        # (already_existing_gencfg_groups_plus_fqdn_exclude_groups, False, deepcopy(exclude_fqdn_as_group) | exclude_fqdn_as_fqdn, None),
        # test conductor and racktables groups already existing in DB
        (already_existing_racktables_and_conductor_groups, True, None, None),
        # TESTS WITH DATABASE UPDATE
        # RS from %taxi_api group has changed IP from '2a02:6b8:c02:d62:0:1315:b23f:f249' to '2a02:6b8:c02:7c6:0:1315:603f:f249'
        # So it should be added to DB
        (already_existing_conductor_groups_but_host_changed_ip__plus__existing_fqdn, True, None, None),
        # test gencfg groups and fqdn already existing in DB + new gencfg groups
        (
            already_existing_gencfg_groups_plus_fqdn + groups_to_delete_during_test,
            True,
            None,
            groups_to_delete_during_test,
        ),
        # test gencfg groups and fqdn already existing in DB
        # + new gencfg groups + exclude_groups and ipv6only is False
        (
            already_existing_gencfg_groups_plus_fqdn_exclude_groups + groups_to_delete_during_test,
            False,
            deepcopy(exclude_fqdn_as_group),
            groups_to_delete_during_test,
        ),
    ],
)
def test_process_groups_success_cases(
    fqdns: typing.Iterable[str],
    ipv6only: bool,
    exclude_fqdn: typing.Iterable[str],
    groups_to_delete_during_test: typing.Iterable[str],
    django_db_setup,
) -> None:
    if groups_to_delete_during_test:
        delete_groups(groups_to_delete_during_test)
    most_recent_rs_id = RealServer.objects.last().id

    ids_new_method, groups_new_method = process_groups_new_method(fqdns, ipv6only=ipv6only, ex_fqdn=exclude_fqdn)
    ids_already_exist_new_method, ids_added_in_db_new_method = get_ids_added_to_db_and_already_existing_in_db(
        ids_new_method, most_recent_rs_id
    )

    rs_objects_new_method = get_rs_by_ids(ids_new_method)

    if ids_added_in_db_new_method:
        delete_created_ids(ids_added_in_db_new_method)

    ids_old_method, groups_old_method = process_groups_old_method(fqdns, ipv6only=ipv6only, ex_fqdn=exclude_fqdn)
    ids_already_exist_old_method, ids_added_in_db_old_method = get_ids_added_to_db_and_already_existing_in_db(
        ids_old_method, most_recent_rs_id
    )

    rs_objects_old_method = get_rs_by_ids(ids_old_method)

    if ids_added_in_db_old_method:
        delete_created_ids(ids_added_in_db_old_method)

    assert sorted(rs_objects_new_method) == sorted(rs_objects_old_method)
    assert sorted(groups_new_method) == sorted(groups_old_method)


def delete_groups(groups_to_delete_during_test: typing.Iterable[str]) -> None:
    temp_delete = RealServer.objects.filter(group__in=groups_to_delete_during_test)
    delete_result = temp_delete.delete()
    print("DELETED: {}".format(delete_result))


def delete_created_ids(ids_added_in_db: typing.Iterable[int]) -> None:
    temp_delete = RealServer.objects.filter(id__in=ids_added_in_db)
    delete_result = temp_delete.delete()
    print("DELETED: {}".format(delete_result))


def get_ids_added_to_db_and_already_existing_in_db(
    ids: typing.Iterable[int], most_recent_rs_id: int
) -> typing.Tuple[typing.List[int], typing.List[int]]:
    ids = sorted(ids)

    for n, _id in enumerate(ids):
        if _id > most_recent_rs_id:
            return ids[:n], ids[n:]
    else:
        return [ids], []


def get_rs_by_ids(ids: typing.Iterable[int]) -> typing.List[RealServer]:
    query_filter = Q(pk__isnull=True)

    for _id in ids:
        query_filter |= Q(id=_id)

    real_servers = (
        RealServer.objects.filter(query_filter)
        .order_by("fqdn")
        .distinct("fqdn")
        .values_list("fqdn", "ip", "group", "config", "location")
    )

    return list(real_servers)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fqdns,ipv6only,ex_fqdn,groups_to_delete_during_test,expected",
    [
        # incorrect gencfg groups
        (
            incorrect_gencfg_group,
            True,
            None,
            None,
            pytest.raises(Exception, match='Gencfg group "@incorrect" not found'),
        ),
        # incorrect fqdn and correct groups
        (
            incorrect_fqdn + already_existing_gencfg_groups,
            True,
            None,
            None,
            pytest.raises(
                Exception, match=re.escape("Failed to resolve incorrect: [Errno -2] Name or service not known")
            ),
        ),
        # Missing input group
        (None, True, None, None, pytest.raises(Exception, match="'NoneType' object is not iterable")),
        # short group name
        (["f"], True, None, None, pytest.raises(Exception, match='Incorrect fqdn "f"')),
    ],
)
def test_process_groups_error_cases(
    fqdns: typing.Iterable[str],
    ipv6only: bool,
    ex_fqdn: typing.Iterable[str],
    groups_to_delete_during_test: typing.Iterable[str],
    expected,
    django_db_setup,
) -> None:
    with expected:
        process_groups_new_method(fqdns, ipv6only=ipv6only, ex_fqdn=ex_fqdn)
    with expected:
        process_groups_old_method(fqdns, ipv6only=ipv6only, ex_fqdn=ex_fqdn)
