#!/usr/bin/env python3
import argparse
import asyncio
import dataclasses
import logging
from typing import Optional

from scripts import build_endpoint_def as builder
from scripts import clusters
from scripts import common


logger = logging.getLogger('common')


@dataclasses.dataclass
class CodeError:
    code: str
    message: str
    location: Optional[str] = None


class ValidationFailed(Exception):
    def __init__(self, cluster, endpoint_id, json):
        self.cluster = cluster
        self.endpoint_id = endpoint_id
        self.json = json
        self.code = 'validation_failed'
        self.message = json['message']
        self.errors = [
            CodeError(**err)
            for err in json.get('details', {}).get('errors', [])
        ]
        errors = '\n---\n'.join(
            [
                f'{err.code} at {err.location}\n {err.message}'
                for err in self.errors
            ],
        )
        msg = (
            f'endpoint cluster={cluster} id={endpoint_id}: '
            f'{self.message}\n{errors}'
        )
        super().__init__(msg)


class TestsFailed(Exception):
    def __init__(self, cluster, endpoint_id, message):
        self.cluster = cluster
        self.endpoint_id = endpoint_id
        self.message = message
        super().__init__(
            f'endpoint cluster={cluster} id={endpoint_id}:\n'
            f'{self.message}',
        )


class TestsRequestFailed(Exception):
    def __init__(self, cluster, endpoint_id, json):
        self.cluster = cluster
        self.endpoint_id = endpoint_id
        self.json = json
        super().__init__(
            f'endpoint cluster={cluster} id={endpoint_id}:\n' f'{self.json}',
        )


async def make_error(cluster, endpoint_id, resp) -> Exception:
    try:
        json = await resp.json()
        if json['code'] == 'tests_failed':
            return TestsFailed(cluster, endpoint_id, json['message'])
        if json['code'] == 'validation_failed':
            return ValidationFailed(cluster, endpoint_id, json)
    except (common.aiohttp.ClientResponseError, KeyError):
        pass
    return await common.RequestFailed.make(cluster, endpoint_id, resp)


async def run_test(
        cluster: str,
        ep_id: str,
        endpoint: builder.Endpoint,
        context: common.Context,
        env: common.Environment,
):
    body = dataclasses.asdict(endpoint)
    body['revision'] = 0
    body['git_commit_hash'] = 'run-test-commit'

    resp = await common.request_api_proxy_manager(
        context,
        env,
        'POST',
        'admin/v2/endpoints/tests',
        params={'cluster': cluster, 'id': ep_id},
        body=body,
    )

    if resp.status != 200:
        logger.debug(f'Response: "{await resp.text()}"')
        raise await make_error(cluster, ep_id, resp)
    else:
        logger.info(f'Tests for endpoint cluster={cluster} id={ep_id} OK')


async def amain(args):
    async with common.Context() as context:
        logger.setLevel(args.log_level)
        uuid = args.endpoint_uuid
        cluster = clusters.cluster_from_alias(uuid.cluster_alias)
        logger.info(
            f'Running tests for endpoint '
            f'cluster={cluster.service}  id={uuid.endpoint_id}',
        )
        endpoint = builder.make_endpoint_def(cluster, uuid.endpoint_id)
        await run_test(
            cluster.service,
            uuid.endpoint_id,
            endpoint,
            context,
            args.environment,
        )


def _args():
    parser = argparse.ArgumentParser(
        description='Builds endpoint revision request body',
    )
    parser.add_argument(
        '-e', '--environment', type=common.Environment, required=True,
    )
    parser.add_argument('-u', '--endpoint-uuid', type=common.EndpointUUID)
    parser.add_argument(
        '-l',
        '--log-level',
        type=common.parse_log_level,
        required=False,
        default=logging.INFO,
    )
    return parser.parse_args()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(amain(_args()))


if __name__ == '__main__':
    main()
