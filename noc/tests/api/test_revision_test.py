import unittest.mock
import bson
import pytest


@pytest.mark.asyncio
async def test_revision_test_create(api_client, core):
    form_data = {
        "base_remote": "base-remote-url",
        "base_commit": "base-commit",
        "test_remote": "test-remote-url",
        "test_commit": "test-commit",
        "test_hostnames": ["host1", "host2"],
    }
    core.create_test = unittest.mock.AsyncMock()

    await api_client.post("/v1/test", data=form_data)
    core.create_test.assert_called_once_with(
        base_remote=form_data["base_remote"],
        base_commit=form_data["base_commit"],
        test_remote=form_data["test_remote"],
        test_commit=form_data["test_commit"],
        test_hostnames=form_data["test_hostnames"],
        chunk_size=None,
        staging_env_id="",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("query, params", (
    ("", {}),
    ("id=000000000000000000000000", {"_id": bson.objectid.ObjectId("000000000000000000000000")}),
    ("left_revision=somerevision", {"left_revision": "somerevision"}),
    ("right_revision=somerevision", {"right_revision": "somerevision"}),
))
async def test_revision_test_list(query, params, api_client, core):
    path = "checkist.ann.revision.RevisionTest.find_by_query"
    with unittest.mock.patch(path) as find_by_query:
        await api_client.get(f"/v1/test?{query}")
        find_by_query.assert_called_once_with(core, params)
