import {doSubmit} from '../doSubmit';
import {errorHandler} from '../errorHandler';

jest.mock('plog', () => ({
    warn: jest.fn().mockReturnValue({
        logId: jest.fn().mockReturnValue({
            type: jest.fn().mockReturnValue({
                write: jest.fn()
            })
        })
    })
}));

jest.mock('../errorHandler', () => ({
    errorHandler: jest.fn()
}));

describe('passport/routes/authv2/authVerify/doSubmit.js', () => {
    const createReqMock = (req = {}) => ({
        api: {
            passwordConfirmSubmit: jest.fn(),
            track: jest.fn().mockReturnValue('akfbefbkf4wiyfw84g')
        },
        headers: {
            ['x-real-scheme']: 'https'
        },
        hostname: 'passport.yandex.test',
        ...req
    });
    const createResMock = (res = {}) => ({
        redirect: jest.fn(),
        locals: {
            store: {
                common: {},
                auth: {
                    processedAccount: {
                        uid: '123456'
                    }
                }
            }
        },
        ...res
    });
    const next = jest.fn();

    beforeEach(() => {
        next.mockReset();
    });
    it('should call next when status === "ok" ', async () => {
        const req = createReqMock();
        const res = createResMock();
        const result = {
            body: {
                account: {
                    uid: '123456'
                },
                status: 'ok'
            }
        };

        req.api.passwordConfirmSubmit.mockResolvedValue(result);

        await doSubmit(req, res, next);

        expect(next).toBeCalled();
    });
    it('should call errorHandler when status !== "ok" ', async () => {
        const req = createReqMock();
        const res = createResMock();
        const result = {
            body: {
                account: {
                    uid: '123456'
                },
                status: 'error',
                errors: ['testError']
            }
        };

        req.api.passwordConfirmSubmit.mockResolvedValue(result);

        await doSubmit(req, res, next);

        expect(errorHandler).toBeCalledWith(result.body.errors, req, res, next);
    });
});
