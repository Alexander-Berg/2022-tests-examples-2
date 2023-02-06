import collections
import datetime

from js_pipeline.generated import models

from admin_pipeline.generated.service.swagger.models import api
from admin_pipeline.pipeline import common as pipeline_common
from admin_pipeline.pipeline_tests import views as testing_views


class TestingHelper:
    @staticmethod
    async def test_pipeline(request_body, context):
        assert False, 'test_pipeline is not defined in helper'

    def serialize(self, pipeline: models.Pipeline, add_consumer=False) -> dict:
        assert False, 'test_pipeline is not defined in helper'

    @staticmethod
    def __serialize_tests(tests_results):
        # Keys, starting with '$' is forbidden in mongodb
        def __replace_dollar_rec(obj):
            if isinstance(obj, dict):
                return {
                    key.replace('$', '_$'): __replace_dollar_rec(value)
                    for key, value in obj.items()
                }
            if isinstance(obj, list):
                return [__replace_dollar_rec(value) for value in obj]
            return obj

        return __replace_dollar_rec(
            tests_results.body.tests_results.serialize()['tests'],
        )

    async def enumerate_pipeline_tests(self, consumer, pipeline_name, context):
        tests = [
            api.EnumeratedTest(test['_id'], test['name'], test['scope'])
            async for test in testing_views.TestsView.find_many(
                context.mongo.secondary, {'scope': 'global'}, consumer,
            )
        ]
        togglers = await testing_views.ChoosenTestsHelper.try_find_one(
            context.mongo.secondary,
            {'pipeline_name': pipeline_name},
            consumer,
        )
        if togglers:
            tests.extend(
                [
                    api.EnumeratedTest(
                        test['_id'], test['name'], test['scope'],
                    )
                    async for test in testing_views.TestsView.find_many(
                        context.mongo.secondary,
                        {'name': {'$in': togglers['tests']}},
                        consumer,
                    )
                ],
            )
        return api.TestsEnumerateResponse(tests=tests)

    async def enable_pipeline_tests(self, request, context):
        await testing_views.ChoosenTestsHelper.update_one(
            context.mongo,
            {
                '$and': [
                    {'pipeline_name': request.pipeline_name},
                    {'consumer': request.consumer},
                ],
            },
            {'$set': {'tests': request.body.enabled_tests}},
            upsert=True,
        )

    async def get_pipeline_tests_results(self, pipeline_id, consumer, context):
        # intentionally query master
        result = await testing_views.TestsResultsHelper.try_find_one(
            context.mongo,
            {'pipeline_id': pipeline_id},
            consumer,
            for_model=models.PipelineTestsResults,
        )
        if not result:
            return None
        return models.PipelineTestsResults.deserialize(
            testing_views.drop_id(result),
        )

    async def perform_tests(self, pipeline, consumer, context):
        enumerated_tests = await self.enumerate_pipeline_tests(
            consumer, pipeline.name, context,
        )
        tests = [
            await testing_views.TestsView.get(
                enumerated_test.id, consumer, context,
            )
            for enumerated_test in enumerated_tests.tests
        ]
        if not tests:
            return models.PipelineTestsResults(
                created=datetime.datetime.now(), tests=[],
            )

        enumerated_mocks = await testing_views.MocksView.enumerate_mocks(
            consumer, context,
        )
        resources_mocks = collections.defaultdict(dict)
        prefetched_resources_mocks = collections.defaultdict(dict)
        input_mocks = dict()
        for enumerated_mock in enumerated_mocks.resources_mocks:
            mock = await testing_views.MocksView.get(
                enumerated_mock.id, consumer, context,
            )
            resources_mocks[mock.resource][mock.name] = mock.mock
        for enumerated_mock in enumerated_mocks.prefetched_resources_mocks:
            mock = await testing_views.MocksView.get(
                enumerated_mock.id, consumer, context,
            )
            prefetched_resources_mocks[mock.resource][mock.name] = mock.mock
        for enumerated_mock in enumerated_mocks.input_mocks:
            mock = await testing_views.MocksView.get(
                enumerated_mock.id, consumer, context,
            )
            input_mocks[mock.name] = mock.mock

        enumerated_checks = await testing_views.ChecksView.enumerate_checks(
            consumer, context,
        )
        checks = dict()
        for enumerated_check in enumerated_checks.output_checks:
            check = await testing_views.ChecksView.get(
                enumerated_check.id, consumer, context,
            )
            checks[check.name] = check.check.serialize()

        test_request_body = {
            'pipeline': self.serialize(pipeline, add_consumer=True),
            'tests': [test.serialize() for test in tests],
            'resources_mocks': resources_mocks,
            'prefetched_resources_mocks': prefetched_resources_mocks,
            'input_mocks': input_mocks,
            'output_checks': checks,
        }
        tests_results = await self.test_pipeline(test_request_body, context)
        tzinfo = (
            datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        )
        now = datetime.datetime.now().astimezone(tzinfo).isoformat()
        await testing_views.TestsResultsHelper.update_one(
            context.mongo,
            {'$and': [{'pipeline_id': pipeline.id}, {'consumer': consumer}]},
            {
                '$set': {
                    'pipeline_id': pipeline.id,
                    'consumer': consumer,
                    'created': now,
                    'tests': self.__serialize_tests(tests_results),
                },
            },
            upsert=True,
        )
        return await self.get_pipeline_tests_results(
            pipeline.id, consumer, context,
        )

    async def test_pipeline_request(self, request, context):
        pipeline = await pipeline_common.get_by_id(
            request.body.pipeline_id, self, context,
        )
        return await self.perform_tests(pipeline, request.consumer, context)
