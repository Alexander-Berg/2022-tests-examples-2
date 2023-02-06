jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import changeActiveAccount from '../changeActiveAccount';
import * as api from '../../../api';
import {domikIsLoading} from '../';
import redirectToRetpath from '../redirectToRetpath';
import showAccounts from '../showAccounts';

jest.mock('../', () => ({
    domikIsLoading: jest.fn()
}));
jest.mock('../redirectToRetpath');
jest.mock('../showAccounts');

describe('Actions: changeActiveAccount', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn();
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
            redirectToRetpath.mockClear();
            domikIsLoading.mockClear();
            showAccounts.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    yu: 'yu',
                    retpath: 'retpath'
                }
            }));

            const uid = 'uid';

            changeActiveAccount(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/change_default', {
                csrf_token: 'csrf',
                retpath: 'retpath',
                uid,
                yu: 'yu'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(1);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(showAccounts).toBeCalled();
            expect(redirectToRetpath).toBeCalled();
        });

        it('should send api request with valid params and fallback retpath param to profile url', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    yu: 'yu',
                    profile_url: '/profile'
                }
            }));

            const uid = 'uid';

            changeActiveAccount(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/change_default', {
                csrf_token: 'csrf',
                retpath: '/profile',
                uid,
                yu: 'yu'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(1);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(showAccounts).toBeCalled();
            expect(redirectToRetpath).toBeCalled();
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
            redirectToRetpath.mockClear();
            domikIsLoading.mockClear();
            showAccounts.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    yu: 'yu',
                    retpath: 'retpath'
                }
            }));

            const uid = 'uid';

            changeActiveAccount(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/change_default', {
                csrf_token: 'csrf',
                retpath: 'retpath',
                uid,
                yu: 'yu'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(showAccounts).toBeCalled();
            expect(redirectToRetpath).not.toBeCalled();
        });
    });
});
