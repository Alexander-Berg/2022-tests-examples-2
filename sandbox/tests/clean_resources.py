# coding: utf-8
import datetime as dt

import pytest

from sandbox.yasandbox.database import mapping
from sandbox.services.modules import clean_resources as clean_resources_module
from sandbox.yasandbox.manager.tests import _create_real_resource


@pytest.fixture()
def clean_resources(server):
    return clean_resources_module.CleanResources()


class TestCleanResources:

    @pytest.mark.usefixtures("client_manager", "resource_manager")
    def test__mark_old_resources(self, task_manager, clean_resources):
        _create_real_resource(task_manager)
        resources = [
            _create_real_resource(task_manager, {'attrs': {'ttl': 'inf'}}),
            _create_real_resource(task_manager, {'attrs': {'ttl': '30'}}),
            _create_real_resource(task_manager, {'attrs': {'ttl': '14'}}),
            _create_real_resource(task_manager, {'attrs': {'ttl': 7}}),
            _create_real_resource(task_manager, {'resource_type': 'TASK_LOGS'}),
            _create_real_resource(task_manager, {'attrs': {'released': 'stable'}}),
            _create_real_resource(task_manager),
        ]
        now = dt.datetime.utcnow()
        past = now - dt.timedelta(days=15)
        mapping.Resource.objects(
            id__in=[_.id for _ in resources]
        ).update(set__time__accessed=past, set__time__expires=past)
        expired, outdated, immortal = clean_resources._find_expired_resources()
        clean_resources._reset_expiration_on_resources(immortal)
        clean_resources._update_expiration_on_resources(outdated)
        clean_resources._delete_expired_resources(expired)
        assert sorted(_["_id"] for _ in expired) == sorted(_.id for _ in resources[2:])
        assert next(mapping.Resource.objects(id=resources[0].id).scalar('time__expires')) is None
        expires = next(mapping.Resource.objects(id=resources[1].id).scalar('time__expires'))
        assert now < expires < now + dt.timedelta(days=16)

    def test__expire_time_rounding(self, clean_resources):
        assert clean_resources._round_expire_time(None) is None

        expire_time = dt.datetime(2019, 1, 15, 10, 13, 0, 420000)
        assert clean_resources._round_expire_time(expire_time) == dt.datetime(2019, 1, 15, 10, 20, 0)

        expire_time = dt.datetime(2019, 1, 15, 10, 0, 0)
        assert clean_resources._round_expire_time(expire_time) == dt.datetime(2019, 1, 15, 10, 0, 0)

        expire_time = dt.datetime(2019, 1, 15, 10, 0, 1)
        assert clean_resources._round_expire_time(expire_time) == dt.datetime(2019, 1, 15, 10, 10, 0)
