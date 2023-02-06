import json
import pytest
import random
import httplib
import datetime as dt
import operator
import aniso8601
import itertools as it

from sandbox import common
import sandbox.common.types.resource as ctr

from sandbox.web import helpers

from sandbox.yasandbox.manager import tests
from sandbox.yasandbox.database import mapping


def check_updated(resource_id, updated, rest_session):
    last_updated = rest_session.resource[resource_id].read()["time"]["updated"]
    assert updated != last_updated
    return last_updated


class TestJSONAPIResource:
    def test__resources_list(self, rest_session, rest_su_session, task_manager, resource_manager):
        tasks = [tests._create_task(task_manager) for _ in xrange(3)]
        resources = [
            tests._create_resource(
                task_manager,
                task=tasks[0],
                create_logs=False,
                parameters={'resource_filename': 'resource_file{}'.format(i)})
            for i in xrange(5)]
        resources.extend(
            tests._create_resource(
                task_manager,
                task=tasks[1],
                create_logs=False,
                parameters={'resource_filename': 'resource_file{}'.format(i)})
            for i in xrange(4)
        )
        resources.append(tests._create_resource(
            task_manager,
            task=tasks[2],
            mark_ready=False,
            create_logs=False,
            parameters={'resource_type': 'OTHER_RESOURCE',
                        'resource_filename': 'other_file',
                        'attrs': {'attr1': 'value1', 'attr2': 'value2'}}
        ))

        first_res_time = dt.datetime.utcnow() - dt.timedelta(hours=1)
        resource_permutation = [i for i in range(len(resources))]
        random.shuffle(resource_permutation)
        rearranged_resources = [None] * len(resources)
        for index, resource in enumerate(resources):
            rearranged_resources[resource_permutation[index]] = resource
        for i, resource in enumerate(rearranged_resources):
            res_time = first_res_time + dt.timedelta(seconds=i)
            mapping.Resource.objects(id=resource.id).update(set__time__updated=res_time)

        ret = rest_session.resource.read(limit=100, order="updated")
        assert ret["total"] == len(ret["items"]) == len(rearranged_resources)
        for resource, response_resource in zip(rearranged_resources, ret["items"]):
            assert response_resource["id"] == resource.id

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource.read()
        assert ex.value.status == httplib.BAD_REQUEST

        ret = rest_session.resource[:100]
        assert ret['total'] == 10
        assert ret['limit'] == 100
        assert ret['offset'] == 0
        assert len(ret['items']) == 10

        assert all(res['rights'] == 'read' for res in ret['items'])
        assert all(
            res['rights'] == 'write' for res in
            rest_su_session.resource.read(limit=100)['items']
        )

        ret = rest_session.resource[:1]
        assert ret['total'] == 10
        assert ret['limit'] == 1
        assert ret['offset'] == 0
        assert len(ret['items']) == 1

        ret = rest_session.resource[7:5]
        assert ret['total'] == 10
        assert ret['limit'] == 5
        assert ret['offset'] == 7
        assert len(ret['items']) == 3

        ret = rest_session.resource[:100:'id']
        items = map(operator.itemgetter('id'), ret['items'])
        assert reduce(lambda a, b: b if a <= b else 0, items, 0)

        ret = rest_session.resource[:100:'-id']
        items = map(operator.itemgetter('id'), ret['items'])
        items.reverse()
        assert reduce(lambda a, b: b if a <= b else 0, items, 0)

        ret = rest_session.resource[{'state': 'NOT_READY,READY'}, : 100]
        assert ret['total'] == 10
        assert ret['limit'] == 100
        assert ret['offset'] == 0
        assert len(ret['items']) == 10

        ret = rest_session.resource[{'state': 'READY'}, : 100]
        assert ret['total'] == 9
        assert ret['limit'] == 100
        assert ret['offset'] == 0
        assert len(ret['items']) == 9

        ret = rest_session.resource[{'state': 'READY'}, : 2]
        assert ret['total'] == 9
        assert ret['limit'] == 2
        assert ret['offset'] == 0
        assert len(ret['items']) == 2

        ret = rest_session.resource[{'state': 'READY'}, : 2: "+id"]
        assert ret['total'] == 9
        assert ret['limit'] == 2
        assert ret['offset'] == 0
        assert len(ret['items']) == 2
        items = map(operator.itemgetter('id'), ret['items'])
        assert items == map(operator.attrgetter('id'), resources[:2])

        ret = rest_session.resource.read(state='READY', offset=2, limit=2, order="+id")
        assert ret['total'] == 9
        assert ret['limit'] == 2
        assert ret['offset'] == 2
        assert len(ret['items']) == 2
        items = map(operator.itemgetter('id'), ret['items'])
        assert items == map(operator.attrgetter('id'), resources[2:4])

        ret = rest_session.resource[{'type': 'OTHER_RESOURCE,TEST_TASK_RESOURCE'}, : 100]
        assert ret['total'] == 10
        assert ret['limit'] == 100
        assert ret['offset'] == 0
        assert len(ret['items']) == 10

        ret = rest_session.resource[{'type': 'OTHER_RESOURCE'}, : 100]
        assert ret['total'] == 1
        assert ret['limit'] == 100
        assert ret['offset'] == 0
        assert len(ret['items']) == 1

        ret = rest_session.resource[{'type': 'TEST_TASK_RESOURCE'}, : 100]
        assert ret['total'] == 9
        assert ret['limit'] == 100
        assert ret['offset'] == 0
        assert len(ret['items']) == 9

        ret = rest_session.resource[{'task_id': tasks[2].id}, : 100]
        assert ret['total'] == 1
        assert len(ret['items']) == 1

        ret = rest_session.resource[{'task_id': [tasks[0].id, tasks[1].id]}, : 100]
        assert ret['total'] == 9
        assert len(ret['items']) == 9

        ret = rest_session.resource[{'id': ','.join([str(o.id) for o in resources[:3]])}, : 100]
        assert ret['total'] == 3
        assert len(ret['items']) == 3

        ret = rest_session.resource[{'attrs': json.dumps({'attr1': 'value1'})}, : 100]
        assert ret['total'] == 1
        assert ret['limit'] == 100
        assert ret['offset'] == 0
        assert len(ret['items']) == 1

        ret = rest_session.resource[{'attrs': json.dumps({'attr1': 'value1', 'attr3': 'value3'})}, : 100]
        assert ret['total'] == 0
        assert ret['limit'] == 100
        assert ret['offset'] == 0
        assert len(ret['items']) == 0

        ret = rest_session.resource[{'attrs': json.dumps({'attr1': 'value1', 'attr3': 'value3'}), 'any_attr': 1}, : 100]
        assert ret['total'] == 1
        assert ret['limit'] == 100
        assert ret['offset'] == 0
        assert len(ret['items']) == 1

        number = 12345
        for f1, f2 in it.product([str, int], [str, int]):
            set_key, find_key = f1(number), f2(number)
            rid = tests._create_resource(
                task_manager, create_logs=False, parameters={"attrs": {"key": set_key}}
            ).id
            ret = rest_session.resource[{'attrs': json.dumps({"key": find_key})}, : 10]
            assert ret['items'] and ret['items'][0]["id"] == rid, \
                "Failed to find by {} attribute (set as {})".format(*map(type, (set_key, find_key)))

        for i, resource in enumerate(resources):
            res_time = first_res_time + dt.timedelta(seconds=i)
            mapping.Resource.objects(id=resource.id).update(time__accessed=res_time, time__created=res_time)

        def _make_interval(since, to):
            return "{}..{}".format(
                helpers.utcdt2iso(first_res_time + dt.timedelta(seconds=since)),
                helpers.utcdt2iso(first_res_time + dt.timedelta(seconds=to))
            )

        interval = _make_interval(1, len(resources) - 2)
        ret = rest_session.resource.read(accessed=interval, limit=100)
        assert ret["total"] == len(ret["items"]) == len(resources) - 2
        ret = rest_session.resource.read(created=interval, limit=100)
        assert ret["total"] == len(ret["items"]) == len(resources) - 2

        interval = _make_interval(-1, len(resources) + 1)
        ret = rest_session.resource.read(accessed=interval, limit=100)
        assert ret["total"] == len(ret["items"]) == len(resources)
        ret = rest_session.resource.read(created=interval, limit=100)
        assert ret["total"] == len(ret["items"]) == len(resources)

        ret = rest_session.resource.read(accessed=_make_interval(0, 4), created=_make_interval(2, 6), limit=100)
        assert ret["total"] == len(ret["items"]) == 3

    def test__resources_get(self, rest_session, task_manager, resource_manager):
        task = tests._create_task(task_manager)
        resources = []
        for i in xrange(10):
            resources.append(tests._create_resource(task_manager, task=task))

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[666].read()
        assert ex.value.status == httplib.NOT_FOUND

        for res in resources:
            ret = rest_session.resource[res.id][...]
            assert ret['id'] == res.id

    def test__resource_touch(self, rest_su_session, rest_session, task_manager, resource_manager):
        task = tests._create_task(task_manager, "SOME_OWNER")
        resource = tests._create_resource(task_manager, task=task)
        creation_time = dt.datetime.utcnow() - dt.timedelta(minutes=10)
        mapping.Resource.objects(id=resource.id).update(time__accessed=creation_time, time__created=creation_time)

        before_touch = dt.datetime.utcnow() - dt.timedelta(seconds=10)
        rest_session.resource[resource.id] = {}
        accessed = rest_su_session.resource[resource.id][...]["time"]["accessed"]
        assert creation_time < before_touch < aniso8601.parse_datetime(accessed).replace(tzinfo=None)

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[666] = {}
        assert ex.value.status == httplib.NOT_FOUND

    def test__resource_create_bad_ttl(self, rest_session, rest_session_login, task_manager, task_session):
        task = tests._create_task(task_manager, "SOME_OWNER")
        task_session(rest_session, task.id, rest_session_login)
        for val in ("-1", "0", "0.5", "qwerty", "1000000"):
            with pytest.raises(rest_session.HTTPError) as ex:
                rest_session.resource.create(
                    {
                        "description": "Resource with bad TTL",
                        "attributes": {"ttl": val},
                        "type": "TEST_RESOURCE",
                        "size": 1024 * 1024
                    }
                )
            assert ex.value.status == httplib.BAD_REQUEST and "TTL" in ex.exconly()

    def test__resource_create_update(
        self, rest_session, rest_session_login, rest_session_group, task_manager, task_session
    ):
        short_data = {
            "description": "Test1Resource",
            "attributes": {"k": "v", "kk": 11},
        }
        data = short_data.copy()
        data.update({"type": "TEST_RESOURCE"})
        tdata = short_data.copy()
        tdata["size"] = 1024 * 1024

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource(data)
        assert ex.value.status == httplib.FORBIDDEN
        assert "task session scope" in str(ex.value)

        task = tests._create_task(task_manager, owner=rest_session_group)
        resource = tests._create_resource(task_manager, task=task)

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[resource.id] = tdata
        assert ex.value.status == httplib.FORBIDDEN
        assert "task session scope" in str(ex.value)

        def validate_data(data_to_check, target, fields):
            for field in fields:
                target_value = target[field]
                if field == "attributes":
                    target_value = {k: str(v) for k, v in target_value.iteritems()}
                assert data_to_check[field] == target_value

        updated = rest_session.resource[resource.id].read()["time"]["updated"]

        rest_session.resource[resource.id] = {}
        assert updated == rest_session.resource[resource.id].read()["time"]["updated"]

        short_empty_data = {"description": "", "attributes": {}}
        rest_session.resource[resource.id] = short_empty_data
        validate_data(rest_session.resource[resource.id].read(), short_empty_data, short_empty_data)
        updated = check_updated(resource.id, updated, rest_session)

        rest_session.resource[resource.id] = short_data
        validate_data(rest_session.resource[resource.id].read(), short_data, short_data)
        check_updated(resource.id, updated, rest_session)

        task_session(rest_session, task.id, rest_session_login)

        broken = data.copy()
        broken.pop("type")
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource(broken)
        assert ex.value.status == httplib.BAD_REQUEST
        assert "type" in str(ex.value)
        # assert "required" in str(ex.value)  TODO:

        broken = data.copy()
        broken["type"] = "NOT_EXISTING_RESOURCE_TYPE"
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource(broken)
        assert ex.value.status == httplib.BAD_REQUEST
        assert "resource type" in str(ex.value)

        ret = rest_session.resource(data)
        data["state"] = ctr.State.NOT_READY
        assert ret["id"]
        validate_data(ret, data, ["type", "state", "description", "attributes"])

        data.update({
            "type": "SANDBOX_TEST_RESOURCE",
            "file_name": "myfile",
            "md5": "d41d8cd98f00b204e9800998ecf8427e",
            "skynet_id": "rbtorrent:da39a3ee5e6b4b0d3255bfef95601890afd80709",
            "description": "Test 1 Resource",
        })
        rest_session.resource[ret["id"]] = data
        ret = rest_session.resource[ret["id"]][:]
        assert ret["type"] == "TEST_RESOURCE"
        validate_data(ret, data, ["md5", "state", "file_name", "skynet_id", "attributes", "description"])

        data["state"] = ctr.State.READY
        rest_session.resource[ret["id"]] = data
        ret = rest_session.resource[ret["id"]][:]
        validate_data(ret, data, ["md5", "state", "file_name", "skynet_id"])

        data["description"] = "updated description"
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[ret["id"]] = data
        assert ex.value.status == httplib.BAD_REQUEST
        assert "is not allowed" in str(ex.value)

    def test__resource_create_observable(self, rest_session, rest_session_login, task_manager, task_session):
        task = tests._create_task(task_manager, "SOME_OWNER")
        task_session(rest_session, task.id, rest_session_login)
        observable_resources = [
            {
                "type": "TEST_RESOURCE",
                "file_name": "archive.tar.gz",
                "description": "test tar.gz",
            },
            {
                "type": "TEST_RESOURCE",
                "file_name": "archive.tgz",
                "description": "test tgz",
            },
            {
                "type": "TEST_RESOURCE",
                "file_name": "archive.tar",
                "description": "test tar",
            },
            {
                "type": "TEST_RESOURCE",
                "file_name": "dir",
                "description": "test dir",
                "multifile": True,
            }
        ]

        for item in observable_resources:
            result = rest_session.resource.create(item)
            assert "observable" in result.keys()
            assert result["observable"]

        not_observable = rest_session.resource.create({
            "type": "TEST_RESOURCE",
            "file_name": "archive.zip",
            "description": "test zip",
        })
        assert "observable" in not_observable.keys()
        assert not not_observable["observable"]

    def test__resource_with_mds(self, rest_session, rest_session_login, rest_session_group, task_manager, task_session):
        task = tests._create_task(task_manager, owner=rest_session_group)
        data = {
            "type": "TEST_RESOURCE",
            "file_name": "myfile1",
            "description": "test resource"
        }
        task_session(rest_session, task.id, rest_session_login)
        res_without_mds = rest_session.resource(data)
        assert res_without_mds["mds"] is None

        data["file_name"] = "myfile2"
        data["mds"] = {"key": "filename"}
        res_with_mds_default_namespace = rest_session.resource(data)
        assert "mds" in res_with_mds_default_namespace
        mds = res_with_mds_default_namespace["mds"]
        assert mds["key"] == data["mds"]["key"]
        assert res_with_mds_default_namespace["multifile"] is False
        assert res_with_mds_default_namespace["executable"] is False
        assert mds["namespace"] == ctr.DEFAULT_S3_BUCKET
        assert rest_session.resource[res_with_mds_default_namespace["id"]][:]["mds"] == mds

        data["file_name"] = "myfile3"
        data["mds"]["namespace"] = "custom_namespace"
        res_with_mds_custom_namespace = rest_session.resource(data)
        assert res_with_mds_custom_namespace["mds"]["namespace"] == data["mds"]["namespace"]

        update_data = {
            "mds": {"key": "filename2"}
        }
        rest_session.resource[res_without_mds["id"]] = update_data
        updated_res = rest_session.resource[res_without_mds["id"]][:]
        assert "mds" in updated_res
        mds = updated_res["mds"]
        assert mds["key"] == update_data["mds"]["key"]
        assert mds["namespace"] == ctr.DEFAULT_S3_BUCKET

    def test__resource_remodification(self, rest_session, rest_session_login, task_manager, task_session):
        task = tests._create_task(task_manager, "SOME_OWNER")
        resource = tests._create_resource(task_manager, mark_ready=False, task=task)
        task_session(rest_session, task.id, rest_session_login)

        data = {"attributes": {"k": "v", "kk": "123"}}
        rest_session.resource[resource.id] = data

        data["state"] = ctr.State.READY
        rest_session.resource[resource.id] = data

        data["attributes"]["kk"] = int(data["attributes"]["kk"])
        rest_session.resource[resource.id] = data

        data["description"] = "updated description"
        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[resource.id] = data
        assert ex.value.status == httplib.BAD_REQUEST

    def test__storage_insufficient_redundancy(
            self, rest_session, rest_su_session, task_manager, resource_manager, client_manager
    ):
        host1 = common.config.Registry().server.storage_hosts[0]
        host2 = common.config.Registry().server.storage_hosts[1]
        resources = [tests._create_resource(task_manager) for _ in xrange(3)]

        for res in resources:
            for host in set(res.get_hosts()):
                del rest_su_session.resource[res.id].source[host]
                assert host not in rest_su_session.resource[res.id].read()['sources']
            resource_manager.add_host(res.id, host1)

        resources.sort(key=lambda x: x.id)

        response = rest_session.resource[host1].insufficient_redundancy[:]
        assert len(response.get("items")) == 3
        assert response.get("total") == 3

        for res in resources:
            assert res.id in [redundancy_res["id"] for redundancy_res in response.get("items")]

        response = rest_session.resource[host1].insufficient_redundancy[1:1]

        assert len(response.get("items")) == 1
        assert response.get("limit") == 1
        assert response.get("offset") == 1
        assert response.get("items")[0].get("id") == resources[1].id
        assert response.get("total") == 3

        resource_manager.add_host(resources[0].id, host2)
        response = rest_session.resource[host1].insufficient_redundancy[:]
        assert len(response.get("items")) == 2
        assert response.get("total") == 2
        assert resources[0].id not in [redundancy_res["id"] for redundancy_res in response.get("items")]
        response = rest_session.resource[host2].insufficient_redundancy[:]
        assert len(response.get("items")) == 0
        assert response.get("total") == 0

        resource_manager.add_host(resources[1].id, host2)
        resource_manager.add_host(resources[2].id, host2)

        response = rest_session.resource[host1].insufficient_redundancy[:]
        assert len(response.get("items")) == 0
        assert response.get("total") == 0


