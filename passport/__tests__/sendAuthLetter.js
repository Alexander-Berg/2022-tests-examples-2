jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import sendAuthLetter from '../sendAuthLetter';
import * as api from '../../../api';
import {
    setAuthMailSent,
    setAuthMailError,
    changePagePopupVisibility,
    changePagePopupType,
    domikIsLoading,
    setAuthMailCancelled,
    updateAuthMailStatus
} from '../';

jest.mock('../', () => ({
    setAuthMailSent: jest.fn(),
    setAuthMailError: jest.fn(),
    setAuthMailCancelled: jest.fn(),
    changePagePopupVisibility: jest.fn(),
    changePagePopupType: jest.fn(),
    domikIsLoading: jest.fn(),
    updateAuthMailStatus: jest.fn()
}));

describe('Actions: sendAuthLetter', () => {
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
            setAuthMailSent.mockClear();
            setAuthMailError.mockClear();
            changePagePopupVisibility.mockClear();
            changePagePopupType.mockClear();
            domikIsLoading.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    track_id: 'track'
                },
                settings: {
                    language: 'ru'
                }
            }));

            sendAuthLetter()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/send_magic_letter', {
                csrf_token: 'csrf',
                language: 'ru',
                track_id: 'track'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setAuthMailError).toBeCalled();
            expect(setAuthMailError).toBeCalledWith('global');
        });

        it('should handle fallback track param to mail track id', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    track_id: 'track'
                },
                settings: {
                    language: 'ru'
                }
            }));

            sendAuthLetter()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/send_magic_letter', {
                csrf_token: 'csrf',
                language: 'ru',
                track_id: 'track'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setAuthMailError).toBeCalled();
            expect(setAuthMailError).toBeCalledWith('global');
        });

        it('should handle fallback track param to mail track id', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'ok', code: ['1', '2', '3']});
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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    track_id: 'track'
                },
                settings: {
                    language: 'ru'
                }
            }));

            sendAuthLetter()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/send_magic_letter', {
                csrf_token: 'csrf',
                language: 'ru',
                track_id: 'track'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(7);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setAuthMailError).not.toBeCalled();
            expect(setAuthMailSent).toBeCalled();
            expect(setAuthMailSent).toBeCalledWith(['1', '2', '3']);
            expect(changePagePopupVisibility).toBeCalledWith(true);
            expect(changePagePopupType).toBeCalledWith('authLetter');
            expect(setAuthMailCancelled).toBeCalledWith(false);
            expect(updateAuthMailStatus).toBeCalledWith(false);
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
            setAuthMailSent.mockClear();
            setAuthMailError.mockClear();
            changePagePopupVisibility.mockClear();
            changePagePopupType.mockClear();
            domikIsLoading.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf',
                    track_id: 'track'
                },
                settings: {
                    language: 'ru'
                }
            }));

            sendAuthLetter()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/send_magic_letter', {
                csrf_token: 'csrf',
                language: 'ru',
                track_id: 'track'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setAuthMailError).toBeCalled();
            expect(setAuthMailError).toBeCalledWith('error.1');
        });

        it('handle failed request without errors', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({});
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
                    csrf: 'csrf',
                    track_id: 'track'
                },
                settings: {
                    language: 'ru'
                }
            }));

            sendAuthLetter()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/send_magic_letter', {
                csrf_token: 'csrf',
                language: 'ru',
                track_id: 'track'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(setAuthMailError).toBeCalled();
            expect(setAuthMailError).toBeCalledWith('global');
        });
    });
});
