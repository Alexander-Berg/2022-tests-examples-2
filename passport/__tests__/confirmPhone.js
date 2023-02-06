import api from '../../../../api';
jest.mock('../../../../api');

import {clearErrors, setErrors} from '../';
import switchToModeRestoreLoginProcess from '../../switchToModeRestoreLoginProcess';
import {changePagePopupType, changePagePopupVisibility} from '../../';
import metrics from '../../../../metrics';
import {
    RESTORE_LOGIN_ENTER_PHONE_CODE_SUCCESS,
    RESTORE_LOGIN_ENTER_PHONE_CODE_FAIL,
    RESTORE_LOGIN_PAGE
} from '../../../metrics_constants';

import confirmPhone from '../confirmPhone';
import {handlePhoneErrors} from '../handleErrors';

// const handleErrorsHelper = helpers.handleErrors;

jest.mock('../', () => ({
    clearErrors: jest.fn(),
    setErrors: jest.fn()
}));

jest.mock('../../', () => ({
    changePagePopupType: jest.fn(),
    changePagePopupVisibility: jest.fn()
}));

jest.mock('../../switchToModeRestoreLoginProcess');

jest.mock('../../../../metrics', () => ({
    send: jest.fn()
}));

jest.mock('../handleErrors', () => ({
    handlePhoneErrors: jest.fn()
}));

describe('Actions: confirmPhone', () => {
    describe('success cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            clearErrors.mockClear();
            setErrors.mockClear();
            changePagePopupType.mockClear();
            changePagePopupVisibility.mockClear();
            switchToModeRestoreLoginProcess.mockClear();
            metrics.send.mockClear();
        });

        it('should send request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    track_id: 'trackId'
                },
                restoreLogin: {
                    confirmationCode: 'confirmationCode'
                }
            }));

            api.__mockSuccess({status: 'ok'});

            confirmPhone()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(4);
            expect(clearErrors).toBeCalled();
            expect(changePagePopupVisibility).toBeCalledWith(false);
            expect(changePagePopupType).toBeCalledWith('');
            expect(switchToModeRestoreLoginProcess).toBeCalled();
            expect(metrics.send).toBeCalledWith([RESTORE_LOGIN_PAGE, RESTORE_LOGIN_ENTER_PHONE_CODE_SUCCESS]);

            expect(api.request).toBeCalledWith('auth/restore_login/confirm_phone', {
                track_id: 'trackId',
                code: 'confirmationCode'
            });
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            api.request.mockClear();
            clearErrors.mockClear();
            setErrors.mockClear();
            changePagePopupType.mockClear();
            changePagePopupVisibility.mockClear();
            switchToModeRestoreLoginProcess.mockClear();
            metrics.send.mockClear();
        });

        it('should send request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    track_id: 'trackId'
                },
                restoreLogin: {
                    confirmationCode: 'confirmationCode'
                }
            }));
            const errors = ['error.1', 'error.2'];

            api.__mockFail({status: 'ok', errors});

            confirmPhone()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(metrics.send).toBeCalledWith([RESTORE_LOGIN_PAGE, RESTORE_LOGIN_ENTER_PHONE_CODE_FAIL]);
            expect(handlePhoneErrors).toBeCalledWith(errors);

            expect(api.request).toBeCalledWith('auth/restore_login/confirm_phone', {
                track_id: 'trackId',
                code: 'confirmationCode'
            });
        });
    });
});
