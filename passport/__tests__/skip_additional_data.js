jest.mock('../../../../api', () => ({
    request: jest.fn()
}));

import api from '../../../../api';
import {domikIsLoading, redirectToRetpath} from '../../../actions';
import {clearErrors} from '../';
import skipAdditionalData from '../skip_additional_data';

jest.mock('../../../actions', () => ({
    redirectToRetpath: jest.fn(),
    domikIsLoading: jest.fn()
}));
jest.mock('../', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn()
}));

describe('Action: skipAdditionalData', () => {
    describe('success cases', () => {
        beforeEach(() => {
            redirectToRetpath.mockImplementation(() => () => {});
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function(fn) {
                        fn({status: 'ok'});
                        return this;
                    };

                    this.catch = function() {
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
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                track_id: '1234',
                csrf_token: 'token',
                user_declined: 'yes'
            };

            skipAdditionalData()(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('auth/additional_data/freeze', params);
        });

        it('should send api request with default account uid', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                track_id: '1234',
                csrf_token: 'token',
                user_declined: 'yes'
            };

            skipAdditionalData()(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('auth/additional_data/freeze', params);
        });

        it('should send api request with empty uid', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                track_id: '1234',
                csrf_token: 'token',
                user_declined: 'yes'
            };

            skipAdditionalData()(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('auth/additional_data/freeze', params);
        });

        it('should send api request with user declined falsy param', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                common: {
                    csrf: 'token'
                }
            }));
            const params = {
                track_id: '1234',
                csrf_token: 'token',
                user_declined: 'no'
            };

            skipAdditionalData('no')(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);
            expect(clearErrors).toBeCalled();
            expect(api.request).toBeCalledWith('auth/additional_data/freeze', params);
        });

        it('should redirect to retpath', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));

            skipAdditionalData()(dispatch, getState);

            expect(redirectToRetpath).toBeCalled();
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            redirectToRetpath.mockImplementation(() => () => {});
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.then = function(fn) {
                        fn({status: 'error'});
                        return this;
                    };

                    this.catch = function(fn) {
                        fn({status: 'error'});
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            redirectToRetpath.mockClear();
        });

        it('should redirect to retpath', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                additionalDataRequest: {
                    track_id: '1234'
                },
                one_domik: {},
                common: {
                    csrf: 'token'
                }
            }));

            skipAdditionalData()(dispatch, getState);

            expect(redirectToRetpath).toBeCalled();
        });
    });
});