class TestJSONAPIResourceAttribute:
    ATTRS = {
        'attr1': 'value1',
        'attr2': 'value2',
        'attr3': 'value3',
    }

    def test__resource_attribute_get(self, rest_session, task_manager, resource_manager):
        res = tests._create_resource(task_manager, parameters={"attrs": self.ATTRS})
        ret = rest_session.resource[res.id].attribute[:]
        assert {item['name']: item['value'] for item in ret} == self.ATTRS

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[666].attribute.read()
        assert ex.value.status == httplib.NOT_FOUND

    def test__resource_attribute_cast(self, rest_session, rest_session_group, task_manager, resource_manager):
        name = "numerical_attribute"
        casts = [str, int]

        for picked_casts in it.product(casts, casts, casts):
            res = tests._create_resource(task_manager, parameters={"owner": rest_session_group})
            set_key, find_key, update_key = [f(res.id) for f in picked_casts]

            rest_session.resource[res.id].attribute.create({"name": name, "value": set_key})
            items = rest_session.resource.read(attrs={name: find_key}, limit=10)["items"]
            assert len(items) == 1 and items[0]["id"] == res.id, \
                "Failed to find resource by created attribute (set as {}, sought as {})".format(set_key, find_key)

            rest_session.resource[res.id].attribute[name].update({"name": name, "value": update_key})
            items = rest_session.resource.read(attrs={name: find_key}, limit=10)["items"]
            assert len(items) == 1 and items[0]["id"] == res.id, \
                "Failed to find resource by updated attribute (updated as {}, sought as {})".format(set_key, find_key)

    def test__resource_attribute_create(self, rest_session, rest_session_group, task_manager, resource_manager):
        res = tests._create_resource(task_manager, parameters={"owner": rest_session_group})

        ret = rest_session.resource[res.id].attribute[:]
        assert ret == []

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[666].attribute(name='name', value='value')
        assert ex.value.status == httplib.NOT_FOUND

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[res.id].attribute('upyaka')
        assert ex.value.status == httplib.BAD_REQUEST

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[res.id].attribute(upyaka='upyaka')
        assert ex.value.status == httplib.BAD_REQUEST

        updated = rest_session.resource[res.id].read()["time"]["updated"]

        for name, value in self.ATTRS.iteritems():
            data = {'name': name, 'value': value}
            ret = rest_session.resource[res.id].attribute(data)
            assert ret == data
            updated = check_updated(res.id, updated, rest_session)

        ret = rest_session.resource[res.id].attribute[:]
        assert {item['name']: item['value'] for item in ret} == self.ATTRS

        for name, value in self.ATTRS.iteritems():
            data = {'name': name, 'value': value}
            with pytest.raises(rest_session.HTTPError) as ex:
                rest_session.resource[res.id].attribute(data)
            assert ex.value.status == httplib.CONFLICT
        ret = rest_session.resource[res.id].attribute[:]
        assert {item['name']: item['value'] for item in ret} == self.ATTRS

        for value in ("-1", "0", "100500", "kek"):
            with pytest.raises(rest_session.HTTPError) as ex:
                rest_session.resource[res.id].attribute.create(name="ttl", value=value)
            assert ex.value.status == httplib.BAD_REQUEST
        rest_session.resource[res.id].attribute.create(name="ttl", value="42")

    def test__resource_attribute_update(self, rest_session, rest_session_group, task_manager, resource_manager):
        res = tests._create_resource(task_manager, parameters={"attrs": self.ATTRS, "owner": rest_session_group})

        ret = rest_session.resource[res.id].attribute[:]
        assert {item['name']: item['value'] for item in ret} == self.ATTRS

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[666].attribute.attr1 = {'value': 'value'}
        assert ex.value.status == httplib.NOT_FOUND

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[res.id].attribute.non_existent = {'value': 'value'}
        assert ex.value.status == httplib.NOT_FOUND

        updated = rest_session.resource[res.id].read()["time"]["updated"]

        for name, value in self.ATTRS.iteritems():
            value += '0'
            rest_session.resource[res.id].attribute[name] = {'value': value}
            updated = check_updated(res.id, updated, rest_session)

        ret = rest_session.resource[res.id].attribute[:]
        assert {item['name']: item['value'] for item in ret} == {k: v + '0' for k, v in self.ATTRS.iteritems()}

        rest_session.resource[res.id].attribute.attr1 = {'name': 'attr4'}
        ret = rest_session.resource[res.id].attribute[:]
        attr = next((r for r in ret if r['name'] == 'attr4'), None)
        assert attr['value'] == self.ATTRS['attr1'] + '0'

        rest_session.resource[res.id].attribute.create(name="ttl", value="42")
        for value in ("-1", "0", "100500", "kek"):
            with pytest.raises(rest_session.HTTPError) as ex:
                rest_session.resource[res.id].attribute["ttl"].update(value=value)
            assert ex.value.status == httplib.BAD_REQUEST
        rest_session.resource[res.id].attribute["ttl"].update(value="43")

    def test__resource_attribute_delete(self, rest_session, rest_session_group, task_manager, resource_manager):
        res = tests._create_resource(task_manager, parameters={"attrs": self.ATTRS, "owner": rest_session_group})

        ret = rest_session.resource[res.id].attribute[:]
        assert {item['name']: item['value'] for item in ret} == self.ATTRS

        with pytest.raises(rest_session.HTTPError) as ex:
            del rest_session.resource[666].attribute.attr1
        assert ex.value.status == httplib.NOT_FOUND

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource[res.id].attribute.non_existent.delete()
        assert ex.value.status == httplib.NOT_FOUND

        updated = rest_session.resource[res.id].read()["time"]["updated"]

        for name, value in self.ATTRS.iteritems():
            del rest_session.resource[res.id].attribute[name]
            updated = check_updated(res.id, updated, rest_session)

        ret = rest_session.resource[res.id].attribute[:]
        assert ret == []

    def test__resource_data_urls(self, rest_session, rest_su_session, client_manager, task_manager, resource_manager):
        res = tests._create_resource(task_manager)
        tests._create_client(client_manager, common.config.Registry().this.id)
        hosts = set(res.get_hosts())
        ret = rest_session.resource[res.id].data.http[:]
        assert set(o['host'] for o in ret) == hosts

        ret = rest_session.resource[res.id].data.rsync[:]
        assert set(o['host'] for o in ret) == hosts

        host_delete_from = random.choice(list(hosts))
        with pytest.raises(rest_session.HTTPError) as ex:
            del rest_session.resource[res.id].data[host_delete_from]
        assert ex.value.status == httplib.FORBIDDEN

    def test__versioned_resources_get(self, task_manager, resource_manager, json_api_url):
        task = tests._create_task(task_manager)
        resources = []
        for i in xrange(10):
            resources.append(tests._create_resource(task_manager, task=task))

        client = common.rest.Client(json_api_url, version=100500)
        for res in resources:
            ret = client.resource[res.id].read()
            assert ret['id'] == res.id

    def test__resource_touch_api_method(self, task_manager, resource_manager, rest_session):
        touch_delay = dt.timedelta(seconds=common.config.Registry().common.resources.touch_delay)
        resource = tests._create_resource(task_manager)
        resource_mp = resource.Model.objects.with_id(resource.id)
        resource_mp.time.accessed = dt.datetime.utcnow() - touch_delay - dt.timedelta(minutes=1)
        resource_mp.save()
        rest_session.resource[resource.id].touch.create()
        resource_mp = resource.Model.objects.with_id(resource.id)
        assert dt.datetime.utcnow() - resource_mp.time.accessed < dt.timedelta(minutes=2)

    def test__resource_meta(self, rest_session):
        for encoded_rc in (
            rest_session.resource.meta["TEST_TASK_RESOURCE"].read(),
            rest_session.resource.meta_list["TEST_TASK_RESOURCE"].read()[0]
        ):
            encoded_rc = rest_session.resource.meta["TEST_TASK_RESOURCE"].read()
            assert encoded_rc["on_restart"] == "DELETE"
            assert encoded_rc["name"] == "TEST_TASK_RESOURCE"
            assert encoded_rc["parent"] == "RESOURCE"

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource.meta["TEST_KEK_RESOURCE"].read()

        assert ex.value.status == httplib.NOT_FOUND

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session.resource.meta_list["TEST_KEK_RESOURCE"].read()

        assert ex.value.status == httplib.NOT_FOUND

    def test__resource_link_get(
        self, task_manager, resource_manager, rest_session, rest_session_login, rest_session2, rest_session_login2
    ):
        resource = tests._create_resource(task_manager)
        resource2 = tests._create_resource(task_manager)
        link1 = rest_session.resource.link.create(resource_id=resource.id)
        link2 = rest_session2.resource.link.create(resource_id=resource.id)
        link3 = rest_session2.resource.link.create(resource_id=resource2.id)
        assert link1["id"] != link2["id"]
        assert link2["id"] != link3["id"]

        links = rest_session.resource.link.read(resource_id=resource.id, limit=3000)
        assert len(links["items"]) == 1
        get_link1 = links["items"][0]
        assert get_link1["id"] == link1["id"]

        with pytest.raises(rest_session.HTTPError) as ex:
            rest_session2.resource.link.read(limit=3000)
        assert ex.value.status == httplib.BAD_REQUEST

        links = rest_session2.resource.link.read(resource_id=resource.id, limit=3000)
        assert len(links["items"]) == 1
        get_link2 = links["items"][0]
        assert get_link2["id"] == link2["id"]

    def test__resource_link_create(self, task_manager, resource_manager, rest_session, rest_session_login):
        resource = tests._create_resource(task_manager)
        link = rest_session.resource.link.create(resource_id=resource.id)
        assert link["author"] == rest_session_login
        assert link["resource_id"] == resource.id

        link2 = rest_session.resource.link.create(resource_id=resource.id)
        assert link["id"] == link2["id"]

        links = rest_session.resource.link.read(resource_id=resource.id, limit=3000)
        assert len(links["items"]) == 1
        link3 = links["items"][0]
        assert link3["author"] == rest_session_login
        assert link3["resource_id"] == resource.id
        assert link3["id"] == link["id"]

    def test__resource_link_update(self, task_manager, resource_manager, rest_session, rest_session_login):
        resource = tests._create_resource(task_manager)
        link = rest_session.resource.link.create(resource_id=resource.id)
        link_mp = mapping.ResourceLink.objects.with_id(link["id"])
        accessed = link_mp.accessed - dt.timedelta(seconds=common.config.Registry().common.resources.touch_delay)

        link_mp.accessed = accessed
        link_mp.save()
        link = rest_session.resource.link.create(resource_id=resource.id)
        link_mp = mapping.ResourceLink.objects.with_id(link["id"])
        assert link_mp.accessed != accessed

        link_mp.accessed = accessed
        link_mp.save()
        link = rest_session.resource.link.update(id=link_mp.id)
        assert link["author"] == rest_session_login
        assert link["resource_id"] == resource.id
        assert link["id"] == link_mp.id
        link_mp = mapping.ResourceLink.objects.with_id(link["id"])
        assert link_mp.accessed != accessed

    def test__resource_lock_for_mds(self, rest_su_session, serviceq):
        res_id = 2
        host1 = "test_host1"
        host2 = "test_host2"
        assert rest_su_session.resource[res_id].mds_lock.create(host=host1, acquire=True)["result"]
        assert not rest_su_session.resource[res_id].mds_lock.create(host=host2, acquire=True)["result"]
        assert rest_su_session.resource[res_id].mds_lock.create(host=host1, acquire=False)["result"]
        assert rest_su_session.resource[res_id].mds_lock.create(host=host2, acquire=True)["result"]
