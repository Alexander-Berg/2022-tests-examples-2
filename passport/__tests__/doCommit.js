import {doCommit} from '../doCommit';

jest.mock('plog', () => ({
    warn: jest.fn().mockReturnValue({
        logId: jest.fn().mockReturnValue({
            type: jest.fn().mockReturnValue({
                write: jest.fn()
            })
        })
    })
}));

describe('passport/routes/authv2/authVerifyCommitRoute/doCommit.js', () => {
    const createReqMock = (req = {}) => ({
        api: {
            passwordConfirmCommit: jest.fn(),
            bundleSession: jest.fn(),
            track: jest.fn().mockReturnValue('akfbefbkf4wiyfw84g')
        },
        _controller: {
            augmentResponse: jest.fn()
        },
        body: {
            track_id: 'dsbsjhfvjwv',
            retpath: 'testRetPath'
        },
        headers: {
            ['x-real-scheme']: 'https'
        },
        hostname: 'passport.yandex.test',
        nquery: {
            origin: 'qwerty'
        },
        ...req
    });
    const createResMock = (res = {}) => ({
        json: jest.fn(),
        ...res
    });
    const next = jest.fn();

    beforeEach(() => {
        next.mockReset();
    });
    it('should return redirectPath to /auth when response any state', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockResolvedValue({
            body: {
                state: 'someState',
                status: 'ok',
                track_id: 'qwerty12345',
                retpath: 'testResultRetpath'
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'ok',
            redirectPath: 'https://passport.yandex.test/auth?track_id=qwerty12345&retpath=testResultRetpath'
        });
    });
    it('should return error object when bundleSession return status error', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockResolvedValue({
            body: {
                account: {
                    uid: '123'
                },
                status: 'ok'
            }
        });
        req.api.bundleSession.mockResolvedValue({
            body: {
                status: 'error',
                errors: ['some.error']
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'error',
            errors: ['some.error']
        });
    });
    it('should return redirectPath to /auth/finish/ when bundleSession return cookie', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockResolvedValue({
            body: {
                account: {
                    uid: '123'
                },
                status: 'ok'
            }
        });
        req.api.bundleSession.mockResolvedValue({
            body: {
                status: 'ok',
                cookies: 'foo: bar',
                track_id: 'qwerty12345',
                retpath: 'testResultRetpath'
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'ok',
            redirectPath: 'https://passport.yandex.test/auth/finish/?track_id=qwerty12345&retpath=testResultRetpath'
        });
    });
    it('should return redirectPath to retpath when status === "ok" without cookies', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockResolvedValue({
            body: {
                account: {
                    uid: '123'
                },
                status: 'ok'
            }
        });
        req.api.bundleSession.mockResolvedValue({
            body: {
                status: 'ok',
                track_id: 'qwerty12345',
                retpath: 'testResultRetpath'
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'ok',
            redirectPath: 'testResultRetpath'
        });
    });
    it('should return redirectPath to profile when status === "ok" without cookies and retpath', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockResolvedValue({
            body: {
                account: {
                    uid: '123'
                },
                status: 'ok'
            }
        });
        req.api.bundleSession.mockResolvedValue({
            body: {
                status: 'ok',
                track_id: 'qwerty12345'
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'ok',
            redirectPath: 'https://passport.yandex.test/profile'
        });
    });
    it('should return redirectPath to redirect?retpath when error action.not_required', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockRejectedValue({
            body: {
                errors: ['action.not_required'],
                status: 'error'
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'ok',
            redirectPath: 'https://passport.yandex.test/redirect?retpath=testRetPath'
        });
    });
    it('should return redirectPath to /auth when error sessionid.invalid', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockRejectedValue({
            body: {
                errors: ['sessionid.invalid'],
                status: 'error'
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'ok',
            redirectPath: 'https://passport.yandex.test/auth?retpath=testRetPath&origin=qwerty'
        });
    });
    it('should return redirectPath to /auth when error account.without_password', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockRejectedValue({
            body: {
                errors: ['account.without_password'],
                status: 'error'
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'ok',
            redirectPath: 'https://passport.yandex.test/profile/upgrade?origin=qwerty&retpath=testRetPath'
        });
    });
    it('should return error password.not_matched.2fa when error password.not_matched and account is 2fa', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockRejectedValue({
            body: {
                errors: ['password.not_matched'],
                status: 'error',
                account: {
                    is_2fa_enabled: true
                }
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'error',
            errors: ['password.not_matched.2fa']
        });
    });
    it('should return error when bundleSession resolved with error', async () => {
        const req = createReqMock();
        const res = createResMock();

        req.api.passwordConfirmCommit.mockResolvedValue({
            body: {
                account: {
                    uid: '123'
                },
                status: 'ok'
            }
        });
        req.api.bundleSession.mockResolvedValue({
            body: {
                status: 'error',
                errors: ['some_error']
            }
        });

        await doCommit(req, res, next);

        expect(res.json).toBeCalledWith({
            status: 'error',
            errors: ['some_error']
        });
    });
});
