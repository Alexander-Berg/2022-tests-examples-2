import _ from 'lodash';
import {handleNonFormErrors} from '../handleNonFormErrors';

jest.mock('plog', () => ({
    warn: jest.fn().mockReturnValue({
        logId: jest.fn().mockReturnValue({
            type: jest.fn().mockReturnValue({
                write: jest.fn()
            })
        })
    })
}));

describe('routes/authRegComplete/handleNonFormErrors', () => {
    const createReqMock = (req) =>
        _.merge(
            {
                query: {},
                api: {
                    authKeyLinkSubmit: jest.fn()
                },
                originalUrl: 'https://yandex.test/',
                headers: ['x-real-scheme'],
                hostname: 'yandex.test/'
            },
            req
        );
    const createResMock = (res) =>
        _.merge(
            {
                locals: {
                    store: {
                        settings: {},
                        common: {},
                        form: {},
                        person: {}
                    }
                },
                json: jest.fn(),
                redirect: jest.fn()
            },
            res
        );

    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should call json for POST', () => {
        const errMock = 'SOME_TEST_ERROR';
        const reqMock = createReqMock({
            method: 'POST'
        });
        const resMock = createResMock();
        const nextMock = jest.fn();

        handleNonFormErrors(errMock, reqMock, resMock, nextMock);

        expect(resMock.json).toBeCalledWith({status: 'error', error: 'SOME_TEST_ERROR'});
    });
    it('should call next with error if it instanceof Error', () => {
        const errMock = new Error('SOME_TEST_ERROR');
        const reqMock = createReqMock();
        const resMock = createResMock();
        const nextMock = jest.fn();

        handleNonFormErrors(errMock, reqMock, resMock, nextMock);

        expect(nextMock).toBeCalledWith(errMock);
    });
    it.each([
        ['action.not_required', 'yandex.test/passport?mode=passport'],
        ['account.disabled', 'yandex.test/passport?mode=passport'],
        ['account.global_logout', 'yandex.test/passport?mode=passport'],
        ['sessionid.invalid', 'yandex.test/auth?retpath=yandex.test%2F%2F'],
        ['sslsession.required', 'yandex.test/auth/secure?retpath=yandex.test%2F%2F']
    ])('should redirect if error is %o to url %o', (error, url) => {
        const errMock = [error];
        const reqMock = createReqMock();
        const resMock = createResMock();
        const nextMock = jest.fn();

        handleNonFormErrors(errMock, reqMock, resMock, nextMock);

        expect(resMock.redirect).toBeCalledWith(url);
    });
    it('should next with error as is', () => {
        const errMock = ['new.error'];
        const reqMock = createReqMock();
        const resMock = createResMock();
        const nextMock = jest.fn();

        handleNonFormErrors(errMock, reqMock, resMock, nextMock);

        expect(nextMock).toBeCalledWith(errMock);
    });
});
