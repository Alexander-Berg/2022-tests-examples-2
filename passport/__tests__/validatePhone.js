import api from '../../../../api';
jest.mock('../../../../api');

import {changePhoneValidationStatus, switchConfirmationMethod} from '../';

jest.mock('../', () => ({
    changePhoneValidationStatus: jest.fn(),
    switchConfirmationMethod: jest.fn()
}));

import {checkPhone} from '../checkPhone';

describe('Actions: validatePhone', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            changePhoneValidationStatus.mockClear();
            switchConfirmationMethod.mockClear();
            checkPhone.check = jest.fn();
        });

        it('should send request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone'
                },
                common: {
                    track_id: 'trackId',
                    csrf: 'csrf'
                }
            }));

            api.__mockSuccess({status: 'ok'});

            checkPhone.validate()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(switchConfirmationMethod).toBeCalledWith('by_sms');
            expect(changePhoneValidationStatus).toBeCalledWith(false);
            expect(api.request).toBeCalledWith('auth/validate_phone', {
                phone_number: 'phone',
                validate_for_call: true,
                check_speech: true,
                track_id: 'trackId',
                csrf_token: 'csrf'
            });
        });

        it('should handle valid phone response', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone'
                },
                common: {
                    track_id: 'trackId',
                    csrf: 'csrf'
                }
            }));

            api.__mockSuccess({status: 'ok', valid_for_call: true});

            checkPhone.validate()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(changePhoneValidationStatus).toBeCalledWith(true);
            expect(api.request).toBeCalledWith('auth/validate_phone', {
                phone_number: 'phone',
                validate_for_call: true,
                check_speech: true,
                track_id: 'trackId',
                csrf_token: 'csrf'
            });
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            changePhoneValidationStatus.mockClear();
            switchConfirmationMethod.mockClear();
            checkPhone.check = jest.fn();
        });

        it('should send request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone'
                },
                common: {
                    track_id: 'trackId',
                    csrf: 'csrf'
                }
            }));

            api.__mockFail({status: 'error'});

            checkPhone.validate()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(switchConfirmationMethod).toBeCalledWith('by_sms');
            expect(changePhoneValidationStatus).toBeCalledWith(false);
            expect(api.request).toBeCalledWith('auth/validate_phone', {
                phone_number: 'phone',
                validate_for_call: true,
                check_speech: true,
                track_id: 'trackId',
                csrf_token: 'csrf'
            });
        });
    });

    describe('always cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            changePhoneValidationStatus.mockClear();
            switchConfirmationMethod.mockClear();
            checkPhone.check = jest.fn();
        });

        it('should send request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone'
                },
                common: {
                    track_id: 'trackId',
                    csrf: 'csrf'
                }
            }));

            api.__mockAlways({status: 'error'});

            checkPhone.validate()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(1);
            expect(checkPhone.check).toBeCalled();
            expect(api.request).toBeCalledWith('auth/validate_phone', {
                phone_number: 'phone',
                validate_for_call: true,
                check_speech: true,
                track_id: 'trackId',
                csrf_token: 'csrf'
            });
        });
    });
});
