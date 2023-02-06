import asyncio
import metrika.admin.brb.server.lib.app.app as main_app
import aiohttp.pytest_plugin
from aiohttp.pytest_plugin import aiohttp_client  # noqa
import asynctest as at
import pytest
import metrika.admin.brb.server.lib.utils.bb_client
import metrika.admin.brb.server.lib.utils.awacs_client
import metrika.admin.brb.server.lib.database as database
import metrika.admin.brb.server.lib.models as models
import mock
import logging


logging.basicConfig(level=logging.DEBUG)


pytest_plugins = ['aiohttp.pytest_plugin']
del aiohttp.pytest_plugin.loop

pytestmark = pytest.mark.asyncio


@pytest.yield_fixture(scope='module')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def loop(event_loop):
    return event_loop


@pytest.fixture(scope="module")
async def mocked_app(config, list_namespaces, list_balancers, dummy_its, dummy_juggler):
    with at.patch('metrika.admin.brb.server.lib.utils.its_client.ITSClient') as mocked_its:
        with at.patch('metrika.admin.brb.server.lib.utils.bb_client.BBClient') as mocked_bb:
            with at.patch('metrika.admin.brb.server.lib.utils.awacs_client.AwacsClient') as mocked_awacs:
                with at.patch('metrika.admin.brb.server.lib.utils.juggler_client.JugglerClient') as mocked_juggler:
                    mocked_awacs.return_value.list_namespaces = list_namespaces
                    mocked_awacs.return_value.list_balancers = list_balancers
                    mocked_bb.return_value.get_user = at.CoroutineMock(return_value='presto')
                    mocked_its.return_value = dummy_its
                    mocked_juggler.return_value = dummy_juggler
                    app = main_app.app
                    main_app.init_app(app, config)
                    yield app


