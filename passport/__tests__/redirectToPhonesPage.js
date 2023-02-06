import redirectToPhonesPage from '../redirectToPhonesPage';
import restoreStateAndRedirect from '../restoreStateAndRedirect';
import redirectToRetpath from '../redirectToRetpath';

jest.mock('../restoreStateAndRedirect');
jest.mock('../redirectToRetpath');

describe('Action: redirectToPhonesPage', () => {
    it('should redirect without retpath', () => {
        const dispatch = jest.fn();
        const host = 'https://host';
        const getState = jest.fn(() => ({
            settings: {
                host
            },
            common: {
                retpath: ''
            }
        }));

        restoreStateAndRedirect.mockImplementation(() => () => {});

        redirectToPhonesPage()(dispatch, getState);

        expect(restoreStateAndRedirect).toBeCalledWith(`${host}/profile/phones`);
        expect(dispatch).toBeCalled();
        restoreStateAndRedirect.mockClear();
    });

    it('should redirect with retpath', () => {
        const dispatch = jest.fn();
        const host = 'https://host';
        const retpath = 'https://ya.ru';
        const getState = jest.fn(() => ({
            settings: {
                host
            },
            common: {
                retpath
            }
        }));

        restoreStateAndRedirect.mockImplementation(() => () => {});
        window.open = jest.fn();

        redirectToPhonesPage()(dispatch, getState);

        expect(window.open).toBeCalledWith(`${host}/profile/phones?retpath=${encodeURIComponent(retpath)}`);
        expect(redirectToRetpath).toBeCalled();
        expect(dispatch).toBeCalled();
        redirectToRetpath.mockClear();
        window.open.mockClear();
    });
});
