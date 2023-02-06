jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import loginSuggestedAccount from '../loginSuggestedAccount';
import * as api from '../../../api';
import {
    inputLoginSuccess,
    loginSuggestedAccountSuccess,
    changeProcessedAccount,
    updateLoginValue,
    domikIsLoading
} from '../';
import multiStepAuthStart from '../multiStepAuthStart';
import switchToModeWelcome from '../switchToModeWelcome';

jest.mock('../', () => ({
    inputLoginSuccess: jest.fn(),
    loginSuggestedAccountSuccess: jest.fn(),
    changeProcessedAccount: jest.fn(),
    updateLoginValue: jest.fn(),
    domikIsLoading: jest.fn()
}));
jest.mock('../multiStepAuthStart');
jest.mock('../switchToModeWelcome');

describe('Actions: loginSuggestedAccount', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({input_login: 'login'});
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
            changeProcessedAccount.mockClear();
            updateLoginValue.mockClear();
            multiStepAuthStart.mockClear();
            switchToModeWelcome.mockClear();
            domikIsLoading.mockClear();
            loginSuggestedAccountSuccess.mockClear();
            inputLoginSuccess.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                }
            }));

            const account = {
                uid: 'uid',
                status: 'VALID'
            };

            loginSuggestedAccount(account)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('accounts/input-login', {
                _uid: account.uid,
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(5);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(inputLoginSuccess).toBeCalled();
            expect(inputLoginSuccess).toBeCalledWith({uid: 'login'});
            expect(loginSuggestedAccountSuccess).toBeCalled();
            expect(loginSuggestedAccountSuccess).toBeCalledWith(account);
            expect(multiStepAuthStart).toBeCalled();
            expect(multiStepAuthStart).toBeCalledWith({login: account.login});
        });

        it('should handle account with invalid status', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                }
            }));

            const account = {
                uid: 'uid',
                status: 'INVALID'
            };

            loginSuggestedAccount(account)(dispatch, getState);

            expect(api.request).not.toBeCalled();
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(1);
            expect(domikIsLoading.mock.calls[0][0]).toBe(false);
            expect(inputLoginSuccess).not.toBeCalled();
            expect(loginSuggestedAccountSuccess).toBeCalled();
            expect(loginSuggestedAccountSuccess).toBeCalledWith(account);
            expect(multiStepAuthStart).toBeCalled();
            expect(multiStepAuthStart).toBeCalledWith({login: account.login});
        });

        it('should handle api response without login', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                }
            }));

            const account = {
                uid: 'uid',
                status: 'VALID'
            };

            loginSuggestedAccount(account)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('accounts/input-login', {
                _uid: account.uid,
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(inputLoginSuccess).not.toBeCalled();
            expect(loginSuggestedAccountSuccess).toBeCalled();
            expect(loginSuggestedAccountSuccess).toBeCalledWith(account);
            expect(multiStepAuthStart).toBeCalled();
            expect(multiStepAuthStart).toBeCalledWith({login: account.login});
        });

        it('should account with preferred social auth method', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                }
            }));

            const account = {
                uid: 'uid',
                status: 'VALID',
                preferred_auth_method: 'social_vk',
                allowed_auth_methods: ['social_vk']
            };

            loginSuggestedAccount(account)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('accounts/input-login', {
                _uid: account.uid,
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(7);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(inputLoginSuccess).toBeCalled();
            expect(inputLoginSuccess).toBeCalledWith({uid: 'login'});
            expect(loginSuggestedAccountSuccess).toBeCalled();
            expect(loginSuggestedAccountSuccess).toBeCalledWith(account);
            expect(multiStepAuthStart).not.toBeCalled();
            expect(changeProcessedAccount).toBeCalled();
            expect(changeProcessedAccount).toBeCalledWith(account);
            expect(updateLoginValue).toBeCalled();
            expect(updateLoginValue).toBeCalledWith(account.login);
            expect(switchToModeWelcome).toBeCalled();
        });
    });
});
