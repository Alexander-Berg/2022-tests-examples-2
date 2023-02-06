import switchToModeMagic from '../switchToModeMagic';
import * as router from 'connected-react-router';
import {switchToModeMagicSuccess, setupBackPane} from '../';

jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../', () => ({
    switchToModeMagicSuccess: jest.fn(),
    setupBackPane: jest.fn()
}));

describe('Actions: switchToModeMagic', () => {
    describe('success cases', () => {
        afterEach(() => {
            router.push.mockClear();
            switchToModeMagicSuccess.mockClear();
            setupBackPane.mockClear();
        });

        it('should switch page and setup backpane', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    pane: 'pane',
                    magicUrl: 'magicUrl'
                },
                auth: {
                    mode: 'addingAccount'
                }
            }));

            switchToModeMagic()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('magicUrl');
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith('pane');
            expect(switchToModeMagicSuccess).toBeCalled();
        });

        it('should not switch the page if mode is equal to "magic"', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    pane: 'pane',
                    magicUrl: 'magicUrl'
                },
                auth: {
                    mode: 'magic'
                }
            }));

            switchToModeMagic()(dispatch, getState);

            expect(router.push).not.toBeCalled();
            expect(setupBackPane).not.toBeCalled();
            expect(switchToModeMagicSuccess).not.toBeCalled();
        });
    });
});
