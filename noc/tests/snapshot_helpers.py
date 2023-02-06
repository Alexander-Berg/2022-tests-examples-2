"""Инструменты для snapshot-тестирования (aka golden-file-тестирование)

Идея в том, что тест генерирует данные (actual, фактический результат), которые
сравниваются с неким эталоном (expected, ожидаемый результат), расположенным в
отдельном файле. Этот эталон - это golden-файл или snapshot.

Для удобства snapshot первый раз генерируется прямо из теста. При этом
выбросится исключение вида RuntimeError("Snapshot created").

Когда snapshot-файл уже существует, происходит сравнение фактического и
ожидаемого результата.

При необходимости обновить сразу несколько снапшотов из тестов нужно запустить
тесты с переменной окружения UPDATE_SNAPSHOTS, например:

env UPDATE_SNAPSHOTS=true pytest -vvv tests/dir

в этом случае снапшоты перезапишутся на фактический результат из тестов.

Фикстуры для БД лежат рядом в директории .inputs, их надо готовить руками или
скопировать из снапшотов.
"""

import contextlib
import json
import os
import os.path
import pathlib
import typing

import aiohttp
import aiohttp.web
from _pytest.fixtures import FixtureRequest

import mongo_helpers


class Target:
    pass


DATABASE = Target()
"""Database sentinel."""

YT = Target()
"""YT sentinel."""


async def create_http_client_response_snapshot(
    resp: aiohttp.ClientResponse,
) -> typing.Any:
    if resp.content_type.startswith("application/json"):
        resp_body = await resp.json()
    else:
        resp_body = await resp.text()

    headers = dict(resp.headers)
    for ignored_header in ["Date", "Server", "Content-Length"]:
        if ignored_header in headers:
            headers.pop(ignored_header)

    cookies_dict = dict(resp.cookies)
    return {
        "body": resp_body,
        "status": resp.status,
        "headers": headers,
        "cookies": cookies_dict,
    }


async def create_http_response_snapshot(resp: aiohttp.web.Response) -> typing.Any:
    if resp.body is not None:
        if resp.content_type.startswith("application/json"):
            resp_body = json.loads(resp.body)
        else:
            resp_body = resp.body.decode()
    else:
        resp_body = None

    headers = dict(resp.headers)
    for ignored_header in ["Date", "Server", "Content-Length"]:
        if ignored_header in headers:
            headers.pop(ignored_header)

    cookies_dict = dict(resp.cookies)
    return {
        "body": resp_body,
        "status": resp.status,
        "headers": headers,
        "cookies": cookies_dict,
    }


async def create_http_request_snapshot(req: aiohttp.web.BaseRequest) -> typing.Any:
    if req.body_exists:
        if req.content_type.startswith("application/json"):
            body = await req.json()
        else:
            body = await req.text()
    else:
        body = None
    headers = dict(req.headers)
    for ignored_header in [
        "Accept",
        "Accept-Encoding",
        "Host",
        "User-Agent",
        "Content-Length",
    ]:
        if ignored_header in headers:
            headers.pop(ignored_header)
    cookies_dict = dict(req.cookies)
    return {
        "method": req.method,
        "url": str(req.rel_url),
        "body": body,
        "headers": headers,
        "cookies": cookies_dict,
    }


async def create_database_snapshot() -> typing.Any:
    db_uri = os.environ["DATABASE_URL"]
    return json.loads(await mongo_helpers.dump(db_uri))


@contextlib.asynccontextmanager
async def apply_database_fixture(data: typing.Any) -> typing.AsyncGenerator[None, None]:
    db_uri = os.environ["DATABASE_URL"]
    await mongo_helpers.load(db_uri, json.dumps(data))
    yield


def snapshot(request: FixtureRequest):
    update_snapshots = "UPDATE_SNAPSHOTS" in os.environ

    async def inner(
        *targets: typing.Union[aiohttp.ClientResponse, Target, aiohttp.web.BaseRequest]
    ) -> None:
        actual: typing.Dict[str, typing.Any] = {}
        for t in targets:
            if isinstance(t, aiohttp.ClientResponse):
                actual["http_response"] = await create_http_client_response_snapshot(t)
            elif isinstance(t, aiohttp.web.BaseRequest):
                actual["http_request"] = await create_http_request_snapshot(t)
            elif isinstance(t, aiohttp.web.Response):
                actual["http_response"] = await create_http_response_snapshot(t)
            elif (
                isinstance(t, tuple)
                and len(t) == 2
                and isinstance(t[0], aiohttp.web.BaseRequest)
                and isinstance(t[1], aiohttp.web.Response)
            ):
                actual["http_request"] = await create_http_request_snapshot(t[0])
                actual["http_response"] = await create_http_response_snapshot(t[1])
            elif t is DATABASE:
                actual["database"] = await create_database_snapshot()

        snapshot_file_path = (
            pathlib.Path(request.fspath).parent
            / ".snapshots"
            / (request.node.name + ".json")
        )

        if not os.path.exists(snapshot_file_path):
            os.makedirs(os.path.dirname(snapshot_file_path), exist_ok=True)
            with open(snapshot_file_path, "w") as f:
                json.dump(
                    actual, f, indent=2, ensure_ascii=False, sort_keys=True,
                )
                f.write("\n")
            raise RuntimeError(f"Snapshot created: {snapshot_file_path}")

        if update_snapshots:
            with open(snapshot_file_path, "w") as f:
                json.dump(
                    actual, f, indent=2, ensure_ascii=False, sort_keys=True,
                )
                f.write("\n")
        with open(snapshot_file_path, "r") as f:
            expected = json.loads(f.read())
        # assert check_objects(actual, expected)
        assert actual == expected

    return inner


@contextlib.asynccontextmanager
async def apply_fixtures(request: FixtureRequest) -> typing.AsyncGenerator[None, None]:
    input_file_path = (
        pathlib.Path(request.fspath).parent / ".inputs" / (request.node.name + ".json")
    )
    is_parametrized_test = "[" in request.node.name and request.node.name.endswith("]")
    if not os.path.exists(input_file_path) and is_parametrized_test:
        unparametrized_test_name = request.node.name.rsplit("[", 1)[0]
        input_file_path = (
            pathlib.Path(request.fspath).parent
            / ".inputs"
            / (unparametrized_test_name + ".json")
        )
    with open(input_file_path, "r") as f:
        input_data = json.loads(f.read())
    async_context_managers = []
    if "database" in input_data:
        async_context_managers.append(apply_database_fixture(input_data["database"]))
    async with contextlib.AsyncExitStack() as stack:
        # enter all async context managers
        for async_ctx in async_context_managers:
            await stack.enter_async_context(async_ctx)
        yield
