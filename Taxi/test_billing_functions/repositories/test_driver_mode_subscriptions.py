import asyncio
import datetime as dt
from unittest import mock

import pytest

import billing.docs.service as docs_models

from billing_functions.repositories import driver_mode_subscriptions


async def test_returns_none_if_no_docs(mock_docs_component):
    timestamp = dt.datetime(2021, 4, 20, tzinfo=dt.timezone.utc)
    repo = driver_mode_subscriptions.DocsAsRepository(mock_docs_component)
    doc = await repo.fetch('', '', timestamp)
    assert doc is None


@pytest.mark.json_obj_hook(Doc=docs_models.Doc)
async def test_chooses_correct_value(load_py_json):
    docs_mock = mock.Mock(spec=docs_models.Docs)
    future = asyncio.Future()
    future.set_result(load_py_json('subscriptions.json'))
    docs_mock.select = mock.Mock(return_value=future)

    timestamp = dt.datetime(2021, 4, 23, tzinfo=dt.timezone.utc)
    repo = driver_mode_subscriptions.DocsAsRepository(docs_mock)
    doc = await repo.fetch('some_park_id', 'some_driver_profile_id', timestamp)
    assert doc.id == 200000000
    assert docs_mock.select.call_args_list == [
        mock.call(mock.ANY, secondary_preferred=True),
    ]
