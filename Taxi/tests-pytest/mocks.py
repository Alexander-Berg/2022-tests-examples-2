"""Mock objects."""

import cStringIO


class FakeRequest(object):

    def __init__(
            self, content='', response_code=None, user_ip=None, user_agent='',
            headers=None, raw_content=None
    ):
        if raw_content is None:
            self.content = cStringIO.StringIO(content)
        else:
            self.content = raw_content
        self.response_code = response_code
        if headers is None:
            self.headers = {}
        else:
            self.headers = headers
        self.user_ip = user_ip
        self.user_agent = user_agent

    def setResponseCode(self, code):
        self.response_code = code

    def setHeader(self, name, value):
        self.headers[name] = value

    def getHeader(self, name):
        return self.headers.get(name)

    def getAllHeaders(self):
        return self.headers
