import pytest

import sandbox.projects.quasar.check_release_status.lib.validate as validate


BRANCH = "85"
OWNER = "staff"


@pytest.mark.parametrize("issues", [
    [],
    [
        validate.Issue(
            "ST-1",
            ["tag"],
            validate.IssueStatus(validate.EIssueStatusId.BETA.value, "prod")
        )
    ],
    [
        validate.Issue(
            "ST-1",
            [23],
            validate.IssueStatus(validate.EIssueStatusId.BETA.value, "prod")
        )
    ]
])
def test_missing(issues):
    with pytest.raises(validate.error.MissingIssueError):
        validate.validate_startrek(
            issues,
            BRANCH,
            OWNER,
            validate.EIssueStatusId.BETA
        )


@pytest.mark.parametrize("issues", [
    [
        validate.Issue(
            "ST-1",
            [validate.IssueTag.STATION.value],
            validate.IssueStatus(1, "prod")
        )
    ],
    [
        validate.Issue(
            "ST-1",
            [validate.IssueTag.STATION.value],
            validate.IssueStatus(1, "prod")
        ),
        validate.Issue(
            "ST-1",
            ["tag"],
            validate.IssueStatus(1, "prod")
        ),
    ],
    [
        validate.Issue(
            "ST-1",
            [validate.IssueTag.STATION_MAX.value],
            validate.IssueStatus(1, "prod")
        ),
        validate.Issue(
            "ST-1",
            ["tag"],
            validate.IssueStatus(1, "prod")
        ),
    ],
    [
        validate.Issue(
            "ST-1",
            [validate.IssueTag.STATION.value],
            validate.IssueStatus(1, "prod")
        ),
        validate.Issue(
            "ST-2",
            [validate.IssueTag.STATION_MAX.value],
            validate.IssueStatus(1, "prod")
        ),
        validate.Issue(
            "ST-3",
            [validate.IssueTag.STATION_MAX.value],
            validate.IssueStatus(1, "prod")
        )
    ]
])
def test_incorrect_number(issues):
    with pytest.raises(validate.error.IncorrectIssueCountError):
        validate.validate_startrek(
            issues,
            BRANCH,
            OWNER,
            validate.EIssueStatusId.BETA
        )


@pytest.mark.parametrize("issue_status", [
    validate.EIssueStatusId.PRODUCTION.value,
    -1,
    "status",
    None
])
def test_incorrect_status(issue_status):
    issues = [
        validate.Issue(
            "ST-1",
            [validate.IssueTag.STATION.value],
            validate.IssueStatus(issue_status, "prod")
        ),
        validate.Issue(
            "ST-2",
            [validate.IssueTag.STATION_MAX.value],
            validate.IssueStatus(issue_status, "prod")
        )
    ]
    with pytest.raises(validate.error.IncorrectIssueStatusError):
        validate.validate_startrek(
            issues,
            BRANCH,
            OWNER,
            validate.EIssueStatusId.BETA
        )


@pytest.mark.parametrize("issues", [
    [
        validate.Issue(
            "ST-1",
            [validate.IssueTag.STATION.value],
            validate.IssueStatus(validate.EIssueStatusId.BETA.value, "beta")
        ),
        validate.Issue(
            "ST-2",
            [validate.IssueTag.STATION_MAX.value],
            validate.IssueStatus(validate.EIssueStatusId.BETA.value, "beta")
        )
    ],
])
def test_valid(issues):
    validate.validate_startrek(
        issues,
        BRANCH,
        OWNER,
        validate.EIssueStatusId.BETA
    )
