import redirectToRegistration from '../redirectToRegistration';
import formatRegistrationUrl from '../../utils/formatRegistrationUrl';

jest.mock('../../utils/formatRegistrationUrl');
const {location} = window;

describe('Action: redirectToRegistration', () => {
    beforeEach(() => {
        delete window.location;
        window.location = {
            href: '123'
        };
    });

    afterEach(() => {
        window.location = location;
    });

    it('should redirect to simple registration', () => {
        const regUrl = 'registrationUrl';

        formatRegistrationUrl.mockImplementation((url) => url);

        const dispatch = jest.fn();
        const getState = jest.fn(() => ({
            auth: {
                form: {
                    registrationLogin: 'login',
                    registrationType: 'portal',
                    registrationPhoneNumber: 'phone',
                    registrationCountry: 'country'
                }
            },
            common: {
                registration_url_with_params: regUrl,
                lite_registration_url_with_params: 'liteRegistrationUrl'
            }
        }));

        redirectToRegistration()(dispatch, getState);

        expect(getState).toBeCalled();
        expect(window.location.href).toEqual(regUrl);
    });

    it('should redirect to lite registration', () => {
        const regUrl = 'liteRegistrationUrl';

        formatRegistrationUrl.mockImplementation((url) => url);

        const dispatch = jest.fn();
        const getState = jest.fn(() => ({
            auth: {
                form: {
                    registrationLogin: 'login',
                    registrationType: 'lite',
                    registrationPhoneNumber: 'phone',
                    registrationCountry: 'country'
                }
            },
            common: {
                registration_url_with_params: 'registrationUrl',
                lite_registration_url_with_params: regUrl
            }
        }));

        redirectToRegistration()(dispatch, getState);

        expect(getState).toBeCalled();
        expect(window.location.href).toEqual(regUrl);
    });
});
