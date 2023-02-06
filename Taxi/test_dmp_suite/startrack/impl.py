__all__ = [
    'EXISTED_ATTACHMENT_NAME', 'NOT_EXISTED_ATTACHMENT_NAME', 'TEST_TASK', 'CURRENT_STATUS', 'NEW_STATUS',
    'MockStartrack', 'CREATED_AT_SECOND',
]

EXISTED_ATTACHMENT_NAME = 'existed_attachment'
CREATED_AT_FIRST = '2020-02-01 08:43:22.967670'
CREATED_AT_SECOND = '2020-02-22 08:43:22.967670'

EXISTED_ATTACHMENTS = [
    {'name': EXISTED_ATTACHMENT_NAME, 'createdAt': CREATED_AT_FIRST},
    {'name': EXISTED_ATTACHMENT_NAME, 'createdAt': CREATED_AT_SECOND},
]

NOT_EXISTED_ATTACHMENT_NAME = 'not_existed_attachment'
TEST_TASK = 'TEST-1234'
CURRENT_STATUS = 'CURRENT'
NEW_STATUS = 'NEW'


"""
Mock classes for Startrack client
"""


class MockBase(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class MockTransitions(object):
    def __init__(self, issue):
        self._issue = issue

    def get_all(self):
        return [MockBase(id=NEW_STATUS)]

    def execute(self):
        self._issue.status.key = NEW_STATUS

    def __getitem__(self, item):
        return self


class MockAttachment(MockBase):
    def __init__(self, **kwargs):
        super(MockAttachment, self).__init__(**kwargs)
        self._is_downloaded = False

    def download_to(self, *args):
        self._is_downloaded = True

    @property
    def is_downloaded(self):
        return self._is_downloaded


class MockIssue(object):
    def __init__(self, attachments=None):
        self.attachments = [
            MockAttachment(**i) for i in attachments
        ]
        self.status = MockBase(key=CURRENT_STATUS)
        self.transitions = MockTransitions(issue=self)


class MockStartrack(object):

    def __init__(self):
        self.issues = {
            TEST_TASK: MockIssue(attachments=EXISTED_ATTACHMENTS)
        }
