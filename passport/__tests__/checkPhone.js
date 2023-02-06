import api from '../../../../api';
jest.mock('../../../../api');

import {changePagePopupType, changePagePopupVisibility, domikIsLoading, changeCaptchaState} from '../../';
import {changeCheckPhoneStatus, setErrors, clearErrors, setSuggestedAccounts, switchConfirmationMethod} from '../';
import switchToModeRestoreLoginResult from '../../switchToModeRestoreLoginResult';
import metrics from '../../../../metrics';
import {
    RESTORE_LOGIN_ENTER_PHONE_SUCCESS,
    RESTORE_LOGIN_ENTER_PHONE_FAIL,
    RESTORE_LOGIN_ENTER_CAPTCHA_FAIL,
    RESTORE_LOGIN_PAGE
} from '../../../metrics_constants';

import {checkPhone} from '../checkPhone';
import {handleCheckPhoneErrors} from '../handleErrors';

jest.mock('../../', () => ({
    changePagePopupType: jest.fn(),
    changePagePopupVisibility: jest.fn(),
    domikIsLoading: jest.fn(),
    changeCaptchaState: jest.fn()
}));

jest.mock('../', () => ({
    changeCheckPhoneStatus: jest.fn(),
    setErrors: jest.fn(),
    clearErrors: jest.fn(),
    setSuggestedAccounts: jest.fn(),
    switchConfirmationMethod: jest.fn()
}));

jest.mock('../../../../metrics', () => ({
    send: jest.fn()
}));

jest.mock('../../switchToModeRestoreLoginResult');

jest.mock('../handleErrors', () => ({
    handleCheckPhoneErrors: jest.fn()
}));

