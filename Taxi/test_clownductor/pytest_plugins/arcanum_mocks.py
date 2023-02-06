from typing import List
from typing import Optional

from aiohttp import web
import pytest

from arcanum_api import components as arcanum_api
from generated.models import arcanum as arcanum_models
from testsuite.mockserver import classes as mock_types


@pytest.fixture(name='arcanum_create_pull_request_mock')
async def _arcanum_create_pull_request_mock(patch, arcanum_pull_request_mock):
    def _wrapper(
            pr_number: Optional[int] = None,
            pr_url: Optional[str] = None,
            exc: Optional[arcanum_api.ArcanumApiBaseError] = None,
    ):
        @patch('arcanum_api.components.ArcanumClient.create_pull_request')
        async def _create_pull_request(*args, **kwargs):
            if exc:
                raise exc

            return arcanum_pull_request_mock(pr_number, pr_url)

        return _create_pull_request

    return _wrapper


@pytest.fixture(name='arcanum_get_pull_request_mock')
async def _arcanum_get_pull_request_mock(patch, arcanum_pull_request_mock):
    def _wrapper(
            pr_number: Optional[int] = None,
            pr_url: Optional[str] = None,
            merge_allowed: Optional[bool] = None,
            status: Optional[arcanum_api.PullRequestStatus] = None,
    ):
        @patch('arcanum_api.components.ArcanumClient.get_pull_request')
        async def _get_pull_request(*args, **kwargs):
            assert kwargs.pop('number') == pr_number
            return arcanum_pull_request_mock(
                pr_number=pr_number,
                pr_url=pr_url,
                merge_allowed=merge_allowed,
                status=status,
            )

        return _get_pull_request

    return _wrapper


@pytest.fixture(name='arcanum_get_review_request_mock')
def _arcanum_get_review_request_mock(
        mock_arcanum, arcanum_review_request_mock,
):
    def _wrapper(
            pr_number: int,
            pr_url: Optional[str] = None,
            full_status: Optional[arcanum_api.PullRequestStatus] = None,
            checks: List[arcanum_models.Check] = None,
    ):
        @mock_arcanum(f'/api/v1/review-requests/{pr_number}')
        def _get_review_request_handler(request: mock_types.MockserverRequest):
            review_mock = arcanum_review_request_mock(
                pr_number=pr_number,
                pr_url=pr_url,
                full_status=full_status,
                checks=checks,
            )

            return web.json_response(
                {'data': review_mock.serialize()}, status=200,
            )

        return _get_review_request_handler

    return _wrapper
