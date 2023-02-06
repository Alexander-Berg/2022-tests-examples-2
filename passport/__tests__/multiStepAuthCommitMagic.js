jest.mock('@blocks/api', () => ({
    request: jest.fn()
}));

import multiStepAuthCommitMagic from '../multiStepAuthCommitMagic';
import * as api from '@blocks/api';
import {domikIsLoading, changeCaptchaState} from '../';
import reloadCaptcha from '@components/Captcha/actions/reloadCaptcha';

jest.mock('../', () => ({
    domikIsLoading: jest.fn(),
    changeCaptchaState: jest.fn()
}));
jest.mock('@components/Captcha/actions/reloadCaptcha');

const mockLocationSetter = jest.fn();

const originalLocation = window.location;

describe('Actions: multiStepAuthCommitMagic', () => {
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

                    this.always = function(fn) {
                        fn();
                        return this;
                    };
                };

                return new FakeApi();
            });

            Object.defineProperty(window, 'location', {
                set: mockLocationSetter
            });
        });

        afterEach(() => {
            api.request.mockClear();
            domikIsLoading.mockClear();
            changeCaptchaState.mockClear();
            reloadCaptcha.mockClear();
            mockLocationSetter.mockClear();
            Object.defineProperty(window, 'location', originalLocation);
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    track_id: 'track',
                    retpath: 'retpath',
                    csrf: 'csrf'
                }
            }));

            multiStepAuthCommitMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_magic', {
                track_id: 'track',
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
            expect(mockLocationSetter).toBeCalledWith('retpath');
        });

        it('should skip success api response with invalid status', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'fail'});
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
                    track_id: 'track',
                    retpath: 'retpath',
                    csrf: 'csrf'
                }
            }));

            multiStepAuthCommitMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_magic', {
                track_id: 'track',
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
            expect(mockLocationSetter).not.toBeCalled();
        });

        it('should fallback retpath param to profile url', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    csrf: 'csrf'
                }
            }));

            multiStepAuthCommitMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_magic', {
                track_id: 'track',
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
            expect(mockLocationSetter).toBeCalledWith('/profile');
        });

        it('should use am finishOkUrl as retpath', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    csrf: 'csrf'
                },
                am: {
                    isAm: true,
                    finishOkUrl: '/amFinishOk'
                }
            }));

            multiStepAuthCommitMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_magic', {
                track_id: 'track',
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(3);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should not use am finishOkUrl when retpath specified', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    track_id: 'track',
                    profile_url: '/profile',
                    csrf: 'csrf',
                    retpath: '/notAmAtAll'
                },
                am: {
                    isAm: true,
                    finishOkUrl: '/amFinishOk'
                }
            }));

            multiStepAuthCommitMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_magic', {
                track_id: 'track',
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(3);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
            expect(mockLocationSetter).toBeCalledWith('/notAmAtAll');
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
            domikIsLoading.mockClear();
            changeCaptchaState.mockClear();
            reloadCaptcha.mockClear();
        });

        it('should skip fail response without captcha errors', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                auth: {
                    isCaptchaRequired: true
                },
                common: {
                    track_id: 'track',
                    retpath: 'retpath',
                    csrf: 'csrf'
                }
            }));

            multiStepAuthCommitMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_magic', {
                track_id: 'track',
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should skip fail response without errors', () => {
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
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                auth: {
                    isCaptchaRequired: true
                },
                common: {
                    track_id: 'track',
                    retpath: 'retpath',
                    csrf: 'csrf'
                }
            }));

            multiStepAuthCommitMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_magic', {
                track_id: 'track',
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(changeCaptchaState).not.toBeCalled();
            expect(reloadCaptcha).not.toBeCalled();
        });

        it('should handle fail response captcha errors', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['captcha.required', 'error.1']});
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
                auth: {
                    isCaptchaRequired: true
                },
                common: {
                    track_id: 'track',
                    retpath: 'retpath',
                    csrf: 'csrf'
                }
            }));

            multiStepAuthCommitMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_magic', {
                track_id: 'track',
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(changeCaptchaState).toBeCalled();
            expect(changeCaptchaState).toBeCalledWith(true);
            expect(reloadCaptcha).toBeCalled();
        });

        it('should handle fail response captcha errors and dont reload captcha', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['captcha.required', 'error.1']});
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
                auth: {
                    isCaptchaRequired: false
                },
                common: {
                    track_id: 'track',
                    retpath: 'retpath',
                    csrf: 'csrf'
                }
            }));

            multiStepAuthCommitMagic()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/multi_step/commit_magic', {
                track_id: 'track',
                csrf_token: 'csrf'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading.mock.calls.length).toBe(2);
            expect(domikIsLoading.mock.calls[0][0]).toBe(true);
            expect(domikIsLoading.mock.calls[1][0]).toBe(false);
            expect(changeCaptchaState).toBeCalled();
            expect(changeCaptchaState).toBeCalledWith(true);
            expect(reloadCaptcha).not.toBeCalled();
        });
    });
});
