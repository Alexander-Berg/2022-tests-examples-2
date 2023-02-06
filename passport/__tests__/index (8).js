// jest.mock('../doCheck');

import checkAuth from '../';

const nextMock = jest.fn();

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

const sessionIDMock = function() {
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

const sessionIDMock2 = function() {
    return new Promise((resolve, reject) => {
        process.nextTick(() =>
            // eslint-disable-next-line no-constant-condition
            true
                ? resolve(invalidSessionInfo)
                : reject({
                      error: 'User with not found.'
                  })
        );
    });
};

describe('checkAuth', () => {
    test('it should call redirectToAuth if something went wrong', () => {
        const req = {
            headers: {},
            _controller: {
                redirectToAuth: jest.fn(),
                getAuth: jest.fn(() => {
                    return {
                        sessionID: sessionIDMock2
                    };
                })
            }
        };

        return checkAuth(req, null, nextMock).then(() => expect(req._controller.redirectToAuth).toHaveBeenCalled());
    });

    test('it should call next if everything is ok', () => {
        const req = {
            headers: {},
            _controller: {
                redirectToAuth: jest.fn(),
                getAuth: jest.fn(() => {
                    return {
                        sessionID: sessionIDMock
                    };
                })
            }
        };

        return checkAuth(req, null, nextMock).then(() => expect(nextMock).toHaveBeenCalled());
    });

    test('it should send statusCode 403', () => {
        const req = {
            headers: {
                'x-requested-with': 'XMLHttpRequest'
            },
            _controller: {
                getAuth: jest.fn(() => {
                    return {
                        sessionID: sessionIDMock2
                    };
                })
            }
        };
        const res = {
            sendStatus: jest.fn()
        };

        return checkAuth(req, res, nextMock).then(() => expect(res.sendStatus).toHaveBeenCalledWith(403));
    });
});
