jest.mock('../../../api', () => ({
    request: jest.fn()
}));

import confirmAuthFromLetter from '../confirmAuthFromLetter';
import * as api from '../../../api';
import {setAuthMailConfirmed, setAuthMailError} from '../';

jest.mock('../', () => ({
    setAuthMailConfirmed: jest.fn(),
    setAuthMailError: jest.fn()
}));

describe('Actions: confirmAuthFromLetter', () => {
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
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            setAuthMailConfirmed.mockClear();
            setAuthMailError.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                },
                settings: {
                    language: 'ru'
                },
                mailAuth: {
                    secret: 'secret',
                    mailTrack: 'track'
                },
                auth: {
                    processedAccount: {
                        uid: 'account.uid',
                        primaryAliasType: 5
                    }
                }
            }));

            confirmAuthFromLetter()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/confirm_magic_letter', {
                csrf_token: 'csrf',
                secret: 'secret',
                track_id: 'track',
                language: 'ru'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(1);
            expect(setAuthMailConfirmed).toBeCalled();
            expect(setAuthMailError).not.toBeCalled();
        });

        it('should ignore invalid api response status', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'fail'});
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
                    csrf: 'csrf'
                },
                settings: {
                    language: 'ru'
                },
                mailAuth: {
                    secret: 'secret',
                    mailTrack: 'track'
                },
                auth: {
                    processedAccount: {
                        uid: 'account.uid',
                        primaryAliasType: 5
                    }
                }
            }));

            confirmAuthFromLetter()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/confirm_magic_letter', {
                csrf_token: 'csrf',
                secret: 'secret',
                track_id: 'track',
                language: 'ru'
            });
            expect(dispatch).not.toBeCalled();
            expect(setAuthMailConfirmed).not.toBeCalled();
            expect(setAuthMailError).not.toBeCalled();
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
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            api.request.mockClear();
            setAuthMailConfirmed.mockClear();
            setAuthMailError.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    csrf: 'csrf'
                },
                settings: {
                    language: 'ru'
                },
                mailAuth: {
                    secret: 'secret',
                    mailTrack: 'track'
                },
                auth: {
                    processedAccount: {
                        uid: 'account.uid',
                        primaryAliasType: 5
                    }
                }
            }));

            confirmAuthFromLetter()(dispatch, getState);

            expect(api.request).toBeCalled();
            expect(api.request).toBeCalledWith('auth/confirm_magic_letter', {
                csrf_token: 'csrf',
                secret: 'secret',
                track_id: 'track',
                language: 'ru'
            });
            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(1);
            expect(setAuthMailConfirmed).not.toBeCalled();
            expect(setAuthMailError).toBeCalled();
            expect(setAuthMailError).toBeCalledWith('error.1');
        });
    });
});
