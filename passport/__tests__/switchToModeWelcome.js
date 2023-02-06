import switchToModeWelcome from '../switchToModeWelcome';
import * as router from 'connected-react-router';
import {switchToModeWelcomeSuccess} from '../';

jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../', () => ({
    switchToModeWelcomeSuccess: jest.fn()
}));

describe('Actions: switchToModeWelcome', () => {
    describe('success cases', () => {
        afterEach(() => {
            router.push.mockClear();
            switchToModeWelcomeSuccess.mockClear();
        });

        it('should switch page', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    welcomeUrl: 'welcomeUrl'
                },
                auth: {
                    mode: 'magic'
                }
            }));

            switchToModeWelcome()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('welcomeUrl');
            expect(switchToModeWelcomeSuccess).toBeCalled();
        });
        it('should not switch page if mode is equal to "welcome"', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    welcomeUrl: 'welcomeUrl'
                },
                auth: {
                    mode: 'welcome'
                }
            }));

            switchToModeWelcome()(dispatch, getState);

            expect(router.push).not.toBeCalled();
            expect(switchToModeWelcomeSuccess).not.toBeCalled();
        });
    });
});
