import _ from 'lodash';
import plog from 'plog';
import {profileGetState} from '../profileGetState';

jest.mock('plog', () => ({
    warn: jest.fn().mockReturnValue({
        logId: jest.fn().mockReturnValue({
            type: jest.fn().mockReturnValue({
                write: jest.fn()
            })
        })
    })
}));

describe('routes/authRegComplete/profileGetState', () => {
    const createReqMock = (req) =>
        _.merge(
            {
                query: {},
                api: {
                    profileGetState: jest.fn()
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
                            values: {},
                            states: {}
                        },
                        person: {}
                    }
                }
            },
            res
        );

    afterEach(() => {
        jest.clearAllMocks();
    });
    it('should call profileGetState and set person information', async () => {
        const reqMock = createReqMock({
            method: 'POST'
        });
        const resMock = createResMock();
        const nextMock = jest.fn();

        reqMock.api.profileGetState.mockResolvedValueOnce({
            body: {
                account: {
                    person: {
                        firstname: 'Qwe',
                        lastname: 'Asd'
                    },
                    display_name: {
                        social: {
                            provider: 'gg'
                        }
                    }
                }
            }
        });

        await profileGetState(reqMock, resMock, nextMock);

        expect(reqMock.api.profileGetState).toBeCalled();
        expect(nextMock).toBeCalled();
        expect(resMock.locals.account).toEqual({
            person: {
                firstname: 'Qwe',
                lastname: 'Asd',
                provider: 'gg'
            },
            display_name: {
                social: {
                    provider: 'gg'
                }
            }
        });
        expect(resMock.locals.store.form).toEqual({
            values: {
                firstname: 'Qwe',
                lastname: 'Asd'
            },
            states: {
                firstname: 'valid',
                lastname: 'valid'
            },
            isEulaShowedInPopup: true
        });
    });
    it('should call PLog methods on error', async () => {
        const reqMock = createReqMock({
            method: 'POST'
        });
        const resMock = createResMock();
        const nextMock = jest.fn();

        reqMock.api.profileGetState.mockRejectedValueOnce({});

        await profileGetState(reqMock, resMock, nextMock);

        expect(reqMock.api.profileGetState).toBeCalled();
        expect(nextMock).toBeCalled();
        expect(plog.warn).toBeCalled();
    });
});
