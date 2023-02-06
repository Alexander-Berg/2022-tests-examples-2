from pahtest.actions import Actions
from pahtest.browser import Browser
from pahtest.options import PlainOptions
from pahtest.results import PlanResult, TestResult


def test_wrong_selenium_url():
    """
    Failed connection to selenium should finish with "not ok - create browser"
    """
    actions = Actions(
        browser=Browser(hub_url='wrong_url', name='chrome'),
        options=PlainOptions(
            name='test', code=dict(browser='chrome', width=800, height=600)
        ),
        code=[{'get_ok': '/'}],
    )
    results = actions.run()
    # - only two results: plan and "not ok - create browser"
    assert 2 == len(results.list), results
    assert isinstance(results.list[0], PlanResult)
    assert isinstance(results.list[1], TestResult)
    # - "not ok - create browser" has correct text
    assert 'create browser' == results.list[1].description
    assert 'Wrong selenium hub url' in results.list[1].message
