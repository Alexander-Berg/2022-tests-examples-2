import redirectToPasswordRequest from '../redirect_to_password_request';
import {restoreStateAndRedirect} from '../../../actions';

jest.mock('../../../actions', () => ({
    restoreStateAndRedirect: jest.fn()
}));

describe('Action: redirectToPasswordRequest', () => {
    it('should redirect without login and retpath', () => {
        const dispatch = jest.fn();
        const authUrl = '/auth';
        const getState = jest.fn(() => ({
            one_domik: {},
            common: {
                auth_url: authUrl
            }
        }));

        restoreStateAndRedirect.mockImplementation(() => () => {});

        redirectToPasswordRequest()(dispatch, getState);

        expect(restoreStateAndRedirect).toBeCalledWith(authUrl);
        expect(dispatch).toBeCalled();
        restoreStateAndRedirect.mockClear();
    });

    it('should redirect with processedAccount login', () => {
        const dispatch = jest.fn();
        const authUrl = '/auth';
        const processedAccountLogin = 'processedAccount.login';
        const defaultAccountLogin = 'defaultAccount.login';
        const getState = jest.fn(() => ({
            one_domik: {
                processedAccount: {
                    login: processedAccountLogin
                },
                defaultAccount: {
                    login: defaultAccountLogin
                }
            },
            common: {
                auth_url: authUrl
            }
        }));

        restoreStateAndRedirect.mockImplementation(() => () => {});

        redirectToPasswordRequest()(dispatch, getState);

        expect(restoreStateAndRedirect).toBeCalledWith(`${authUrl}?login=${processedAccountLogin}`);
        expect(dispatch).toBeCalled();
        restoreStateAndRedirect.mockClear();
    });

    it('should redirect with defaultAccount login', () => {
        const dispatch = jest.fn();
        const authUrl = '/auth';
        const defaultAccountLogin = 'defaultAccount.login';
        const getState = jest.fn(() => ({
            one_domik: {
                defaultAccount: {
                    login: defaultAccountLogin
                }
            },
            common: {
                auth_url: authUrl
            }
        }));

        restoreStateAndRedirect.mockImplementation(() => () => {});

        redirectToPasswordRequest()(dispatch, getState);

        expect(restoreStateAndRedirect).toBeCalledWith(`${authUrl}?login=${defaultAccountLogin}`);
        expect(dispatch).toBeCalled();
        restoreStateAndRedirect.mockClear();
    });

    it('should redirect with login and retpath', () => {
        const dispatch = jest.fn();
        const authUrl = '/auth';
        const currentUrl = 'https://ya.ru';
        const defaultAccountLogin = 'defaultAccount.login';
        const getState = jest.fn(() => ({
            one_domik: {
                defaultAccount: {
                    login: defaultAccountLogin
                }
            },
            common: {
                currentUrl,
                auth_url: authUrl
            }
        }));

        restoreStateAndRedirect.mockImplementation(() => () => {});

        redirectToPasswordRequest()(dispatch, getState);

        expect(restoreStateAndRedirect).toBeCalledWith(
            `${authUrl}?login=${encodeURIComponent(defaultAccountLogin)}&retpath=${encodeURIComponent(currentUrl)}`
        );
        expect(dispatch).toBeCalled();
        restoreStateAndRedirect.mockClear();
    });
});
