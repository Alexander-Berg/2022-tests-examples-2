import mapStateToProps from '../mapStateToProps';

describe('Components: WelcomePage.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            common: {
                addUserUrl: 'addUserUrl',
                editUrl: 'editUrl',
                welcomeUrl: 'welcomeUrl',
                backPane: 'backPane'
            },
            auth: {
                processedAccount: {
                    uid: 'account.uid',
                    preferred_auth_method: 'otp',
                    allowed_auth_methods: ['otp'],
                    primaryAliasType: 5
                },
                form: {
                    login: 'form.login',
                    isForceOTP: false
                },
                unitedAccounts: [{}, {}]
            },
            customs: {
                tagline: 'appmetrica'
            },
            social: {
                providers: []
            },
            mailAuth: {
                isUpdatedAuthLetterStatus: true
            },
            messengerAuth: {
                isEnabled: false
            }
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            hasOnlyOneSuggestedAccount: false,
            addUserUrl: 'addUserUrl',
            editUrl: 'editUrl',
            welcomeUrl: 'welcomeUrl',
            backPane: 'backPane',
            hasUnitedAccounts: true,
            isAm: false,
            customTagline: i18n('appmetrica'),
            account: {
                uid: 'account.uid',
                preferred_auth_method: 'otp',
                allowed_auth_methods: ['otp'],
                primaryAliasType: 5
            },
            login: 'form.login',
            hasSocialButton: false,
            isShowPasswordField: false,
            isShowMailAuthBtn: true,
            isShowMessengerAuthBtn: false,
            isForceMailAuthEnable: false,
            isFullScreen: false,
            isMessengerAuthEnabled: false,
            isMailAuthCaptchaRequired: false,
            isMessengerAuthCaptchaRequired: false,
            isSocialAccount: false,
            isMailAuthEnabled: true,
            mailAuthExperiment: undefined,
            neoPhonishPrefix: undefined,
            isShowSMSAuthBtn: false,
            isShowSamlSsoButton: false,
            isShowRestoreNeoPhonishButton: false
        });
    });

    it('should fallback props', () => {
        const state = {
            common: {
                addUserUrl: 'addUserUrl',
                editUrl: 'editUrl',
                welcomeUrl: 'welcomeUrl',
                backPane: 'backPane'
            },
            auth: {
                processedAccount: {
                    uid: 'account.uid',
                    preferred_auth_method: 'password',
                    allowed_auth_methods: ['otp']
                },
                form: {
                    login: 'form.login',
                    isForceOTP: true
                },
                unitedAccounts: [{}, {}]
            },
            customs: {
                tagline: 'appmetrica'
            },
            social: {
                providers: [
                    {
                        data: {
                            code: 'vk'
                        }
                    }
                ]
            },
            mailAuth: {
                isEnabled: false
            },
            messengerAuth: {
                isEnabled: false
            }
        };

        let result = mapStateToProps(state);

        expect(result.isShowPasswordField).toBe(false);

        state.auth.processedAccount.preferred_auth_method = null;
        state.auth.processedAccount.allowed_auth_methods = undefined;
        state.customs.tagline = null;
        result = mapStateToProps(state);

        expect(result.account).toEqual({
            uid: 'account.uid',
            preferred_auth_method: null,
            allowed_auth_methods: undefined
        });
        expect(result.isShowPasswordField).toBe(true);
        expect(result.customTagline).toBe(i18n('_AUTH_.sign_in_title'));

        state.auth.processedAccount.preferred_auth_method = 'social_vk';
        result = mapStateToProps(state);

        expect(result.hasSocialButton).toBe(true);
    });
});
