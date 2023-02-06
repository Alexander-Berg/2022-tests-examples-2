import switchToModePreRegister from '../switchToModePreRegister';
import * as router from 'connected-react-router';

jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));

describe('Actions: switchToModePreRegister', () => {
    describe('success cases', () => {
        afterEach(() => {
            router.push.mockClear();
        });

        it('should switch page', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    preRegisterUrl: 'preRegisterUrl'
                },
                auth: {
                    mode: 'magic'
                }
            }));

            switchToModePreRegister()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(1);
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('preRegisterUrl');
        });

        it('should not switch page if mode is equal to "preregister"', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    preRegisterUrl: 'preRegisterUrl'
                },
                auth: {
                    mode: 'preRegister'
                }
            }));

            switchToModePreRegister()(dispatch, getState);

            expect(router.push).not.toBeCalled();
        });
    });
});
