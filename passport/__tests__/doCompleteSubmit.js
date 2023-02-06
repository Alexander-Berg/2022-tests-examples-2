import _ from 'lodash';
import {doCompleteSubmit} from '../doCompleteSubmit';

describe('routes/authRegComplete/doCompleteSubmit', () => {
    const createReqMock = (req) =>
        _.merge(
            {
                api: {
                    completeSubmit: jest.fn()
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
                        form: {
                            validation: {}
                        },
                        person: {}
                    },
                    result: {}
                }
            },
            res
        );

    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should skip request if pass res.locals.skipSubmit', async () => {
        const reqMock = createReqMock();
        const resMock = {
            locals: {
                skipSubmit: true
            }
        };
        const nextMock = jest.fn();

        await doCompleteSubmit(reqMock, resMock, nextMock);

        expect(reqMock.api.completeSubmit).not.toBeCalled();
    });
    it('should modify form.type after success request', async () => {
        const reqMock = createReqMock();
        const resMock = createResMock({
            locals: {
                store: {
                    common: {
                        track_id: 'asdqwe',
                        retpath: 'test/auth'
                    }
                }
            }
        });
        const nextMock = jest.fn();

        reqMock.api.completeSubmit.mockResolvedValueOnce({
            body: {
                status: 'ok',
                state: 'complete_lite'
            }
        });

        await doCompleteSubmit(reqMock, resMock, nextMock);

        expect(reqMock.api.completeSubmit).toBeCalledWith({track_id: 'asdqwe', retpath: 'test/auth'});
        expect(resMock.locals.store.form.type).toEqual('complete_lite');
    });
    it('should throw error after failed request', async () => {
        const reqMock = createReqMock();
        const resMock = createResMock();
        const nextMock = jest.fn();

        reqMock.api.completeSubmit.mockResolvedValueOnce({
            body: {
                status: 'fail'
            }
        });

        await doCompleteSubmit(reqMock, resMock, nextMock);

        expect(nextMock).toBeCalledWith(new Error());
    });
});
