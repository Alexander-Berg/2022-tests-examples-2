from dateutil import parser


class UserTrackerFixture:
    def __init__(self, mockserver):
        self.mockserver = mockserver
        self.installed = False
        self.args = {}
        self.expected = 0
        self.called = 0
        self.should_fail = False

    def expect(self, args, times=1):
        self.args = args
        self.called = 0
        self.expected = times
        self._install()

    def set_fail(self, fail=True):
        self.should_fail = fail

    def _install(self):
        if self.installed:
            return
        self.installed = True
        # pylint: disable=unused-variable
        @self.mockserver.handler('/fleet-tracking-system/v1/position/store')
        def position_store(request):
            assert len(request.json['positions']) == 1
            data = request.json['positions'][0]
            self.called += 1

            assert request.headers['X-YaFts-Client-Service-Tvm'] == '0'
            assert request.args['pipeline'] == 'go-users'
            assert data['source'] == 'Verified'
            if 'accuracy' in data['geodata']:
                assert data['geodata']['accuracy'] == self.args['accuracy']
            if 'point' in self.args:
                point = self.args['point']
                assert data['geodata']['lon'] == point[0]
                assert data['geodata']['lat'] == point[1]
            if 'time' in self.args:
                timestamp = parser.parse(self.args['time']).timestamp()
                assert data['timestamp'] == timestamp * 1000
            if 'user_id' in self.args:
                assert request.args['uuid'] == 'users_' + self.args['user_id']
            return self.mockserver.make_response('Ok', 200)

    def finalize(self):
        assert self.called == self.expected
