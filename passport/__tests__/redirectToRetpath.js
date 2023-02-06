import redirectToRetpath from '../redirectToRetpath';
import {redirectToRetpathSuccess} from '../';
import restoreStateAndRedirect from '../restoreStateAndRedirect';

jest.mock('../', () => ({
    redirectToRetpathSuccess: jest.fn()
}));
jest.mock('../restoreStateAndRedirect');

describe('Actions: redirectToRetpath', () => {
    describe('success cases', () => {
        it('should handle with retpath param', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    retpath: 'retpath',
                    profile_url: 'profileUrl'
                }
            }));

            redirectToRetpath()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(redirectToRetpathSuccess).toBeCalled();
            expect(restoreStateAndRedirect).toBeCalledWith('retpath');
        });

        it('should fallback retpath param to profile url', () => {
            const dispatch = jest.fn();
            const getState = jest.fn(() => ({
                common: {
                    profile_url: 'profileUrl'
                }
            }));

            redirectToRetpath()(dispatch, getState);

            expect(dispatch).toBeCalled();
            expect(dispatch.mock.calls.length).toBe(2);
            expect(redirectToRetpathSuccess).toBeCalled();
            expect(restoreStateAndRedirect).toBeCalledWith('profileUrl');
        });
    });
});
