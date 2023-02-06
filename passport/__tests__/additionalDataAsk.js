import {push} from 'connected-react-router';

jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import * as api from '../../../api';
import {updateCSRF} from '../../../common/actions';
// eslint-disable-next-line no-duplicate-imports
import * as router from 'connected-react-router';
import redirectToRetpath from '../redirectToRetpath';
import showAccounts from '../showAccounts';
import {initAdditionalDataRequest, setupBackPane} from '../';
import additionalDataAsk from '../additionalDataAsk';

jest.mock('../../../common/actions', () => ({
    updateCSRF: jest.fn()
}));
jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../redirectToRetpath');
jest.mock('../showAccounts');
jest.mock('../', () => ({
    initAdditionalDataRequest: jest.fn(),
    setupBackPane: jest.fn()
}));

describe('Actions: additionalDataAsk', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockImplementation((method) => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        let fnResult = {};

                        if (method === 'auth/accounts') {
                            fnResult = {
                                csrf: 'csrf',
                                accounts: {
                                    defaultAccount: {
                                        uid: 'defaultAccount.uid'
                                    }
                                }
                            };
                        } else if (method === 'auth/additional_data/ask_v2') {
                            fnResult = {state: ''};
                        }

                        fn(fnResult);
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            updateCSRF.mockClear();
            router.push.mockClear();
            redirectToRetpath.mockClear();
            showAccounts.mockClear();
            initAdditionalDataRequest.mockClear();
            setupBackPane.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    askEmailUrl: 'askEmailUrl',
                    askPhoneUrl: 'askPhoneUrl'
                }
            }));

            additionalDataAsk()(dispatch, getState);

            expect(api.request.mock.calls.length).toBe(2);
            expect(api.request.mock.calls[1][1]).toEqual({
                csrf_token: 'csrf',
                uid: 'defaultAccount.uid'
            });
            expect(dispatch.mock.calls.length).toBe(4);
            expect(updateCSRF).toBeCalledWith('csrf');
            expect(initAdditionalDataRequest).toBeCalledWith({state: ''});
            expect(setupBackPane).toBeCalledWith(null);
            expect(redirectToRetpath).toBeCalled();
        });

        it('should handle phone state and redirect to phone request page', () => {
            api.request.mockImplementation((method) => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        let fnResult = {};

                        if (method === 'auth/accounts') {
                            fnResult = {
                                csrf: 'csrf',
                                accounts: {
                                    defaultAccount: {
                                        uid: 'defaultAccount.uid'
                                    }
                                }
                            };
                        } else if (method === 'auth/additional_data/ask_v2') {
                            fnResult = {state: 'phone'};
                        }

                        fn(fnResult);
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });

            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    askEmailUrl: 'askEmailUrl',
                    askPhoneUrl: 'askPhoneUrl'
                }
            }));

            additionalDataAsk()(dispatch, getState);

            expect(api.request.mock.calls.length).toBe(2);
            expect(api.request.mock.calls[1][1]).toEqual({
                csrf_token: 'csrf',
                uid: 'defaultAccount.uid'
            });
            expect(dispatch.mock.calls.length).toBe(5);
            expect(updateCSRF).toBeCalledWith('csrf');
            expect(initAdditionalDataRequest).toBeCalledWith({state: 'phone'});
            expect(setupBackPane).toBeCalledWith(null);
            expect(showAccounts).toBeCalled();
            expect(push).toBeCalledWith('askPhoneUrl');
            expect(redirectToRetpath).not.toBeCalled();
        });

        it('should handle phone state and redirect to email request page', () => {
            api.request.mockImplementation((method) => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        let fnResult = {};

                        if (method === 'auth/accounts') {
                            fnResult = {
                                csrf: 'csrf',
                                accounts: {
                                    defaultAccount: {
                                        uid: 'defaultAccount.uid'
                                    }
                                }
                            };
                        } else if (method === 'auth/additional_data/ask_v2') {
                            fnResult = {state: 'email'};
                        }

                        fn(fnResult);
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });

            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    askEmailUrl: 'askEmailUrl',
                    askPhoneUrl: 'askPhoneUrl'
                }
            }));

            additionalDataAsk()(dispatch, getState);

            expect(api.request.mock.calls.length).toBe(2);
            expect(api.request.mock.calls[1][1]).toEqual({
                csrf_token: 'csrf',
                uid: 'defaultAccount.uid'
            });
            expect(dispatch.mock.calls.length).toBe(5);
            expect(updateCSRF).toBeCalledWith('csrf');
            expect(initAdditionalDataRequest).toBeCalledWith({state: 'email'});
            expect(setupBackPane).toBeCalledWith(null);
            expect(showAccounts).toBeCalled();
            expect(push).toBeCalledWith('askEmailUrl');
            expect(redirectToRetpath).not.toBeCalled();
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
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            updateCSRF.mockClear();
            router.push.mockClear();
            redirectToRetpath.mockClear();
            showAccounts.mockClear();
            initAdditionalDataRequest.mockClear();
            setupBackPane.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    askEmailUrl: 'askEmailUrl',
                    askPhoneUrl: 'askPhoneUrl'
                }
            }));

            additionalDataAsk()(dispatch, getState);

            expect(api.request.mock.calls.length).toBe(1);
            expect(dispatch.mock.calls.length).toBe(1);
            expect(updateCSRF).not.toBeCalled();
            expect(initAdditionalDataRequest).not.toBeCalled();
            expect(setupBackPane).not.toBeCalled();
            expect(redirectToRetpath).toBeCalled();
        });

        it('should send api request with valid params', () => {
            api.request.mockImplementation((method) => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        if (method === 'auth/accounts') {
                            fn({
                                csrf: 'csrf',
                                accounts: {
                                    defaultAccount: {
                                        uid: 'defaultAccount.uid'
                                    }
                                }
                            });
                        }

                        return this;
                    };

                    this.fail = function(fn) {
                        fn();

                        return this;
                    };
                };

                return new FakeApi();
            });

            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    askEmailUrl: 'askEmailUrl',
                    askPhoneUrl: 'askPhoneUrl'
                }
            }));

            additionalDataAsk()(dispatch, getState);

            expect(api.request.mock.calls.length).toBe(2);
            expect(api.request.mock.calls[1][1]).toEqual({
                csrf_token: 'csrf',
                uid: 'defaultAccount.uid'
            });
            expect(dispatch.mock.calls.length).toBe(3);
            expect(updateCSRF).toBeCalledWith('csrf');
            expect(initAdditionalDataRequest).not.toBeCalled();
            expect(setupBackPane).not.toBeCalled();
            expect(redirectToRetpath).toBeCalled();
        });
    });
});
