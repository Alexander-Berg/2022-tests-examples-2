jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import forgetAccount from '../forgetAccount';
import * as api from '../../../api';
import {domikIsLoading, changeMobileMenuVisibility} from '../';
import showAccounts from '../showAccounts';

jest.mock('../', () => ({
    domikIsLoading: jest.fn(),
    changeMobileMenuVisibility: jest.fn()
}));
jest.mock('../showAccounts');

describe('Actions: forgetAccount', () => {
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
                    csrf: 'csrf'
                }
            }));

            const uid = 'uid';

            forgetAccount(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('accounts/forget', {
                _uid: uid,
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(showAccounts).toBeCalled();
            expect(changeMobileMenuVisibility).not.toBeCalled();
        });

        it('should handle touch for success api request', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                settings: {
                    ua: {
                        isTouch: true
                    }
                },
                common: {
                    csrf: 'csrf'
                }
            }));

            const uid = 'uid';

            forgetAccount(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('accounts/forget', {
                _uid: uid,
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(showAccounts).toBeCalled();
            expect(changeMobileMenuVisibility).toBeCalled();
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
                    csrf: 'csrf'
                }
            }));

            const uid = 'uid';

            forgetAccount(uid)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('accounts/forget', {
                _uid: uid,
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(showAccounts).toBeCalled();
            expect(changeMobileMenuVisibility).not.toBeCalled();
        });
    });
});
