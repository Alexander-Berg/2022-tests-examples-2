import redirectToEmailsPage from '../redirect_to_emails_page';
import {restoreStateAndRedirect, redirectToRetpath} from '../../../actions';

jest.mock('../../../actions', () => ({
    restoreStateAndRedirect: jest.fn(),
    redirectToRetpath: jest.fn()
}));

describe('Action: redirectToEmailsPage', () => {
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

        redirectToEmailsPage()(dispatch, getState);

        expect(restoreStateAndRedirect).toBeCalledWith(`${host}/profile/emails`);
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

        redirectToEmailsPage()(dispatch, getState);

        expect(window.open).toBeCalledWith(`${host}/profile/emails?retpath=${encodeURIComponent(retpath)}`);
        expect(redirectToRetpath).toBeCalled();
        expect(dispatch).toBeCalled();
        redirectToRetpath.mockClear();
        window.open.mockClear();
    });
});