describe('Actions: checkPhone', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            changePagePopupType.mockClear();
            changePagePopupVisibility.mockClear();
            domikIsLoading.mockClear();
            changeCaptchaState.mockClear();
            changeCheckPhoneStatus.mockClear();
            setErrors.mockClear();
            clearErrors.mockClear();
            setSuggestedAccounts.mockClear();
            switchToModeRestoreLoginResult.mockClear();
            switchConfirmationMethod.mockClear();
            checkPhone.validate = jest.fn();
        });

        it('should send request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone',
                    confirmMethod: 'by_sms',
                    isValidPhone: true,
                    errors: {}
                },
                common: {
                    track_id: 'trackId'
                },
                settings: {
                    language: 'lang'
                }
            }));

            api.__mockSuccess({status: 'ok'});

            checkPhone.check()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(5);
            expect(clearErrors).toBeCalled();
            expect(changeCheckPhoneStatus).toBeCalledWith(true);
            expect(changePagePopupType).toBeCalledWith('restoreLoginEnterConfirmationCode');
            expect(changePagePopupVisibility).toBeCalledWith(true);
            expect(metrics.send).toBeCalledWith([RESTORE_LOGIN_PAGE, RESTORE_LOGIN_ENTER_PHONE_SUCCESS]);

            expect(api.request).toBeCalledWith('auth/restore_login/check_phone', {
                phone_number: 'phone',
                track_id: 'trackId',
                display_language: 'lang',
                confirm_method: 'by_sms'
            });
        });

        it('should send request with confirm method = call and valid phone', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone',
                    confirmMethod: 'by_call',
                    isValidPhone: true,
                    errors: {}
                },
                common: {
                    track_id: 'trackId'
                },
                settings: {
                    language: 'lang'
                }
            }));

            api.__mockSuccess({status: 'ok'});

            checkPhone.check()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(5);
            expect(clearErrors).toBeCalled();
            expect(checkPhone.validate).not.toBeCalled();
            expect(changeCheckPhoneStatus).toBeCalledWith(true);
            expect(changePagePopupType).toBeCalledWith('restoreLoginEnterConfirmationCode');
            expect(changePagePopupVisibility).toBeCalledWith(true);
            expect(metrics.send).toBeCalledWith([RESTORE_LOGIN_PAGE, RESTORE_LOGIN_ENTER_PHONE_SUCCESS]);

            expect(api.request).toBeCalledWith('auth/restore_login/check_phone', {
                phone_number: 'phone',
                track_id: 'trackId',
                display_language: 'lang',
                confirm_method: 'by_call'
            });
        });

        it('should send request with confirm method = call and invalid phone', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone',
                    confirmMethod: 'by_call',
                    isValidPhone: false,
                    errors: {}
                },
                common: {
                    track_id: 'trackId'
                },
                settings: {
                    language: 'lang'
                }
            }));

            api.__mockSuccess({status: 'ok'});

            checkPhone.check()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(clearErrors).toBeCalled();
            expect(checkPhone.validate).toBeCalled();
            expect(api.request).not.toBeCalled();
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            changePagePopupType.mockClear();
            changePagePopupVisibility.mockClear();
            domikIsLoading.mockClear();
            changeCaptchaState.mockClear();
            changeCheckPhoneStatus.mockClear();
            setErrors.mockClear();
            clearErrors.mockClear();
            setSuggestedAccounts.mockClear();
            switchToModeRestoreLoginResult.mockClear();
            checkPhone.validate = jest.fn();
            switchConfirmationMethod.mockClear();
            metrics.send.mockClear();
        });

        it('should handle errors', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone',
                    confirmMethod: 'by_sms',
                    isValidPhone: true,
                    errors: {}
                },
                common: {
                    track_id: 'trackId'
                },
                settings: {
                    language: 'lang'
                }
            }));
            const errors = ['error.1', 'error.2'];

            api.__mockFail({status: 'ok', errors});

            checkPhone.check()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(clearErrors).toBeCalled();
            expect(setErrors).toBeCalled();
            expect(handleCheckPhoneErrors).toBeCalledWith(errors);
            expect(metrics.send).toBeCalledWith([RESTORE_LOGIN_PAGE, RESTORE_LOGIN_ENTER_PHONE_FAIL, errors[0]]);

            expect(api.request).toBeCalledWith('auth/restore_login/check_phone', {
                phone_number: 'phone',
                track_id: 'trackId',
                display_language: 'lang',
                confirm_method: 'by_sms'
            });
        });

        it('should handle empty errors list', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone',
                    confirmMethod: 'by_sms',
                    isValidPhone: true,
                    errors: {}
                },
                common: {
                    track_id: 'trackId'
                },
                settings: {
                    language: 'lang'
                }
            }));

            api.__mockFail({status: 'ok'});

            checkPhone.check()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(clearErrors).toBeCalled();
            expect(setErrors).toBeCalled();
            expect(handleCheckPhoneErrors).toBeCalledWith([]);
            expect(api.request).toBeCalledWith('auth/restore_login/check_phone', {
                phone_number: 'phone',
                track_id: 'trackId',
                display_language: 'lang',
                confirm_method: 'by_sms'
            });
        });

        it('should handle user.not_verified error', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone',
                    confirmMethod: 'by_sms',
                    isValidPhone: true,
                    errors: {}
                },
                common: {
                    track_id: 'trackId'
                },
                settings: {
                    language: 'lang'
                }
            }));
            const errors = ['user.not_verified', 'error.2'];

            api.__mockFail({status: 'ok', errors});

            checkPhone.check()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(changePagePopupType).toBeCalledWith('restoreLoginEnterCaptcha');
            expect(changePagePopupVisibility).toBeCalledWith(true);
            expect(changeCaptchaState).toBeCalledWith(true);

            expect(api.request).toBeCalledWith('auth/restore_login/check_phone', {
                phone_number: 'phone',
                track_id: 'trackId',
                display_language: 'lang',
                confirm_method: 'by_sms'
            });
        });

        it('should handle phone_secure.not_found error', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone',
                    confirmMethod: 'by_sms',
                    isValidPhone: true,
                    errors: {}
                },
                common: {
                    track_id: 'trackId'
                },
                settings: {
                    language: 'lang'
                }
            }));
            const errors = ['phone_secure.not_found', 'error.2'];

            api.__mockFail({status: 'ok', errors});

            checkPhone.check()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(setErrors).toBeCalled();
            expect(changePagePopupVisibility).toBeCalledWith(false);
            expect(changePagePopupType).toBeCalledWith('');
            expect(setSuggestedAccounts).toBeCalledWith([]);
            expect(switchToModeRestoreLoginResult).toBeCalled();
            expect(handleCheckPhoneErrors).toBeCalledWith(errors);
            expect(metrics.send).toBeCalledWith([RESTORE_LOGIN_PAGE, RESTORE_LOGIN_ENTER_PHONE_FAIL, errors[0]]);

            expect(api.request).toBeCalledWith('auth/restore_login/check_phone', {
                phone_number: 'phone',
                track_id: 'trackId',
                display_language: 'lang',
                confirm_method: 'by_sms'
            });
        });

        it('should handle captcha error', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone',
                    confirmMethod: 'by_sms',
                    isValidPhone: true,
                    errors: {}
                },
                common: {
                    track_id: 'trackId'
                },
                settings: {
                    language: 'lang'
                }
            }));
            const errors = ['captcha.not_matched', 'error.2'];

            api.__mockFail({status: 'ok', errors});

            checkPhone.check()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(setErrors).toBeCalled();
            expect(handleCheckPhoneErrors).toBeCalledWith(errors);
            expect(metrics.send).toBeCalledWith([RESTORE_LOGIN_PAGE, RESTORE_LOGIN_ENTER_CAPTCHA_FAIL]);

            expect(api.request).toBeCalledWith('auth/restore_login/check_phone', {
                phone_number: 'phone',
                track_id: 'trackId',
                display_language: 'lang',
                confirm_method: 'by_sms'
            });
        });
    });

    describe('always cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            changePagePopupType.mockClear();
            changePagePopupVisibility.mockClear();
            domikIsLoading.mockClear();
            changeCaptchaState.mockClear();
            changeCheckPhoneStatus.mockClear();
            setErrors.mockClear();
            clearErrors.mockClear();
            setSuggestedAccounts.mockClear();
            switchToModeRestoreLoginResult.mockClear();
            checkPhone.validate = jest.fn();
            switchConfirmationMethod.mockClear();
            metrics.send.mockClear();
        });

        it('should handle always case', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    phone: 'phone',
                    confirmMethod: 'by_sms',
                    isValidPhone: true,
                    errors: {}
                },
                common: {
                    track_id: 'trackId'
                },
                settings: {
                    language: 'lang'
                }
            }));

            api.__mockAlways({status: 'ok'});

            checkPhone.check()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(false);

            expect(api.request).toBeCalledWith('auth/restore_login/check_phone', {
                phone_number: 'phone',
                track_id: 'trackId',
                display_language: 'lang',
                confirm_method: 'by_sms'
            });
        });
    });
});
