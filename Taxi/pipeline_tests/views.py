import copy
import typing

from aiohttp import web

from js_pipeline.generated import models

from admin_pipeline import common
from admin_pipeline import common_helpers
from admin_pipeline.generated.service.swagger.models import api


def drop_id(doc: dict) -> dict:
    data = copy.copy(doc)
    if '_id' in doc:
        del data['_id']
    if 'id' in doc:
        del data['id']
    return data


class NotFoundError(Exception):
    ERR_CODE = 'not_found'


class _CommonView(common_helpers.DBHelper):
    DATA_TYPE: typing.Optional[typing.Type] = None

    @staticmethod
    def __for_db(data):
        return common.for_db(data, id_type=str)

    @classmethod
    async def create(cls, request, context):
        data = request.body
        existing = await cls.try_find_one(
            context.mongo.secondary,
            {'_id': data.id},
            request.consumer,
            for_model=cls.DATA_TYPE,
        )
        if existing is not None:
            raise web.HTTPBadRequest(
                reason=f'Item with id ({data.id}) already exists',
            )
        serialized = cls.__for_db(cls.DATA_TYPE.serialize(data))
        serialized['consumer'] = request.consumer
        await cls.insert_one(context.mongo, serialized)

    @classmethod
    async def get(cls, id_, consumer, context):
        found = await cls.try_find_one(
            context.mongo.secondary,
            {'_id': id_},
            consumer,
            for_model=cls.DATA_TYPE,
        )
        if not found:
            raise NotFoundError('Item not found: %s for %s' % (id_, consumer))
        return cls.DATA_TYPE.deserialize(common.for_json(found))

    @classmethod
    async def update_item(cls, request, context):
        item = request.body
        if item.id != request.id:
            raise web.HTTPBadRequest(
                reason='Item id changed! Old %s, new - %s '
                % (request.id, item.id),
            )
        doc = cls.__for_db(cls.DATA_TYPE.serialize(item))
        doc['consumer'] = request.consumer
        result = await cls.update(
            context.mongo,
            {'$and': [{'_id': request.id}, {'consumer': request.consumer}]},
            doc,
        )
        if result['n'] != 1:
            raise NotFoundError(
                'Item not found: %s for %s' % (request.id, request.consumer),
            )

    @classmethod
    async def delete(cls, request, context):
        await cls.remove(
            context.mongo,
            {'$and': [{'_id': request.id}, {'consumer': request.consumer}]},
        )


class ChecksView(_CommonView):
    DATA_TYPE = api.Check
    PROJECTIONS = {DATA_TYPE: ['name', 'check']}

    @classmethod
    def determine_check_type(cls, check):
        if 'source_code' in check:
            return 'imperative'
        if 'expected_output' in check:
            return 'combined'
        raise Exception('Unexpected check type: ' + str(check))

    @classmethod
    def get_collection(cls, db):
        return db.admin_pipeline_test_checks

    @classmethod
    async def enumerate_checks(cls, consumer, context):
        all_checks = cls.find_many(
            context.mongo, {}, consumer, for_model=api.Check,
        )
        result = api.TestChecksEnumerateResponse(
            output_checks=[
                api.EnumeratedCheck(
                    check['_id'],
                    check['name'],
                    cls.determine_check_type(check['check']),
                )
                async for check in all_checks
            ],
        )
        return result


class MocksView(_CommonView):
    DATA_TYPE = api.Mock
    PROJECTIONS = {DATA_TYPE: ['name', 'resource', 'is_prefetched', 'mock']}

    @classmethod
    def get_collection(cls, db):
        return db.admin_pipeline_test_mocks

    @classmethod
    async def enumerate_mocks(cls, consumer, context):
        all_mocks = cls.find_many(
            context.mongo, {}, consumer, for_model=api.Mock,
        )
        input_mocks = []
        prefetched_resources_mocks = []
        resources_mocks = []
        async for mock in all_mocks:
            resource = mock.get('resource')
            name = mock['name']
            _id = mock['_id']
            is_prefetched = mock['is_prefetched']
            if not resource:
                input_mocks.append(api.EnumeratedMocksItem(_id, name))
            elif is_prefetched:
                prefetched_resources_mocks.append(
                    api.EnumeratedMocksItem(_id, name, resource),
                )
            else:
                resources_mocks.append(
                    api.EnumeratedMocksItem(_id, name, resource),
                )

        result = api.TestMocksEnumerateResponse(
            input_mocks=input_mocks,
            resources_mocks=resources_mocks,
            prefetched_resources_mocks=prefetched_resources_mocks,
        )
        return result


class TestsView(_CommonView):
    DATA_TYPE = models.PipelineTest
    PROJECTIONS = {
        DATA_TYPE: [
            'name',
            'scope',
            'testcases',
            'prefetched_resources_mocks',
            'resources_mocks',
            'input_mocks',
            'output_checks',
        ],
    }

    @classmethod
    def get_collection(cls, db):
        return db.admin_pipeline_tests

    @classmethod
    async def enumerate_tests(cls, request, context):
        all_tests = cls.find_many(
            context.mongo, {}, request.consumer, for_model=models.PipelineTest,
        )
        result = api.TestsEnumerateResponse(
            tests=[
                api.EnumeratedTest(test['_id'], test['name'], test['scope'])
                async for test in all_tests
            ],
        )
        return result


class ChoosenTestsHelper(common_helpers.DBHelper):
    PROJECTIONS: dict = dict()

    @classmethod
    def get_collection(cls, db):
        return db.admin_pipeline_choosen_tests


class TestsResultsHelper(common_helpers.DBHelper):
    PROJECTIONS: dict = {models.PipelineTestsResults: ['tests', 'created']}

    @classmethod
    def get_collection(cls, db):
        return db.admin_pipeline_tests_results
