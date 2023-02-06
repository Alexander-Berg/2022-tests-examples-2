import asyncio
import json
import logging
import math
import typing as tp
import uuid

from generated.clients import supportai as supportai_client
import generated.clients_libs.supportai.supportai_lib as supportai_lib
import generated.clients_libs.supportai_context.supportai_lib as supportai_context_lib  # noqa:  E501

from supportai_tasks import models as db_models
from supportai_tasks.stq.tasks import base_task
from supportai_tasks.utils import dialogs_helper
from supportai_tasks.utils import testing_aggregation


logger = logging.getLogger(__name__)


DIFF_SKIP_KEYS = ['probabilities', 'explanation']
DIFF_SKIP_FEATURES = ['chat_id', 'last_policy_slug']
TESTING_SUFFIX = '-testrun'


def _is_equal(first, second) -> bool:
    if isinstance(first, float) and isinstance(second, float):
        return math.isclose(first, second)
    if type(first) == type(second):  # pylint: disable=unidiomatic-typecheck
        return first == second
    return False


async def _diff(first, second):
    if isinstance(first, dict) and isinstance(second, dict):
        diff = {}
        for key in first.keys():
            if key in DIFF_SKIP_KEYS:
                continue

            if key in second:
                local_diff = await _diff(first[key], second[key])
                if local_diff:
                    diff[key] = local_diff
            else:
                diff[key] = first[key]
    elif isinstance(first, list) and isinstance(second, list):
        diff = []
        # O(n^2) ~ const | n ~ const
        for item_first in first:

            if (
                    isinstance(item_first, dict)
                    and item_first.get('key') in DIFF_SKIP_FEATURES
            ):
                continue

            contains = False
            for item_second in second:
                items_diff = await _diff(item_first, item_second)
                if not items_diff:
                    contains = True
            if not contains:
                diff.append(item_first)
    else:
        if _is_equal(first, second):
            return
        diff = first

    return diff


