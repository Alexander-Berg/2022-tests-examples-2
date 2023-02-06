import switchToModeEdit from '../switchToModeEdit';
import * as router from 'connected-react-router';
import {switchToModeEditSuccess, setupBackPane} from '../';

jest.mock('connected-react-router', () => ({
    push: jest.fn()
}));
jest.mock('../', () => ({
    switchToModeEditSuccess: jest.fn(),
    setupBackPane: jest.fn()
}));

describe('Actions: switchToModeEdit', () => {
    describe('success cases', () => {
        afterEach(() => {
            router.push.mockClear();
            switchToModeEditSuccess.mockClear();
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
                    unitedAccounts: []
                },
                mode: 'magic'
            }));

            switchToModeEdit()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(3);
            expect(router.push).toBeCalled();
            expect(router.push).toBeCalledWith('editUrl');
            expect(setupBackPane).toBeCalled();
            expect(setupBackPane).toBeCalledWith(null);
            expect(switchToModeEditSuccess).toBeCalled();
        });
    });
});
