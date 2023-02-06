from __future__ import annotations

import contextlib
import datetime

import pytest

from billing_functions.stq import pipeline
from billing_functions.stq import single_doc
from test_billing_functions.stq import stq as stq_helper

TEST_DOC_ID = 18061991


class ExpectedException(Exception):
    pass


async def test_stq_fails_if_no_doc(
        *, do_mock_billing_reports, do_mock_billing_docs, stq3_context,
):
    do_mock_billing_reports()
    do_mock_billing_docs()
    with pytest.raises(ValueError):
        await single_doc.task(
            stq3_context, stq_helper.task_info(), TEST_DOC_ID,
        )


@pytest.mark.now('2021-10-21T00:00:00+00:00')
@pytest.mark.parametrize('expected_updates_json', ['expected_updates.json'])
async def test_stq_task_happy_path(
        expected_updates_json,
        *,
        patch,
        load_json,
        dummy_pipeline,
        do_mock_billing_reports,
        do_mock_billing_docs,
        stq3_context,
        monkeypatch,
):
    @patch('random.randrange')
    def _randrange(start, stop):
        return 12345

    class DummyStq:
        @staticmethod
        async def reschedule(*args, **kwargs):
            pass

    do_mock_billing_reports([load_json('doc.json')])
    billing_docs = do_mock_billing_docs()
    monkeypatch.setattr(stq3_context.stq, 'dummy', DummyStq, raising=False)
    for _ in range(3):  # postpone, fail
        with contextlib.suppress(ExpectedException):
            await single_doc.task(
                stq3_context, stq_helper.task_info('dummy'), TEST_DOC_ID,
            )
    expected_update_request = load_json(expected_updates_json)
    assert billing_docs.update_requests == expected_update_request
    expected_restored_docs = load_json('expected_restored_docs.json')
    assert billing_docs.restored_docs == expected_restored_docs


async def test_stq_task_fails_if_no_handler(
        *,
        load_json,
        do_mock_billing_reports,
        do_mock_billing_docs,
        stq3_context,
):
    doc = load_json('doc.json')
    do_mock_billing_reports()
    do_mock_billing_docs([doc])
    with pytest.raises(ValueError):
        await single_doc.task(
            stq3_context, stq_helper.task_info(), TEST_DOC_ID,
        )


@pytest.mark.config(
    BILLING_STQ_SLEEP_ON_EXEC={
        '__default__': {'min_interval': 0, 'max_interval': 0},
        'some_queue': {'min_interval': 0.1, 'max_interval': 0.2},
    },
)
@pytest.mark.dontfreeze
async def test_stq_task_wait_before_task_exec(
        *, do_mock_billing_reports, do_mock_billing_docs, stq3_context,
):
    do_mock_billing_reports()
    do_mock_billing_docs()
    was = datetime.datetime.now()
    with pytest.raises(ValueError):
        await single_doc.task(
            stq3_context,
            stq_helper.task_info(queue='some_queue', exec_tries=2),
            TEST_DOC_ID,
        )
    now = datetime.datetime.now()
    assert now - was > datetime.timedelta(seconds=0.1)


@pytest.fixture(name='dummy_pipeline')
def make_dummy_handler(stq3_context, monkeypatch):
    def do_handler(
            next_status: str, doc_update: pipeline.Serializable,
    ) -> pipeline.StageHandler:
        async def _handle(context, doc):
            return pipeline.Results.completed(next_status, doc_update)

        return _handle

    def do_simple_handler(
            doc_update: pipeline.Serializable,
    ) -> pipeline.StageHandler:
        async def _handle(context, doc):
            return doc_update

        return _handle

    def fail_once(handler: pipeline.StageHandler) -> pipeline.StageHandler:
        failed_once = False

        async def _handle(context, doc):
            nonlocal failed_once
            if not failed_once:
                failed_once = True
                raise ExpectedException('BOOM')
            return await handler(context, doc)

        return _handle

    def postpone_once(handler: pipeline.StageHandler) -> pipeline.StageHandler:
        awaited_once = False

        async def _handle(context, doc):
            nonlocal awaited_once
            if not awaited_once:
                awaited_once = True
                return pipeline.Results.postponed()
            return await handler(context, doc)

        return _handle

    class Serializable:
        @staticmethod
        def serialize() -> dict:
            return {'some_field': 'some_value'}

    pipeline.configure(
        kinds=['1', '2', '3'],
        deserialize=lambda doc: doc,
        terminal_statuses=['processed'],
        stages=[
            pipeline.Stage(
                status='stage0',
                next_status='stage1',
                field_to_update='some_int_value',
                handler=do_simple_handler(doc_update=1),
            ),
            pipeline.Stage(
                status='stage1',
                next_status='stage2',
                field_to_update='some_string_value',
                handler=do_simple_handler(doc_update='some_string_value'),
            ),
            pipeline.Stage(
                status='stage2',
                expected_statuses=['stage3'],
                field_to_update='some_bool_value',
                handler=postpone_once(do_handler('stage3', doc_update=True)),
            ),
            pipeline.Stage(
                status='stage3',
                next_status='stage4',
                field_to_update='codegen_model',
                force_doc_update=True,
                handler=do_simple_handler(doc_update=Serializable()),
            ),
            pipeline.Stage(
                status='stage4',
                expected_statuses=['processed'],
                field_to_update='list_of_codegen_models',
                handler=fail_once(
                    do_handler('processed', doc_update=[Serializable]),
                ),
            ),
        ],
    )

    yield

    # pylint: disable=protected-access
    for kind in '1', '2', '3':
        pipeline._PIPELINES.pop(kind)
