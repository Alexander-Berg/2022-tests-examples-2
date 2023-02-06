import switchToModeRestoreLogin from '../switchToModeRestoreLogin';
import * as router from 'connected-react-router';
import {switchToModeRestoreLoginSuccess} from '../';

jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../', () => ({
    switchToModeRestoreLoginSuccess: jest.fn()
}));
jest.mock('../restoreLogin/submit');

describe('Actions: switchToModeRestoreLogin', () => {
    describe('success cases', () => {
        afterEach(() => {
            router.push.mockClear();
            switchToModeRestoreLoginSuccess.mockClear();
        });

        it('should switch page', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    restoreLoginUrl: 'restoreLoginUrl'
                },
                auth: {
                    mode: 'magic'
                }
            }));

            switchToModeRestoreLogin()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('restoreLoginUrl');
            expect(switchToModeRestoreLoginSuccess).toBeCalled();
        });

        it('should not switch page if mode is equal to "restoreLoginUrl"', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    restoreLoginUrl: 'restoreLoginUrl'
                },
                auth: {
                    mode: 'restoreLogin'
                }
            }));

            switchToModeRestoreLogin()(dispatch, getState);

            expect(router.push).not.toBeCalled();
            expect(switchToModeRestoreLoginSuccess).not.toBeCalled();
        });
        it('should get track for restoration process', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    restoreLoginUrl: 'restoreLoginUrl'
                },
                auth: {
                    mode: 'magic'
                }
            }));

            switchToModeRestoreLogin()(dispatch, getState);
        });
    });
});
