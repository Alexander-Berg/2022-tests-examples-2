jest.mock('../../api', () => ({
    request: jest.fn()
}));
import api from '../../api';

import {validatePhoneForCall} from '@blocks/actions/form';

jest.mock('@blocks/actions/form', () => ({
    validatePhoneForCall: jest.fn()
}));

import validatePhoneNumber from '../methods/validatePhoneNumber';

describe('Action: validatePhoneNumber', () => {
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
            validatePhoneForCall.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                settings: {
                    country: 'ru'
                },
                common: {
                    track_id: trackId
                }
            }));
            const params = {
                country: 'ru',
                phone_number: number,
                validate_for_call: true,
                track_id: trackId,
                check_speech: true
            };

            validatePhoneNumber(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(1);
            expect(validatePhoneForCall).toBeCalled();
            expect(validatePhoneForCall).toBeCalledWith(false);
            expect(api.request).toBeCalledWith('validate-phone', params);
        });

        it('should send api request with valid params and valid phone', () => {
            api.request.mockClear();
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'ok', valid_for_call: true});
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });

            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                settings: {
                    country: 'ru'
                },
                common: {
                    track_id: trackId
                }
            }));
            const params = {
                country: 'ru',
                phone_number: number,
                validate_for_call: true,
                track_id: trackId,
                check_speech: true
            };

            validatePhoneNumber(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(1);
            expect(validatePhoneForCall).toBeCalled();
            expect(validatePhoneForCall).toBeCalledWith(true);
            expect(api.request).toBeCalledWith('validate-phone', params);
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
            validatePhoneForCall.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                settings: {
                    country: 'ru'
                },
                common: {
                    track_id: trackId
                }
            }));
            const params = {
                country: 'ru',
                phone_number: number,
                validate_for_call: true,
                track_id: trackId,
                check_speech: true
            };

            validatePhoneNumber(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(1);
            expect(validatePhoneForCall).toBeCalled();
            expect(validatePhoneForCall).toBeCalledWith(false);
            expect(api.request).toBeCalledWith('validate-phone', params);
        });
    });
});
