import contextlib

import pytest

from metrics_processing.tagging import utils as tags_utils
from taxi.clients.tags import TagsRequestError

from taxi_driver_metrics.common.utils import tags_manager


@pytest.mark.parametrize('fail', [True, False])
@pytest.mark.parametrize('policy', ['strict', 'liberal'])
@pytest.mark.parametrize('policy_override', ['strict', 'liberal', None])
@pytest.mark.config(DRIVER_METRICS_ENABLE_TAG_FETCHER=True)
async def test_policies(
        web_context,
        fail,
        policy,
        policy_override,
        tags_service_mock,
        mockserver,
):
    def match_profile_return(*args, **kwargs):
        if fail:
            return mockserver.make_response('internal error', status=500)
        return {}

    tags_service_mock(match_profile_return=match_profile_return)
    setattr(web_context.config, 'DRIVER_METRICS_TAGS_POLICY', policy)

    tags_manager_ = tags_manager.TagsManager(
        web_context.config,
        web_context.tags_client,
        web_context.driver_tags_client,
    )

    with contextlib.ExitStack() as stack:
        if policy_override:
            new_policy = tags_utils.TagsPolicy(policy_override)
            stack.enter_context(tags_manager_.policy(new_policy))
        if (policy_override or policy) == 'strict' and fail:
            stack.enter_context(pytest.raises(TagsRequestError))
        await tags_manager_.fetch_service_tags('udid', None, None)
