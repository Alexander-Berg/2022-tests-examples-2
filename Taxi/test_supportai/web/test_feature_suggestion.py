import pytest

from supportai.utils import feature_suggestions_helpers


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['default.sql', 'data.sql']),
]


@pytest.mark.config(
    SUPPORTAI_FEATURE_SUGGESTION_SETTINGS={
        'projects': 'all',
        'ignore_projects': [],
    },
)
async def test_suggestion_cache(web_context):
    await web_context.feature_suggestions_cache.refresh_cache()

    suggestions = await feature_suggestions_helpers.get_suggestions(
        context=web_context, project_slug='ya_lavka', feature='feature1',
    )

    assert set(suggestions) == {'0', '3', '1', '2'}

    await web_context.feature_suggestions_cache.add_suggestions(
        project_slug='ya_lavka', features={'feature1': '5'},
    )
    await web_context.feature_suggestions_cache.refresh_cache()

    suggestions = await feature_suggestions_helpers.get_suggestions(
        context=web_context, project_slug='ya_lavka', feature='feature1',
    )

    assert set(suggestions) == {'0', '2', '3', '1', '5'}

    await web_context.feature_suggestions_cache.add_suggestions(
        project_slug='ya_lavka',
        features={'feature98': 'value98', 'feature99': 'value99'},
    )

    suggestions = web_context.feature_suggestions_cache.suggestions_queue
    assert suggestions.qsize() == 2

    await web_context.feature_suggestions_cache.refresh_cache()

    suggestions = web_context.feature_suggestions_cache.suggestions_queue
    assert suggestions.empty()

    suggestions = await feature_suggestions_helpers.get_suggestions(
        context=web_context, project_slug='ya_lavka', feature='feature99',
    )
    assert suggestions == []