@base_task.TasksFactory.register('test_configuration')
class TestConfigurationTask(base_task.BaseTask):
    def __init__(self, context, task, log_extra: tp.Optional[dict] = None):
        super().__init__(context, task, log_extra)
        self.aggregation = testing_aggregation.Aggregation(
            context, log_extra, task.id,
        )

    async def _responses_diff(self, release_response, draft_response):
        release_dict = supportai_lib.SupportResponse.serialize(
            release_response,
        )
        draft_dict = supportai_lib.SupportResponse.serialize(draft_response)

        release_dict.pop('version', None)
        draft_dict.pop('version', None)

        release_diff = await _diff(release_dict, draft_dict)
        draft_diff = await _diff(draft_dict, release_dict)

        return {
            'release_diff': json.dumps(release_diff),
            'draft_diff': json.dumps(draft_diff),
            'is_equal': not (release_diff or draft_diff),
        }

    async def _request_to_response(self, request, version=None):
        response = await self.context.clients.supportai.support_v1(
            body=request,
            project_id=self.project.slug,
            simulated=True,
            mocked=True,
            version=version,
        )
        return response

    def _get_config_settings(self, config):
        settings = config['default_settings']
        for project in config['projects']:
            if project['project_id'] == self.project.slug:
                settings = project['settings']
        return (
            settings['delay_between_batches_in_seconds'],
            settings['delay_between_requests_in_milliseconds'],
            settings['batch_size'],
        )

    async def _run_internal(
            self, task_args: tp.Optional[dict],
    ) -> base_task.TaskProcessingState:

        config = self.context.config.SUPPORTAI_TASKS_CONFIGURATION_TESTING
        (
            delay_between_batches,
            delay_between_requests,
            batch_size,
        ) = self._get_config_settings(config)

        task_args = task_args or {}
        if task_args.get('sample_slug') is None:
            self.task.error_message = 'sample_slug is required task parameter'
            return base_task.TaskProcessingState.Error

        await self.aggregation.init_from_db()

        logger.info(
            f'Start run testing batch on {task_args["sample_slug"]} sample. '
            f'Offset: {task_args.get("offset", 0)}',
        )
        records_count = await self._run_batch(
            task_args['sample_slug'],
            task_args.get('use_history', False),
            task_args.get('offset', 0),
            batch_size,
            delay_between_requests,
        )
        logger.info(f'Batch processed {records_count} records.')

        if records_count == 0:
            return base_task.TaskProcessingState.Finished

        await self.aggregation.save_testing_aggregation()

        self._reschedule_task(delay_between_batches)
        return base_task.TaskProcessingState.Working

    async def _run_batch(
            self,
            sample_slug,
            use_history,
            offset,
            batch_size,
            delay_between_requests,
    ):
        dialogs_response = await dialogs_helper.get_dialogs_from_context(
            context=self.context,  # type: ignore
            project_slug=self.project.slug,
            sampling_slug=sample_slug,
            offset=offset,
            limit=batch_size,
        )

        diff_list: tp.List[tp.Tuple[tp.Any, tp.Any]] = []
        processed_dialogs_count = 0
        old_chat_id = None

        for dialog in dialogs_response.dialogs:
            processed_dialogs_count += 1
            new_chat_id = uuid.uuid4().hex + TESTING_SUFFIX
            for record in dialog.records:

                request_dict = supportai_context_lib.SupportRequest.serialize(
                    record.request,
                )
                request = supportai_lib.SupportRequest.deserialize(
                    request_dict,
                )
                old_chat_id = request.chat_id
                request.chat_id = new_chat_id

                try:
                    release_response = await self._request_to_response(request)
                except supportai_client.ClientException as exc:
                    logger.warning(
                        f'Supportai error during offline testing: {exc}',
                    )
                    continue
                response_v1 = release_response.body

                response_dict = (
                    supportai_context_lib.SupportResponse.serialize(
                        record.response,
                    )
                )
                history_response_body = (
                    supportai_lib.SupportResponse.deserialize(response_dict)
                )
                response_v2 = history_response_body

                if not use_history:
                    try:
                        draft_response = await self._request_to_response(
                            request, 'draft',
                        )
                    except supportai_client.ClientException as exc:
                        logger.warning(
                            f'Supportai error during offline testing: {exc}',
                        )
                        continue
                    response_v2 = draft_response.body

                responses_diff = await self._responses_diff(
                    response_v1, response_v2,
                )
                diff_list.append((record.request, responses_diff))

                self.aggregation.add_aggregation(
                    response_v1,
                    response_v2,
                    history_response_body,
                    dialog.chat_mark,
                    responses_diff['is_equal'],
                )

                # early stopping
                if not responses_diff['is_equal']:
                    logger.info(
                        f'Stop process dialog with chat_id {old_chat_id}: '
                        f'responses are not equal',
                    )
                    break

                await asyncio.sleep(delay_between_requests / 1000)

        records_count = len(diff_list)

        params = self.task.params.extra
        params['processed_dialogs_count'] = (
            params.get('processed_dialogs_count', 0) + processed_dialogs_count
        )
        params['offset'] = offset + batch_size

        self.task.progress = (
            100 * params['processed_dialogs_count'] // dialogs_response.total
            if dialogs_response.total
            else 0
        )

        async with self.context.pg.master_pool.acquire(
                log_extra=self.log_extra,
        ) as conn:
            for request, result in diff_list:
                request_messages = request.dialog.messages
                request_text = (
                    request_messages[-1].text if request_messages else ''
                )
                await db_models.ConfigurationTest.insert(
                    context=self.context,
                    db_conn=conn,
                    task_id=self.task.id,
                    request_text=request_text,
                    is_equal=result['is_equal'],
                    diff=json.dumps(
                        {
                            'release': result['release_diff'],
                            'draft': result['draft_diff'],
                        },
                    )
                    if not result['is_equal']
                    else None,
                    chat_id=old_chat_id if old_chat_id else None,
                )
                logger.info(f'Results saved to DB.')

        return records_count
