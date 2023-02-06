import {errorHandler} from '../errorHandler';
import {processErrors} from '../../../../lib/passport-errors';

jest.mock('plog', () => ({
    warn: jest.fn().mockReturnValue({
        logId: jest.fn().mockReturnValue({
            type: jest.fn().mockReturnValue({
                write: jest.fn()
            })
        })
    })
}));

jest.mock('../../../../lib/passport-errors', () => ({
    processErrors: jest.fn().mockReturnValue([{code: 'testCode', msg: 'Some Text'}])
}));

describe('passport/routes/authv2/authVerify/errorHandler.js', () => {
    const createReqMock = (req = {}) => ({
        api: {
            passwordConfirmSubmit: jest.fn(),
            track: jest.fn().mockReturnValue('akfbefbkf4wiyfw84g')
        },
        headers: {
            ['x-real-scheme']: 'https'
        },
        hostname: 'passport.yandex.test',
        nquery: {
            retpath: 'testRetpath',
            origin: 'testOrigin'
        },
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
                },
                form: {
                    errors: {
                        password: {}
                    }
                }
            }
        },
        ...res
    });
    const next = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
        next.mockReset();
    });
    it('should redirect to /redirect with retpath when action.not_required', () => {
        const req = createReqMock();
        const res = createResMock();

        errorHandler(['action.not_required'], req, res, next);

        expect(res.redirect).toBeCalledWith('https://passport.yandex.test/redirect?retpath=testRetpath');
    });
    it('should redirect to /auth when sessionid.invalid', () => {
        const req = createReqMock();
        const res = createResMock();

        errorHandler(['sessionid.invalid'], req, res, next);

        expect(res.redirect).toBeCalledWith('https://passport.yandex.test/auth?retpath=testRetpath&origin=testOrigin');
    });
    it('should redirect to /profile/upgrade when account.without_password', () => {
        const req = createReqMock();
        const res = createResMock();

        errorHandler(['account.without_password'], req, res, next);

        expect(res.redirect).toBeCalledWith(
            'https://passport.yandex.test/profile/upgrade?origin=testOrigin&retpath=testRetpath'
        );
    });
    it('should set captchaRequired when captcha.required', () => {
        const req = createReqMock();
        const res = createResMock();

        errorHandler(['captcha.required'], req, res, next);

        expect(res.locals.store.form.captchaRequired).toEqual(true);
    });
    it('should set password.not_matched.2fa when password.not_matched for 2fa account', () => {
        const req = createReqMock();
        const res = createResMock({
            account: {
                is_2fa_enabled: true
            }
        });

        errorHandler(['password.not_matched'], req, res, next);

        expect(processErrors).toBeCalledWith(['password.not_matched.2fa'], undefined, {});
    });
});
