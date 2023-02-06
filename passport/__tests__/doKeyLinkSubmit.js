import _ from 'lodash';
import {doKeyLinkSubmit} from '../doKeyLinkSubmit';

describe('routes/authRegComplete/doKeyLinkSubmit', () => {
    const createReqMock = (req) =>
        _.merge(
            {
                query: {},
                api: {
                    authKeyLinkSubmit: jest.fn()
                }
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
                }
            },
            res
        );

    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should call request if secretKey is passed', async () => {
        const reqMock = createReqMock({
            query: {
                key: 'testKey'
            }
        });
        const resMock = createResMock();
        const nextMock = jest.fn();

        reqMock.api.authKeyLinkSubmit.mockResolvedValueOnce({
            body: {
                status: 'ok',
                state: 'complete_lite'
            }
        });

        await doKeyLinkSubmit(reqMock, resMock, nextMock);

        expect(reqMock.api.authKeyLinkSubmit).toBeCalled();
    });
    it('should not call request if secretKey is not passed', async () => {
        const reqMock = createReqMock();
        const resMock = createResMock();
        const nextMock = jest.fn();

        await doKeyLinkSubmit(reqMock, resMock, nextMock);

        expect(reqMock.api.authKeyLinkSubmit).not.toBeCalled();
    });
    it('should set skipSubmit=true if state = complete_autoregistered', async () => {
        const reqMock = createReqMock({
            query: {
                key: 'testKey'
            }
        });
        const resMock = createResMock();
        const nextMock = jest.fn();

        reqMock.api.authKeyLinkSubmit.mockResolvedValueOnce({
            body: {
                status: 'ok',
                state: 'complete_autoregistered'
            }
        });

        await doKeyLinkSubmit(reqMock, resMock, nextMock);

        expect(resMock.locals.skipSubmit).toEqual(true);
    });
});
