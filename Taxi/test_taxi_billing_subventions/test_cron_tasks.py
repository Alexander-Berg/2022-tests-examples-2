# pylint: disable=invalid-name,redefined-builtin,too-many-lines
import copy
import datetime as dt
import typing as tp

import pytest

from taxi.billing.util import dates as billing_dates
from taxi.maintenance import run

from taxi_billing_subventions.cron import app
from taxi_billing_subventions.cron.tasks import take_parks_b2b_fixed_commission


class DocsClient:
    def __init__(self) -> None:
        self._next_doc_id = 0
        self.created_docs: tp.List[dict] = []
        self._required_fields = {
            'kind',
            'external_obj_id',
            'external_event_ref',
            'service',
            'data',
            'event_at',
            'journal_entries',
        }

    async def create(self, data: dict, log_extra=None) -> dict:
        actual_keys = set(data.keys())
        if self._required_fields - actual_keys:
            raise Exception(
                'Validation error: {keys}'.format(
                    keys=', '.join(self._required_fields - actual_keys),
                ),
            )
        self.created_docs.append(data)
        result = copy.deepcopy(data)
        result['doc_id'] = self._next_doc_id
        if 'process_at' not in data:
            result['process_at'] = billing_dates.format_time(
                dt.datetime.utcnow(),
            )
        self._next_doc_id += 1
        return result


class SubventionsClient:
    async def process_doc(
            self,
            doc_id: int,
            doc_kind: tp.Optional[str] = None,
            process_at: tp.Optional[dt.datetime] = None,
            log_extra=None,
    ) -> dict:
        return {}


def create_app(loop, simple_secdist):
    data = app.App(loop)
    data.secdist = simple_secdist
    data.docs_client = DocsClient()
    data.subventions_client = SubventionsClient()
    return data


@pytest.mark.now('2020-06-30T19:31:35')
@pytest.mark.parametrize('expected_docs_json', ['expected_docs.json'])
async def test_cron_run(expected_docs_json, loop, simple_secdist, load_json):
    expected_docs = load_json(expected_docs_json)
    context_app = create_app(loop, simple_secdist)
    context = run.StuffContext(
        lock=None,
        task_id='123',
        start_time=dt.datetime.now(),
        data=context_app,
    )
    await take_parks_b2b_fixed_commission.do_stuff(
        context=context, loop=loop, log_extra={},
    )
    assert context_app.docs_client.created_docs == expected_docs
