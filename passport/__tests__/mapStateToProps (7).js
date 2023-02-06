import mapStateToProps from '../mapStateToProps';

describe('Components: AnimatedLayer.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            auth: {
                unitedAccounts: {
                    1: {
                        uid: 1
                    }
                },
                form: {
                    isCanRegister: true
                },
                isCaptchaRequired: true,
                magicError: 'magicError',
                loginError: 'loginError',
                passwordError: 'passwordError',
                captchaError: 'captchaError'
            },
            mobileMenu: {
                isShowMobileMenu: true
            },
            pagePopup: {
                isShowPagePopup: true
            },
            additionalDataRequest: {
                errors: 'additionalDataErrors'
            }
        };

        let result = mapStateToProps(state);

        expect(result).toEqual({
            isCanRegister: true,
            accounts: {
                1: {
                    uid: 1
                }
            },
            isCaptchaRequired: true,
            magicError: 'magicError',
            loginError: 'loginError',
            passwordError: 'passwordError',
            captchaError: 'captchaError',
            isShowMobileMenu: true,
            isShowPagePopup: true,
            additionalDataErrors: 'additionalDataErrors'
        });

        delete state.auth.form;

        result = mapStateToProps(state);

        expect(result.isCanRegister).toBe(false);
    });
});
