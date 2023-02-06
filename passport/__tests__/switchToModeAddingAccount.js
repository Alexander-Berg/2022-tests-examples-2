import switchToModeAddingAccount from '../switchToModeAddingAccount';
import * as router from 'connected-react-router';
import {switchToModeAddingAccountSuccess, setupBackPane} from '../';

jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../', () => ({
    switchToModeAddingAccountSuccess: jest.fn(),
    setupBackPane: jest.fn()
}));

describe('Actions: switchToModeAddingAccount', () => {
    describe('success cases', () => {
        afterEach(() => {
            router.push.mockClear();
            switchToModeAddingAccountSuccess.mockClear();
            setupBackPane.mockClear();
        });

        it('should switch page and setup backpane', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    addUserUrl: 'addUserUrl',
                    editUrl: 'editUrl'
                },
                auth: {
                    unitedAccounts: [],
                    mode: 'edit'
                }
            }));

            switchToModeAddingAccount()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('addUserUrl');
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith(null);
            expect(switchToModeAddingAccountSuccess).toBeCalled();
        });

        it('should switch page and setup backpane', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    addUserUrl: 'addUserUrl',
                    editUrl: 'editUrl'
                },
                auth: {
                    unitedAccounts: [{}, {}],
                    mode: 'edit'
                }
            }));

            switchToModeAddingAccount()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('addUserUrl');
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith('editUrl');
            expect(switchToModeAddingAccountSuccess).toBeCalled();
        });

        it('should not switch the page if mode is equal to "addingAccount"', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    addUserUrl: 'addUserUrl',
                    editUrl: 'editUrl'
                },
                auth: {
                    unitedAccounts: [{}, {}],
                    mode: 'addingAccount'
                }
            }));

            switchToModeAddingAccount()(dispatch, getState);

            expect(router.push).not.toBeCalled();
            expect(setupBackPane).not.toBeCalled();
            expect(switchToModeAddingAccountSuccess).not.toBeCalled();
        });
    });
});
