import mapStateToProps from '../mapStateToProps';

describe('Components: AddAccountPage.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            auth: {
                form: {
                    isCanRegister: true
                },
                unitedAccounts: [{}, {}]
            },
            common: {
                addUserUrl: 'addUserUrl',
                editUrl: 'editUrl'
            },
            customs: {
                tagline: 'appmetrica'
            }
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            addUserUrl: 'addUserUrl',
            editUrl: 'editUrl',
            isAm: undefined,
            isCanRegister: true,
            isFullScreen: false,
            isWebView: undefined,
            isWebViewWithSocialAuth: undefined,
            origin: undefined,
            yandexSupportUrl: undefined,
            hasUnitedAccounts: true,
            customTagline: i18n('appmetrica'),
            hideTagline: false,
            hideSocialBlock: false
        });
    });

    it('should fallback props', () => {
        const state = {
            auth: {
                form: {
                    isCanRegister: true
                },
                unitedAccounts: [{}, {}]
            },
            common: {
                addUserUrl: 'addUserUrl',
                editUrl: 'editUrl'
            },
            customs: {}
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            addUserUrl: 'addUserUrl',
            editUrl: 'editUrl',
            isAm: undefined,
            isCanRegister: true,
            isFullScreen: false,
            isWebView: undefined,
            isWebViewWithSocialAuth: undefined,
            origin: undefined,
            yandexSupportUrl: undefined,
            hasUnitedAccounts: true,
            customTagline: i18n('_AUTH_.sign_in_title.yandexid'),
            hideTagline: false,
            hideSocialBlock: false
        });
    });
    it.each([
        [
            {auth: {form: {}, isBookQREnabled: true}, customs: {}, router: {location: {pathname: '/auth'}}},
            'hideTagline',
            true
        ],
        [
            {auth: {form: {}, isBookQREnabled: true}, customs: {}, router: {location: {pathname: '/auth/add'}}},
            'hideTagline',
            true
        ],
        [
            {auth: {form: {}, isBookQREnabled: true}, customs: {}, router: {location: {pathname: '/auth/list'}}},
            'hideTagline',
            false
        ],
        [
            {auth: {form: {}, isBookQREnabled: false}, customs: {}, router: {location: {pathname: '/auth'}}},
            'hideTagline',
            false
        ]
    ])('should return correct props on state: %o with prop: %s with value: %s', (state, propName, expected) => {
        expect(mapStateToProps(state)[propName]).toEqual(expected);
    });
});
