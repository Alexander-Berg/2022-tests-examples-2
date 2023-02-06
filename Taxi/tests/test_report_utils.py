import json

from taxi_buildagent import report_utils as utils


def test_serializing_pr_reports():
    test_list = [
        utils.PullRequestReport(
            pull_request=utils.PullRequest(
                number=1,
                url='http://foo/1',
                staff_user='foo',
                title=None,
                labels=None,
                from_branch=None,
            ),
            reason='merge conflict',
            category=utils.CATEGORY_MERGE_CONFLICT,
            other_pr=utils.PullRequest(
                number=2,
                url='http://foo/2',
                staff_user='somebody',
                title=None,
                labels=None,
                from_branch=None,
            ),
        ),
        utils.PullRequestReport(
            pull_request=utils.PullRequest(
                number=2,
                url='http://foo/2',
                staff_user='bar',
                title=None,
                labels=None,
                from_branch=None,
            ),
            reason='develop',
            category=utils.CATEGORY_LABEL_TTL_EXCEEDED,
        ),
    ]

    dumped = utils.dump_pr_reports(test_list)

    assert json.loads(dumped) == [
        {
            'pull_request': {
                'number': 1,
                'url': 'http://foo/1',
                'staff_user': 'foo',
                'title': None,
                'labels': None,
                'from_branch': None,
            },
            'reason': 'merge conflict',
            'category': 2,
            'other_pr': {
                'number': 2,
                'url': 'http://foo/2',
                'staff_user': 'somebody',
                'title': None,
                'labels': None,
                'from_branch': None,
            },
        },
        {
            'pull_request': {
                'number': 2,
                'url': 'http://foo/2',
                'staff_user': 'bar',
                'title': None,
                'labels': None,
                'from_branch': None,
            },
            'reason': 'develop',
            'category': 1,
            'other_pr': None,
        },
    ]
    assert utils.load_pr_reports(dumped) == test_list
