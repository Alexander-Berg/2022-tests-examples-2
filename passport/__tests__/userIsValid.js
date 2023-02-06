// jest.mock('../doCheck');

import userIsValid from '../userIsValid.js';

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

describe('userIsValid', () => {
    test('it should call next if something went wrong', () => {
        expect.assertions(1);

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

        const res = {
            locals: {}
        };

        return userIsValid(req, res, nextMock).then(() => expect(nextMock).toHaveBeenCalled());
    });

    test('it should write userIsValid === false if something went wrong', () => {
        expect.assertions(1);

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

        const res = {
            locals: {}
        };

        return userIsValid(req, res, nextMock).then(() => expect(res.locals.userIsValid).toBe(false));
    });

    test('it should call next if everything is ok', () => {
        expect.assertions(1);

        const req = {
            _controller: {
                redirectToAuth: jest.fn(),
                getAuth: jest.fn(() => {
                    return {
                        sessionID: sessionIDMock
                    };
                })
            }
        };

        const res = {
            locals: {}
        };

        return userIsValid(req, res, nextMock).then(() => expect(nextMock).toHaveBeenCalled());
    });

    test('it should write userIsValid === true if everything is ok', () => {
        expect.assertions(1);

        const req = {
            _controller: {
                redirectToAuth: jest.fn(),
                getAuth: jest.fn(() => {
                    return {
                        sessionID: sessionIDMock
                    };
                })
            }
        };

        const res = {
            locals: {}
        };

        return userIsValid(req, res, nextMock).then(() => expect(res.locals.userIsValid).toBe(true));
    });
});
