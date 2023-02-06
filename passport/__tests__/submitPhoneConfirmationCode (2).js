jest.mock('../../api', () => ({
    request: jest.fn()
}));

import api from '../../api';
import {
    updateStates,
    updateValues,
    updateHumanConfirmationStatus,
    updateConfirmationFetchingStatus,
    changePhoneConfirmationType,
    setCallConfirmationTimer
} from '@blocks/actions/form';
import updateFieldStatus from '../methods/updateFieldStatus';
import findFieldsWithErrors from '../methods/findFieldsWithErrors';
import checkIfFieldEmpty from '../methods/checkIfFieldEmpty';

jest.mock('@blocks/actions/form', () => ({
    updateStates: jest.fn(),
    updateValues: jest.fn(),
    updateHumanConfirmationStatus: jest.fn(),
    updateConfirmationFetchingStatus: jest.fn(),
    changePhoneConfirmationType: jest.fn(),
    setCallConfirmationTimer: jest.fn()
}));

jest.mock('../methods/checkIfFieldEmpty');
jest.mock('../methods/findFieldsWithErrors');
jest.mock('../methods/updateFieldStatus');

import submitPhoneConfirmationCode from '../methods/submitPhoneConfirmationCode';

describe('Action: submitPhoneConfirmationCode', () => {
    describe('success cases', () => {
        beforeEach(() => {
            checkIfFieldEmpty.mockImplementation(() => jest.fn());
            findFieldsWithErrors.mockImplementation(() => jest.fn());
            updateFieldStatus.mockImplementation(() => jest.fn());
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'ok'});
                        return this;
                    };

                    this.fail = function() {
                        return this;
                    };

                    this.always = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            checkIfFieldEmpty.mockClear();
            findFieldsWithErrors.mockClear();
            updateFieldStatus.mockClear();
            updateStates.mockClear();
            updateValues.mockClear();
            updateHumanConfirmationStatus.mockClear();
            changePhoneConfirmationType.mockClear();
            updateConfirmationFetchingStatus.mockClear();
            api.request.mockClear();
            setCallConfirmationTimer.mockClear();
        });

        it('should send api request with valid params', () => {
            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const isCallConfirmation = false;
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                common: {
                    track_id: trackId
                },
                form: {
                    isPhoneCallConfirmationAvailable: false,
                    validation: {
                        isValidPhoneForCall: false
                    }
                }
            }));
            const params = {
                track_id: trackId,
                number
            };

            submitPhoneConfirmationCode(number, isCallConfirmation)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(8);
            expect(updateConfirmationFetchingStatus).toBeCalled();
            expect(updateConfirmationFetchingStatus).toBeCalledWith({isFetching: true});
            expect(updateStates).toBeCalled();
            expect(updateStates.mock.calls.length).toBe(3);
            expect(updateStates.mock.calls[0][0]).toEqual({field: 'phoneCode', status: ''});
            expect(updateStates.mock.calls[1][0]).toEqual({field: 'phone', status: ''});
            expect(updateStates.mock.calls[2][0]).toEqual({field: 'phoneCodeStatus', status: 'code_sent'});
            expect(updateValues).toBeCalled();
            expect(updateValues).toBeCalledWith({field: 'phoneCode', value: ''});
            expect(changePhoneConfirmationType).toBeCalled();
            expect(changePhoneConfirmationType).toBeCalledWith('sms');
            expect(findFieldsWithErrors).toBeCalled();
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('phone', 'valid');
            expect(api.request).toBeCalledWith(
                'phone-confirm-code-submit',
                Object.assign({}, params, {confirm_method: 'by_sms', isCodeWithFormat: true})
            );
        });

        it('should send api request with valid params and default call confirmation flag', () => {
            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                common: {
                    track_id: trackId
                },
                form: {
                    isPhoneCallConfirmationAvailable: false,
                    validation: {
                        isValidPhoneForCall: false
                    }
                }
            }));
            const params = {
                track_id: trackId,
                number
            };

            submitPhoneConfirmationCode(number)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(8);
            expect(updateConfirmationFetchingStatus).toBeCalled();
            expect(updateConfirmationFetchingStatus).toBeCalledWith({isFetching: true});
            expect(updateStates).toBeCalled();
            expect(updateStates.mock.calls.length).toBe(3);
            expect(updateStates.mock.calls[0][0]).toEqual({field: 'phoneCode', status: ''});
            expect(updateStates.mock.calls[1][0]).toEqual({field: 'phone', status: ''});
            expect(updateStates.mock.calls[2][0]).toEqual({field: 'phoneCodeStatus', status: 'code_sent'});
            expect(updateValues).toBeCalled();
            expect(updateValues).toBeCalledWith({field: 'phoneCode', value: ''});
            expect(changePhoneConfirmationType).toBeCalled();
            expect(changePhoneConfirmationType).toBeCalledWith('sms');
            expect(findFieldsWithErrors).toBeCalled();
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('phone', 'valid');
            expect(api.request).toBeCalledWith(
                'phone-confirm-code-submit',
                Object.assign({}, params, {confirm_method: 'by_sms', isCodeWithFormat: true})
            );
        });

        it('should skip submit confirmation code for empty phone', () => {
            checkIfFieldEmpty.mockImplementation(() => jest.fn(() => true));

            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const isCallConfirmation = false;
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                common: {
                    track_id: trackId
                },
                form: {
                    isPhoneCallConfirmationAvailable: false,
                    validation: {
                        isValidPhoneForCall: false
                    }
                }
            }));

            submitPhoneConfirmationCode(number, isCallConfirmation)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(2);
            expect(updateConfirmationFetchingStatus).toBeCalled();
            expect(updateConfirmationFetchingStatus.mock.calls.length).toBe(2);
            expect(updateConfirmationFetchingStatus.mock.calls[0][0]).toEqual({isFetching: true});
            expect(updateConfirmationFetchingStatus.mock.calls[1][0]).toEqual({isFetching: false});
        });

        it('should submit confirmation code with phone call confirmation type', () => {
            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const isCallConfirmation = true;
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                common: {
                    track_id: trackId
                },
                form: {
                    isPhoneCallConfirmationAvailable: true,
                    validation: {
                        isValidPhoneForCall: true
                    }
                }
            }));
            const params = {
                track_id: trackId,
                confirm_method: 'by_call',
                number
            };

            submitPhoneConfirmationCode(number, isCallConfirmation)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(9);
            expect(updateConfirmationFetchingStatus).toBeCalled();
            expect(updateConfirmationFetchingStatus).toBeCalledWith({isFetching: true});
            expect(updateStates).toBeCalled();
            expect(updateStates.mock.calls.length).toBe(3);
            expect(updateStates.mock.calls[0][0]).toEqual({field: 'phoneCode', status: ''});
            expect(updateStates.mock.calls[1][0]).toEqual({field: 'phone', status: ''});
            expect(updateStates.mock.calls[2][0]).toEqual({field: 'phoneCodeStatus', status: 'code_sent'});
            expect(updateValues).toBeCalled();
            expect(updateValues).toBeCalledWith({field: 'phoneCode', value: ''});
            expect(changePhoneConfirmationType).toBeCalled();
            expect(changePhoneConfirmationType).toBeCalledWith('call');
            expect(findFieldsWithErrors).toBeCalled();
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('phone', 'valid');
            expect(api.request).toBeCalledWith('phone-confirm-code-submit', params);
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            checkIfFieldEmpty.mockImplementation(() => jest.fn());
            findFieldsWithErrors.mockImplementation(() => jest.fn());
            updateFieldStatus.mockImplementation(() => jest.fn());
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function(fn) {
                        fn({status: 'error'});
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: []});
                        return this;
                    };

                    this.always = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });
        });

        afterEach(() => {
            checkIfFieldEmpty.mockClear();
            findFieldsWithErrors.mockClear();
            updateFieldStatus.mockClear();
            updateStates.mockClear();
            updateValues.mockClear();
            updateHumanConfirmationStatus.mockClear();
            changePhoneConfirmationType.mockClear();
            updateConfirmationFetchingStatus.mockClear();
            api.request.mockClear();
        });

        it('should skip invalid status', () => {
            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const isCallConfirmation = true;
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                common: {
                    track_id: trackId
                },
                form: {
                    isPhoneCallConfirmationAvailable: true,
                    validation: {
                        isValidPhoneForCall: true
                    }
                }
            }));
            const params = {
                track_id: trackId,
                confirm_method: 'by_call',
                number
            };

            submitPhoneConfirmationCode(number, isCallConfirmation)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(5);
            expect(updateConfirmationFetchingStatus).toBeCalled();
            expect(updateConfirmationFetchingStatus).toBeCalledWith({isFetching: true});
            expect(updateStates).toBeCalled();
            expect(updateStates.mock.calls.length).toBe(2);
            expect(updateStates.mock.calls[0][0]).toEqual({field: 'phoneCode', status: ''});
            expect(updateStates.mock.calls[1][0]).toEqual({field: 'phone', status: ''});
            expect(updateValues).toBeCalled();
            expect(updateValues).toBeCalledWith({field: 'phoneCode', value: ''});
            expect(changePhoneConfirmationType).toBeCalled();
            expect(changePhoneConfirmationType).toBeCalledWith('call');
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('phone', 'not_valid');
            expect(api.request).toBeCalledWith('phone-confirm-code-submit', params);
        });

        it('should handle phone.confirmed error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['phone.confirmed']});
                        return this;
                    };

                    this.always = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });

            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const isCallConfirmation = true;
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                common: {
                    track_id: trackId
                },
                form: {
                    isPhoneCallConfirmationAvailable: true,
                    validation: {
                        isValidPhoneForCall: true
                    }
                }
            }));
            const params = {
                track_id: trackId,
                confirm_method: 'by_call',
                number
            };

            submitPhoneConfirmationCode(number, isCallConfirmation)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(5);
            expect(updateConfirmationFetchingStatus).toBeCalled();
            expect(updateConfirmationFetchingStatus).toBeCalledWith({isFetching: true});
            expect(updateStates).toBeCalled();
            expect(updateStates.mock.calls.length).toBe(2);
            expect(updateStates.mock.calls[0][0]).toEqual({field: 'phoneCode', status: ''});
            expect(updateStates.mock.calls[1][0]).toEqual({field: 'phone', status: ''});
            expect(updateValues).toBeCalled();
            expect(updateValues).toBeCalledWith({field: 'phoneCode', value: ''});
            expect(changePhoneConfirmationType).toBeCalled();
            expect(changePhoneConfirmationType).toBeCalledWith('call');
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus.mock.calls.length).toBe(1);
            expect(updateFieldStatus.mock.calls[0][0]).toEqual('phone');
            expect(updateFieldStatus.mock.calls[0][1]).toEqual('not_valid');
            expect(api.request).toBeCalledWith('phone-confirm-code-submit', params);
        });

        it('should handle sms_limit.exceeded error', () => {
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
                        return this;
                    };

                    this.fail = function(fn) {
                        fn({errors: ['sms_limit.exceeded']});
                        return this;
                    };

                    this.always = function() {
                        return this;
                    };
                };

                return new FakeApi();
            });

            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const isCallConfirmation = true;
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                common: {
                    track_id: trackId
                },
                form: {
                    isPhoneCallConfirmationAvailable: true,
                    validation: {
                        isValidPhoneForCall: true
                    }
                }
            }));
            const params = {
                track_id: trackId,
                confirm_method: 'by_call',
                number
            };

            submitPhoneConfirmationCode(number, isCallConfirmation)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
            expect(updateConfirmationFetchingStatus).toBeCalled();
            expect(updateConfirmationFetchingStatus).toBeCalledWith({isFetching: true});
            expect(updateStates).toBeCalled();
            expect(updateStates.mock.calls.length).toBe(3);
            expect(updateStates.mock.calls[0][0]).toEqual({field: 'phoneCode', status: ''});
            expect(updateStates.mock.calls[1][0]).toEqual({field: 'phone', status: ''});
            expect(updateStates.mock.calls[2][0]).toEqual({field: 'phoneCodeStatus', status: ''});
            expect(updateValues).toBeCalled();
            expect(updateValues).toBeCalledWith({field: 'phoneCode', value: ''});
            expect(changePhoneConfirmationType).toBeCalled();
            expect(changePhoneConfirmationType).toBeCalledWith('call');
            expect(updateFieldStatus).toBeCalled();
            expect(updateFieldStatus).toBeCalledWith('phone', 'not_valid');
            expect(api.request).toBeCalledWith('phone-confirm-code-submit', params);
        });
    });

    describe('always cases', () => {
        beforeEach(() => {
            checkIfFieldEmpty.mockImplementation(() => jest.fn());
            findFieldsWithErrors.mockImplementation(() => jest.fn());
            updateFieldStatus.mockImplementation(() => jest.fn());
            api.request.mockImplementation(() => {
                const FakeApi = function() {
                    this.done = function() {
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
            checkIfFieldEmpty.mockClear();
            findFieldsWithErrors.mockClear();
            updateFieldStatus.mockClear();
            updateStates.mockClear();
            updateValues.mockClear();
            updateHumanConfirmationStatus.mockClear();
            changePhoneConfirmationType.mockClear();
            updateConfirmationFetchingStatus.mockClear();
            api.request.mockClear();
        });

        it('should stop fetching process', () => {
            const dispatch = jest.fn();
            const number = '+7 123 456 789';
            const isCallConfirmation = true;
            const trackId = 'track_id';
            const getState = jest.fn(() => ({
                common: {
                    track_id: trackId
                },
                form: {
                    isPhoneCallConfirmationAvailable: true,
                    validation: {
                        isValidPhoneForCall: true
                    }
                }
            }));
            const params = {
                track_id: trackId,
                confirm_method: 'by_call',
                number
            };

            submitPhoneConfirmationCode(number, isCallConfirmation)(dispatch, getState);

            expect(dispatch.mock.calls.length).toBe(6);
            expect(updateConfirmationFetchingStatus).toBeCalled();
            expect(updateConfirmationFetchingStatus.mock.calls.length).toBe(2);
            expect(updateConfirmationFetchingStatus.mock.calls[0][0]).toEqual({isFetching: true});
            expect(updateConfirmationFetchingStatus.mock.calls[1][0]).toEqual({isFetching: false});
            expect(updateStates).toBeCalled();
            expect(updateStates.mock.calls.length).toBe(2);
            expect(updateStates.mock.calls[0][0]).toEqual({field: 'phoneCode', status: ''});
            expect(updateStates.mock.calls[1][0]).toEqual({field: 'phone', status: ''});
            expect(updateValues).toBeCalled();
            expect(updateValues).toBeCalledWith({field: 'phoneCode', value: ''});
            expect(changePhoneConfirmationType).toBeCalled();
            expect(changePhoneConfirmationType).toBeCalledWith('call');
            expect(api.request).toBeCalledWith('phone-confirm-code-submit', params);
        });
    });
});
