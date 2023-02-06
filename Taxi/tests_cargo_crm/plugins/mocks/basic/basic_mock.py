class BasicMock:
    def __init__(self):
        self.response_code = None
        self.response_json = None
        self.expected_data = None
        self.default_responses = {}

    def set_response(self, code, json):
        self.response_code = code
        self.response_json = json

    def set_response_by_code(self, code):
        self.set_response(
            code,
            self.default_responses.get(code, {'code': code, 'json': code}),
        )

    def get_response(self):
        if self.response_code is None:
            self.set_response_by_code(200)
        return {'code': self.response_code, 'json': self.response_json}

    def set_expected_data(self, data):
        self.expected_data = data

    def get_expected_data(self):
        return self.expected_data
