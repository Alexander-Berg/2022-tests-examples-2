import pytest


from meta_etl.layer.notificator.impl import NotificationIssue, NotificationSender


CASES = [
    'TAXIDMPNOTICE-372',
    'TAXIDMPNOTICE-373'
]


@pytest.mark.slow
@pytest.mark.parametrize("issue_name", CASES)
def test_attributes(issue_name):
    # TODO: DMPDEV-5608
    pass
