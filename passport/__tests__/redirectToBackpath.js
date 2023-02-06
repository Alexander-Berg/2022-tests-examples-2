import redirectToBackpath from '../redirectToBackpath';
import {redirectToBackpathSuccess} from '../';
import restoreStateAndRedirect from '../restoreStateAndRedirect';

jest.mock('../', () => ({
    redirectToBackpathSuccess: jest.fn()
}));
jest.mock('../restoreStateAndRedirect');

describe('Actions: redirectToBackpath', () => {
    describe('success cases', () => {
        it('should handle with backpath param', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    backpath: 'backpath',
                    profile_url: 'profileUrl'
                }
            }));

            redirectToBackpath()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(redirectToBackpathSuccess).toBeCalled();
            expect(restoreStateAndRedirect).toBeCalledWith('backpath');
        });

        it('should fallback backpath param to profile url', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    profile_url: 'profileUrl'
                }
            }));

            redirectToBackpath()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(redirectToBackpathSuccess).toBeCalled();
            expect(restoreStateAndRedirect).toBeCalledWith('profileUrl');
        });
    });
});
