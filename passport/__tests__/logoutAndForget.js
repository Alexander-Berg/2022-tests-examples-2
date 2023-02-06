jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import logoutAndForget from '../logoutAndForget';
import * as api from '../../../api';
import {domikIsLoading, changeMobileMenuVisibility} from '../';
import showAccounts from '../showAccounts';

jest.mock('../', () => ({
    domikIsLoading: jest.fn(),
    changeMobileMenuVisibility: jest.fn()
}));
jest.mock('../showAccounts');

describe('Actions: logoutAndForget', () => {
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
            domikIsLoading.mockClear();
            changeMobileMenuVisibility.mockClear();
            showAccounts.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                settings: {},
                common: {
                    csrf: 'csrf',
                    yu: 'yu',
                    retpath: 'retpath'
                }
            }));
            const uid = 'uid';

            logoutAndForget(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/logout_and_forget', {
                csrf_token: 'csrf',
                retpath: 'retpath',
                uid,
                yu: 'yu'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(showAccounts).toBeCalled();
            expect(changeMobileMenuVisibility).not.toBeCalled();
        });

        it('should handle touch for success api response', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                settings: {
                    ua: {
                        isTouch: true
                    }
                },
                common: {
                    csrf: 'csrf',
                    yu: 'yu',
                    retpath: 'retpath'
                }
            }));
            const uid = 'uid';

            logoutAndForget(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/logout_and_forget', {
                csrf_token: 'csrf',
                retpath: 'retpath',
                uid,
                yu: 'yu'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(showAccounts).toBeCalled();
            expect(changeMobileMenuVisibility).toBeCalled();
            expect(changeMobileMenuVisibility).toBeCalledWith(false);
        });

        it('should fallback for retpath param to profile url', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                settings: {},
                common: {
                    csrf: 'csrf',
                    yu: 'yu',
                    profile_url: '/profile'
                }
            }));
            const uid = 'uid';

            logoutAndForget(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/logout_and_forget', {
                csrf_token: 'csrf',
                retpath: '/profile',
                uid,
                yu: 'yu'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(showAccounts).toBeCalled();
            expect(changeMobileMenuVisibility).not.toBeCalled();
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
            domikIsLoading.mockClear();
            changeMobileMenuVisibility.mockClear();
            showAccounts.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                settings: {},
                common: {
                    csrf: 'csrf',
                    yu: 'yu',
                    retpath: 'retpath'
                }
            }));
            const uid = 'uid';

            logoutAndForget(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/logout_and_forget', {
                csrf_token: 'csrf',
                retpath: 'retpath',
                uid,
                yu: 'yu'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(showAccounts).toBeCalled();
            expect(changeMobileMenuVisibility).not.toBeCalled();
        });
    });
});
