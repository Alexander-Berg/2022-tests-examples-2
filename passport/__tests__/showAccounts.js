jest.mock('../../../api', () => ({
    request: jest.fn(),
    setCsrfToken: jest.fn()
}));

import showAccounts from '../showAccounts';
import * as router from 'connected-react-router';
import * as api from '../../../api';
import {updateCSRF} from '../../../common/actions';
import {domikIsLoading, showAccountsSuccess, showAccountsFail} from '../';

jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../../../common/actions', () => ({
    updateCSRF: jest.fn()
}));
jest.mock('../', () => ({
    domikIsLoading: jest.fn(),
    showAccountsSuccess: jest.fn(),
    showAccountsFail: jest.fn()
}));

describe('Actions: showAccounts', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({
                            accounts: {
                                unitedAccounts: []
                            },
                            csrf: 'csrf'
                        });
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
            updateCSRF.mockClear();
            domikIsLoading.mockClear();
            showAccountsSuccess.mockClear();
            showAccountsFail.mockClear();
            router.push.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    addUserUrl: 'addUserUrl',
                    origin: 'origin'
                },
                auth: {
                    mode: 'magic'
                }
            }));

            showAccounts(true)(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/accounts', {origin: 'origin'});
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(1);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(updateCSRF).toBeCalled();
            expect(updateCSRF).toBeCalledWith('csrf');
            expect(showAccountsSuccess).toBeCalled();
            expect(showAccountsSuccess).toBeCalledWith({unitedAccounts: []});
            expect(router.push).not.toBeCalled();
            expect(showAccountsFail).not.toBeCalled();
        });

        it('should send api request with fallback without redirect arg', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    addUserUrl: 'addUserUrl',
                    origin: 'origin'
                },
                auth: {
                    mode: 'edit'
                }
            }));

            showAccounts()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/accounts', {origin: 'origin'});
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(5);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateCSRF).toBeCalled();
            expect(updateCSRF).toBeCalledWith('csrf');
            expect(showAccountsSuccess).toBeCalled();
            expect(showAccountsSuccess).toBeCalledWith({unitedAccounts: []});
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('addUserUrl');
            expect(showAccountsFail).not.toBeCalled();
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
            updateCSRF.mockClear();
            domikIsLoading.mockClear();
            showAccountsSuccess.mockClear();
            showAccountsFail.mockClear();
            router.push.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    addUserUrl: 'addUserUrl',
                    origin: 'origin'
                },
                auth: {
                    mode: 'edit'
                }
            }));

            showAccounts()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/accounts', {origin: 'origin'});
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(updateCSRF).not.toBeCalled();
            expect(showAccountsSuccess).not.toBeCalled();
            expect(router.push).not.toBeCalled();
            expect(showAccountsFail).toBeCalled();
            expect(showAccountsFail).toBeCalledWith(['error.1', 'error.2']);
        });
    });
});
