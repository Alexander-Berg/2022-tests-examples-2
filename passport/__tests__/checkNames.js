import api from '../../../../api';
jest.mock('../../../../api');

import {clearErrors, setSuggestedAccounts, setErrors} from '../';
import switchToModeRestoreLoginResult from '../../switchToModeRestoreLoginResult';
import checkNames from '../checkNames';
import {handleNamesErrors} from '../handleErrors';

jest.mock('../', () => ({
    clearErrors: jest.fn(),
    setSuggestedAccounts: jest.fn(),
    setErrors: jest.fn()
}));

jest.mock('../../switchToModeRestoreLoginResult');

jest.mock('../handleErrors', () => ({
    handleNamesErrors: jest.fn()
}));

describe('Actions: checkNames', () => {
    describe('success cases', () => {
        beforeEach(() => {
            clearErrors.mockClear();
            setSuggestedAccounts.mockClear();
            setErrors.mockClear();
            switchToModeRestoreLoginResult.mockClear();
            api.request.mockClear();
        });

        it('should send request with valid params', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    firstName: 'firstName',
                    lastName: 'lastName'
                },
                common: {
                    track_id: 'trackId'
                }
            }));
            const accounts = [{id: 1}, {id: 2}];

            api.__mockSuccess({status: 'ok', accounts});

            checkNames()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(clearErrors).toBeCalled();
            expect(setSuggestedAccounts).toBeCalledWith(accounts);
            expect(switchToModeRestoreLoginResult).toBeCalled();

            expect(api.request).toBeCalledWith('auth/restore_login/check_names', {
                firstname: 'firstName',
                lastname: 'lastName',
                track_id: 'trackId',
                allow_neophonish: true
            });
        });

        it('should handle success response without accounts', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    firstName: 'firstName',
                    lastName: 'lastName'
                },
                common: {
                    track_id: 'trackId'
                }
            }));

            api.__mockSuccess({status: 'ok'});

            checkNames()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(setSuggestedAccounts).toBeCalledWith([]);
            expect(switchToModeRestoreLoginResult).toBeCalled();

            expect(api.request).toBeCalledWith('auth/restore_login/check_names', {
                firstname: 'firstName',
                lastname: 'lastName',
                track_id: 'trackId',
                allow_neophonish: true
            });
        });
    });

    describe('fail cases', () => {
        beforeEach(() => {
            clearErrors.mockClear();
            setSuggestedAccounts.mockClear();
            setErrors.mockClear();
            switchToModeRestoreLoginResult.mockClear();
            api.request.mockClear();
        });

        it('should handle errors', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    firstName: 'firstName',
                    lastName: 'lastName'
                },
                common: {
                    track_id: 'trackId'
                }
            }));
            const errors = ['error.1', 'error.2'];

            api.__mockFail({status: 'ok', errors});

            checkNames()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(handleNamesErrors).toBeCalledWith(errors);

            expect(api.request).toBeCalledWith('auth/restore_login/check_names', {
                firstname: 'firstName',
                lastname: 'lastName',
                track_id: 'trackId',
                allow_neophonish: true
            });
        });

        it('should handle compare.not_matched error', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                restoreLogin: {
                    firstName: 'firstName',
                    lastName: 'lastName'
                },
                common: {
                    track_id: 'trackId'
                }
            }));
            const errors = ['compare.not_matched', 'error.2'];

            api.__mockFail({status: 'ok', errors});

            checkNames()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(clearErrors).toBeCalled();
            expect(setSuggestedAccounts).toBeCalledWith([]);
            expect(switchToModeRestoreLoginResult).toBeCalled();

            expect(api.request).toBeCalledWith('auth/restore_login/check_names', {
                firstname: 'firstName',
                lastname: 'lastName',
                track_id: 'trackId',
                allow_neophonish: true
            });
        });
    });
});
