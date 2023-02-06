import {authPrepareWithCred} from '../authPrepareWithCred';
import * as api from '@blocks/api';
import {authPrepareWithCredSuccess, authPrepareWithCredFail, startLoadingPrepareWithCred, showSuccessScreen} from '../';

jest.mock('@blocks/api', () => ({
    request: jest.fn()
}));

jest.mock('../', () => ({
    authPrepareWithCredSuccess: jest.fn(),
    authPrepareWithCredFail: jest.fn(),
    startLoadingPrepareWithCred: jest.fn(),
    showSuccessScreen: jest.fn()
}));

const {location} = window;

describe('Actions: authPrepareWithCred', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'ok'});
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });

            delete window.location;
            window.location = {};
        });

        afterEach(() => {
            api.request.mockClear();
            authPrepareWithCredSuccess.mockClear();
            authPrepareWithCredFail.mockClear();
            startLoadingPrepareWithCred.mockClear();
            showSuccessScreen.mockClear();
            window.location = location;
        });

        it('should send api request with valid params when is AM', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                am: {
                    isAm: true,
                    finishOkUrl: 'finish',
                    trackId: 'track'
                }
            }));

            authPrepareWithCred()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth-prepare-with-cred', {
                trackId: 'track'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(startLoadingPrepareWithCred).toBeCalled();
            expect(authPrepareWithCredSuccess).toBeCalled();
            expect(window.location).toEqual('finish');
        });

        it('should send api request with valid params when not AM', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                am: {
                    isAm: false,
                    finishOkUrl: undefined,
                    trackId: 'track'
                }
            }));

            authPrepareWithCred()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth-prepare-with-cred', {
                trackId: 'track'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(startLoadingPrepareWithCred).toBeCalled();
            expect(authPrepareWithCredSuccess).toBeCalled();
            expect(showSuccessScreen).toBeCalled();
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['error.1', 'error.2']});
                        return this;
                    };

                    this.always = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            authPrepareWithCredSuccess.mockClear();
            authPrepareWithCredFail.mockClear();
            startLoadingPrepareWithCred.mockClear();
            showSuccessScreen.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                am: {
                    isAm: true,
                    finishOkUrl: 'finish',
                    trackId: 'track'
                }
            }));

            authPrepareWithCred()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth-prepare-with-cred', {
                trackId: 'track'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(startLoadingPrepareWithCred).toBeCalled();
            expect(authPrepareWithCredFail).toBeCalled();
            expect(authPrepareWithCredFail).toBeCalledWith(
                expect.objectContaining({
                    errors: ['error.1', 'error.2']
                })
            );
        });
    });
});