class TestBrbApi:
    async def test_index_page(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        resp = await client.get('/')
        text = await resp.text()

        assert resp.status == 200
        assert '<!doctype html>' in text

    async def test_closing_dc(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        db = mocked_app['db']
        async with mocked_app['lock']:
            dc = await models.datacenter.DatacenterModel(db).get_by_id(1)
        data = {"id": str(dc['id']), "status": "closing", "downtime": dc['downtime'], "updated": "", "name": dc['name']}
        resp = await client.put(f"/front/datacenters/{dc['id']}", json=data)
        async with mocked_app['lock']:
            async with db.transaction():
                dc_after = await models.datacenter.DatacenterModel(db).get_by(dc_name=dc["name"])

        assert resp.status == 200
        assert dc_after[0]['status'] in ['closing', 'closed']

    async def test_closing_action_appear(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        db = mocked_app['db']
        async with mocked_app['lock']:
            dc = await models.datacenter.DatacenterModel(db).get_by_id(1)
            action = await models.action.ActionsModel(db).last()

        assert action["username"] == "presto"
        assert action["dc_name"] == dc["name"]
        assert action["action"] == "closing"

    async def test_downtiming_dc(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        db = mocked_app['db']
        async with mocked_app['lock']:
            dc = await models.datacenter.DatacenterModel(db).get_by_id(1)
        data = {"id": str(dc['id']), "status": dc['status'], "downtime": "downtiming", "updated": "", "name": dc['name']}
        resp = await client.put(f"/front/datacenters/{dc['id']}", json=data)
        async with mocked_app['lock']:
            async with db.transaction():
                dc_after = await models.datacenter.DatacenterModel(db).get_by(dc_name=dc["name"])

        assert resp.status == 200
        assert dc_after[0]['downtime'] in ['downtiming', 'downtimed']

    async def test_downtime_action_appear(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        db = mocked_app['db']
        async with mocked_app['lock']:
            dc = await models.datacenter.DatacenterModel(db).get_by_id(1)
            action = await models.action.ActionsModel(db).last()

        assert action["username"] == "presto"
        assert action["dc_name"] == dc["name"]
        assert action["action"] == "downtiming"

    async def test_open_and_undowntime(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        db = mocked_app['db']
        async with mocked_app['lock']:
            async with db.transaction():
                await models.datacenter.DatacenterModel(db).set_by_id(1, status='closed', downtime='downtimed')
                dc = await models.datacenter.DatacenterModel(db).get_by_id(1)
        data = {"id": str(dc['id']), "status": "opening", "downtime": "undowntiming", "updated": "", "name": dc['name']}
        resp = await client.put(f"/front/datacenters/{dc['id']}", json=data)
        async with mocked_app['lock']:
            async with db.transaction():
                dc_after = await models.datacenter.DatacenterModel(db).get_by(dc_name=dc["name"])

        assert resp.status == 200
        assert dc_after[0]['downtime'] in ['undowntiming', 'undowntimed']
        assert dc_after[0]['status'] in ['opening', 'open']

    async def test_open_and_undowntime_action_appear(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        db = mocked_app['db']
        async with mocked_app['lock']:
            dc = await models.datacenter.DatacenterModel(db).get_by_id(1)
            action = await models.action.ActionsModel(db).last()

        assert action["username"] == "presto"
        assert action["dc_name"] == dc["name"]
        assert action["action"] == "opening + undowntiming"

    async def test_close_two_dc(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        db = mocked_app['db']
        async with mocked_app['lock']:
            async with db.transaction():
                await models.datacenter.DatacenterModel(db).set_by_id(1, status='closed', downtime='downtimed')
                await models.datacenter.DatacenterModel(db).set_by_id(2, status='open', downtime='undowntimed')
                dc = await models.datacenter.DatacenterModel(db).get_by_id(2)
        data = {"id": str(dc['id']), "status": "closing", "downtime": "undowntimed", "updated": "", "name": dc['name']}
        resp = await client.put(f"/front/datacenters/{dc['id']}", json=data)
        async with mocked_app['lock']:
            async with db.transaction():
                dc_after = await models.datacenter.DatacenterModel(db).get_by(dc_name=dc["name"])

        assert resp.status == 400
        assert dc_after[0]['status'] == 'open'

    async def test_awacs_closed_and_downtimed(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        db = mocked_app['db']
        async with mocked_app['lock']:
            async with db.transaction():
                await models.datacenter.DatacenterModel(db).set_by_id(1, status='open', downtime='undowntimed')
                dc = await models.datacenter.DatacenterModel(db).get_by_id(3)
        data = {"id": str(dc['id']), "status": "closing", "downtime": "downtiming", "updated": "", "name": dc['name']}
        resp = await client.put(f"/front/datacenters/{dc['id']}", json=data)
        await asyncio.sleep(7)
        async with mocked_app['lock']:
            async with db.transaction():
                dc_after = await models.datacenter.DatacenterModel(db).get_by(dc_name=dc["name"])
                closed_balancers = await models.awacs.AwacsModel(db).get_awacs(status="closed", dc_name=dc['name'])
                downtimes = await models.downtime.DowntimeModel(db).get_by_dc(dc_name=dc['name'])

        assert resp.status == 200
        assert dc_after[0]['status'] == 'closed'
        assert dc_after[0]['downtime'] == 'downtimed'
        assert len(closed_balancers) == 9
        assert len(downtimes) == 2

    async def test_awacs_opened_and_undowntimed(self, mocked_app, aiohttp_client):
        client = await aiohttp_client(mocked_app)
        db = mocked_app['db']
        async with mocked_app['lock']:
            async with db.transaction():
                dc = await models.datacenter.DatacenterModel(db).get_by_id(3)
        data = {"id": str(dc['id']), "status": "opening", "downtime": "undowntiming", "updated": "", "name": dc['name']}
        resp = await client.put(f"/front/datacenters/{dc['id']}", json=data)
        await asyncio.sleep(7)
        async with mocked_app['lock']:
            async with db.transaction():
                dc_after = await models.datacenter.DatacenterModel(db).get_by(dc_name=dc["name"])
                opened_balancers = await models.awacs.AwacsModel(db).get_awacs(status="open", dc_name=dc['name'])
                downtimes = await models.downtime.DowntimeModel(db).get_by_dc(dc_name=dc['name'])

        assert resp.status == 200
        assert dc_after[0]['status'] == 'open'
        assert dc_after[0]['downtime'] == 'undowntimed'
        assert len(opened_balancers) == 9
        assert len(downtimes) == 0
