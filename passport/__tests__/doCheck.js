import doCheck from '../doCheck.js';

const users = [
    {
        id: '1',
        status: {
            value: 'VALID'
        }
    },
    {
        id: '2',
        status: {
            value: 'INVALID'
        }
    }
];

const validSessionInfo = {
    status: {
        value: 'VALID'
    },
    default_uid: '1',
    users: users
};

const invalidSessionInfo = {
    status: {
        value: 'INVALID'
    },
    default_uid: '2',
    users: users
};

const sessionIDMock2 = function() {
    return new Promise((resolve, reject) => {
        process.nextTick(() =>
            // eslint-disable-next-line no-constant-condition
            true
                ? resolve(validSessionInfo)
                : reject({
                      error: 'User with not found.'
                  })
        );
    });
};

const req = {
    _controller: {
        redirectToAuth: jest.fn(),
        getAuth: jest.fn(() => {
            return {
                sessionID: sessionIDMock2
            };
        })
    }
};

describe('checkAuth', () => {
    describe('doCheck', () => {
        test('it should return JSON with status', () => {
            return doCheck(req).then((data) => {
                expect(data.status).toBeDefined();
            });
        });

        test('it should return JSON with status === ok', () => {
            return doCheck(req).then((data) => {
                expect(data.status).toEqual('ok');
            });
        });

        test('it should return JSON with status === error', () => {
            expect.assertions(1);
            const req = {
                _controller: {
                    getAuth: jest.fn(() => {
                        return {
                            sessionID: function() {
                                return new Promise((resolve, reject) => {
                                    process.nextTick(() => reject(invalidSessionInfo));
                                });
                            }
                        };
                    })
                }
            };

            return doCheck(req).catch((data) => {
                expect(data.status).toEqual('error');
            });
        });

        test('it should return JSON with status === ok if err.code === need_resign', () => {
            expect.assertions(1);
            const req = {
                _controller: {
                    getAuth: jest.fn(() => {
                        return {
                            sessionID: function() {
                                return new Promise((resolve, reject) => {
                                    process.nextTick(() => reject({code: 'need_resign'}));
                                });
                            }
                        };
                    })
                }
            };

            return doCheck(req).then((data) => {
                expect(data.status).toEqual('ok');
            });
        });
    });
});
