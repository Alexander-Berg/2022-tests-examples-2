import switchToModeRestoreLoginResult from '../switchToModeRestoreLoginResult';
import * as router from 'connected-react-router';
import {switchToModeRestoreLoginResultSuccess} from '../';

jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../', () => ({
    switchToModeRestoreLoginResultSuccess: jest.fn()
}));

describe('Actions: switchToModeRestoreLoginResult', () => {
    describe('success cases', () => {
        afterEach(() => {
            router.push.mockClear();
            switchToModeRestoreLoginResultSuccess.mockClear();
        });

        it('should switch page', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    restoreLoginResultUrl: 'restoreLoginResultUrl'
                },
                auth: {
                    mode: 'magic'
                }
            }));

            switchToModeRestoreLoginResult()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('restoreLoginResultUrl');
            expect(switchToModeRestoreLoginResultSuccess).toBeCalled();
        });
        it('should not switch page if mode is equal to "restoreLoginResult"', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    restoreLoginResultUrl: 'restoreLoginResultUrl'
                },
                auth: {
                    mode: 'restoreLoginResult'
                }
            }));

            switchToModeRestoreLoginResult()(dispatch, getState);

            expect(router.push).not.toBeCalled();
            expect(switchToModeRestoreLoginResultSuccess).not.toBeCalled();
        });
    });
});
