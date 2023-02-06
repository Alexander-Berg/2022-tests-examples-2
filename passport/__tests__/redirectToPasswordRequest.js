import redirectToPasswordRequest from '../redirectToPasswordRequest';
import restoreStateAndRedirect from '../restoreStateAndRedirect';

jest.mock('../restoreStateAndRedirect');

describe('Action: redirectToPasswordRequest', () => {
    it('should redirect without login and retpath', () => {
        const dispatch = jest.fn();
        const authUrl = '/auth';
        const getState = jest.fn(() => ({
            auth: {},
            common: {
                authUrl
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
            auth: {
                processedAccount: {
                    login: processedAccountLogin
                },
                defaultAccount: {
                    login: defaultAccountLogin
                }
            },
            common: {
                authUrl
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
            auth: {
                defaultAccount: {
                    login: defaultAccountLogin
                }
            },
            common: {
                authUrl
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
            auth: {
                defaultAccount: {
                    login: defaultAccountLogin
                }
            },
            common: {
                currentUrl,
                authUrl
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
