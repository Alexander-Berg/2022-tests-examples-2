jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import authPasswordSubmitForMagic from '../authPasswordSubmitForMagic';
import {updateMagicTokensSuccess, domikIsLoading} from '../';
import showAccounts from '../showAccounts';
import * as api from '../../../api';

jest.mock('../', () => ({
    updateMagicTokensSuccess: jest.fn(),
    domikIsLoading: jest.fn()
}));
jest.mock('../showAccounts');

describe('Actions: authPasswordSubmitForMagic', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'ok', track_id: 'track', csrf_token: 'token'});
                        return this;
                    };

                    this.fail = function() {
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
            updateMagicTokensSuccess.mockClear();
            domikIsLoading.mockClear();
            showAccounts.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    profile_url: '/profile',
                    retpath: 'retpath',
                    fretpath: 'fretpath',
                    clean: 'clean',
                    origin: 'origin'
                }
            }));

            authPasswordSubmitForMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/password/submit', {
                retpath: 'retpath',
                fretpath: 'fretpath',
                clean: 'clean',
                origin: 'origin',
                with_code: 1
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateMagicTokensSuccess).toBeCalled();
            expect(updateMagicTokensSuccess).toBeCalledWith('track', 'token');
        });

        it('should send api request with valid params and fallback retpath to profile url', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    profile_url: '/profile',
                    fretpath: 'fretpath',
                    clean: 'clean',
                    origin: 'origin'
                }
            }));

            authPasswordSubmitForMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/password/submit', {
                retpath: '/profile',
                fretpath: 'fretpath',
                clean: 'clean',
                origin: 'origin',
                with_code: 1
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateMagicTokensSuccess).toBeCalled();
            expect(updateMagicTokensSuccess).toBeCalledWith('track', 'token');
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
                        fn();
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
            updateMagicTokensSuccess.mockClear();
            domikIsLoading.mockClear();
            showAccounts.mockClear();
        });

        it('should handle failed api request', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    profile_url: '/profile',
                    retpath: 'retpath',
                    fretpath: 'fretpath',
                    clean: 'clean',
                    origin: 'origin'
                }
            }));

            authPasswordSubmitForMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/password/submit', {
                retpath: 'retpath',
                fretpath: 'fretpath',
                clean: 'clean',
                origin: 'origin',
                with_code: 1
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateMagicTokensSuccess).not.toBeCalled();
            expect(showAccounts).toBeCalled();
        });
    });
});
