import mapStateToProps from '../mapStateToProps';

describe('Components: LoginForm.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            auth: {
                form: {
                    login: 'login',
                    isCanRegister: true,
                    registrationLogin: 'registrationLogin',
                    registrationType: 'portal',
                    registrationPhoneNumber: 'registrationPhoneNumber',
                    registrationCountry: 'registrationCountry'
                },
                mode: 'mode',
                loginError: 'loginError',
                loading: true
            },
            common: {
                registration_url_with_params: 'url?login=login&phone_number=phone_number&country=country',
                lite_registration_url_with_params: 'liteRegistrationUrlWithParams',
                retpath: 'retpath',
                fretpath: 'fretpath',
                clean: 'clean',
                csrf: 'csrf',
                addUserUrl: 'addUserUrl',
                authUrl: 'authUrl',
                backPane: 'backPane',
                neoPhonish: {origins: ['neophonish']},
                experiments: {flags: ['auth-toggle-input-exp']}
            },
            settings: {
                ua: {
                    isTouch: false
                }
            },
            customs: {
                yaIdType: ''
            }
        };

        const result = mapStateToProps(state);

        expect(result).toEqual({
            registrationUrl: 'url?&phone_number=registrationPhoneNumber&country=registrationCountry',
            registrationType: 'portal',
            login: 'login',
            retpath: 'retpath',
            fretpath: 'fretpath',
            clean: 'clean',
            csrf: 'csrf',
            addUserUrl: 'addUserUrl',
            authUrl: 'authUrl',
            backPane: 'backPane',
            isCanRegister: true,
            registrationLogin: 'registrationLogin',
            mode: 'mode',
            hasCaptcha: false,
            loading: true,
            registrationExpUrl: undefined,
            isPreRegisterExp: undefined,
            isRegisterWithSuggestToRestoreByPhoneInDaHouse: undefined,
            isNeoPhonishRegisterExp: false,
            isToggleInputExp: true,
            isAm: undefined
        });
    });

    it('should fallback props', () => {
        const state = {
            auth: {
                form: {
                    login: 'login',
                    isCanRegister: true,
                    registrationType: 'portal',
                    registrationLogin: null
                },
                mode: 'mode',
                loginError: 'loginError',
                loading: false
            },
            common: {
                registration_url_with_params: 'url?login=login&phone_number=phone_number&country=country',
                lite_registration_url_with_params: 'lite_url?login=login&phone_number=phone_number&country=country',
                liteRegisterUrl: 'lite_auth_url',
                retpath: 'retpath',
                fretpath: 'fretpath',
                clean: 'clean',
                csrf: 'csrf',
                addUserUrl: 'addUserUrl',
                authUrl: 'authUrl',
                backPane: 'backPane',
                neoPhonish: {origins: ['neophonish']}
            },
            settings: {
                ua: {
                    isTouch: false
                }
            },
            customs: {
                yaIdType: ''
            }
        };

        let result = mapStateToProps(state);

        expect(result).toEqual({
            registrationUrl: 'url?',
            registrationType: 'portal',
            login: 'login',
            retpath: 'retpath',
            fretpath: 'fretpath',
            clean: 'clean',
            csrf: 'csrf',
            addUserUrl: 'addUserUrl',
            authUrl: 'authUrl',
            backPane: 'backPane',
            isCanRegister: true,
            registrationLogin: null,
            mode: 'mode',
            hasCaptcha: false,
            loading: false,
            registrationExpUrl: undefined,
            isNeoPhonishRegisterExp: false,
            isToggleInputExp: false,
            isAm: undefined
        });

        state.auth.form.registrationType = 'lite';
        result = mapStateToProps(state);

        expect(result).toEqual({
            registrationUrl: 'lite_auth_url',
            registrationType: 'lite',
            login: 'login',
            retpath: 'retpath',
            fretpath: 'fretpath',
            clean: 'clean',
            csrf: 'csrf',
            addUserUrl: 'addUserUrl',
            authUrl: 'authUrl',
            backPane: 'backPane',
            isCanRegister: true,
            registrationLogin: null,
            mode: 'mode',
            hasCaptcha: false,
            loading: false,
            registrationExpUrl: undefined,
            isNeoPhonishRegisterExp: false,
            isToggleInputExp: false,
            isAm: undefined
        });

        state.auth.form.registrationLogin = 'registrationLogin';
        state.auth.form.registrationPhoneNumber = null;
        result = mapStateToProps(state);

        expect(result).toEqual({
            registrationUrl: 'lite_auth_url',
            registrationType: 'lite',
            login: 'login',
            retpath: 'retpath',
            fretpath: 'fretpath',
            clean: 'clean',
            csrf: 'csrf',
            addUserUrl: 'addUserUrl',
            authUrl: 'authUrl',
            backPane: 'backPane',
            isCanRegister: true,
            registrationLogin: 'registrationLogin',
            mode: 'mode',
            hasCaptcha: false,
            loading: false,
            registrationExpUrl: undefined,
            isNeoPhonishRegisterExp: false,
            isToggleInputExp: false,
            isAm: undefined
        });
    });
});
