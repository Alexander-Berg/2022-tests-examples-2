import switchToModeRestoreLoginProcess from '../switchToModeRestoreLoginProcess';
import * as router from 'connected-react-router';
import {switchToModeRestoreLoginProcessSuccess} from '../';

jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../', () => ({
    switchToModeRestoreLoginProcessSuccess: jest.fn()
}));

describe('Actions: switchToModeRestoreLoginProcess', () => {
    describe('success cases', () => {
        afterEach(() => {
            router.push.mockClear();
            switchToModeRestoreLoginProcessSuccess.mockClear();
        });

        it('should switch page', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    restoreLoginProcessUrl: 'restoreLoginProcessUrl'
                },
                auth: {
                    mode: 'magic'
                }
            }));

            switchToModeRestoreLoginProcess()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('restoreLoginProcessUrl');
            expect(switchToModeRestoreLoginProcessSuccess).toBeCalled();
        });
        it('should not switch page if mode is equal to "restoreLoginProcess"', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    restoreLoginProcessUrl: 'restoreLoginProcessUrl'
                },
                auth: {
                    mode: 'restoreLoginProcess'
                }
            }));

            switchToModeRestoreLoginProcess()(dispatch, getState);

            expect(router.push).not.toBeCalled();
            expect(switchToModeRestoreLoginProcessSuccess).not.toBeCalled();
        });
    });
});
