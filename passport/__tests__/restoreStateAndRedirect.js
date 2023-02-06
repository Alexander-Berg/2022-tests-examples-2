import restoreStateAndRedirect from '../restoreStateAndRedirect';
import {domikIsLoading, redirect} from '../';
import * as router from 'connected-react-router';

jest.mock('../', () => ({
    domikIsLoading: jest.fn(),
    redirect: jest.fn()
}));
jest.mock('connected-react-router', () => ({
    replace: jest.fn()
}));

describe('Actions: restoreStateAndRedirect', () => {
    describe('success cases', () => {
        it('should handle with retpath param', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    editUrl: 'editUrl'
                },
                auth: {}
            }));

            restoreStateAndRedirect('/url')(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(domikIsLoading).toBeCalled();
            expect(domikIsLoading).toBeCalledWith(true);
            expect(router.replace).toBeCalledWith('editUrl');
            expect(redirect).toBeCalledWith('/url');
        });
    });
});
