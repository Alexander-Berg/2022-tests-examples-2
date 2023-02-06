import mapStateToProps from '../mapStateToProps';

describe('Components: PasswordForm.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            common: {
                track_id: 'track',
                csrf: 'csrf',
                authUrl: 'authUrl'
            },
            auth: {
                form: {
                    isForceOTP: false,
                    password: 'formPassword'
                },
                passwordError: 'passwordError',
                processedAccount: {},
                loading: true
            }
        };

        let result = mapStateToProps(state, {});

        expect(result).toEqual({
            password: 'formPassword',
            trackId: 'track',
            csrf: 'csrf',
            authUrl: 'authUrl',
            passwordError: 'passwordError',
            isShowSubmitButton: true,
            isShowPasswordField: true,
            isShowOTPField: false,
            isShouldFallbackToPassword: false,
            hasCaptcha: false,
            isMagicAuth: false,
            loading: true,
            hidePasswordAccountSuggest: false,
            isShowQrButton: true
        });

        state.auth.processedAccount.allowed_auth_methods = ['otp'];
        state.auth.processedAccount.preferred_auth_method = 'otp';
        state.auth.form.isForceOTP = true;
        result = mapStateToProps(state, {});

        expect(result).toEqual({
            password: 'formPassword',
            trackId: 'track',
            csrf: 'csrf',
            authUrl: 'authUrl',
            passwordError: 'passwordError',
            isShowSubmitButton: true,
            isShowPasswordField: false,
            isShouldFallbackToPassword: false,
            isShowOTPField: true,
            hasCaptcha: false,
            isMagicAuth: false,
            loading: true,
            hidePasswordAccountSuggest: false,
            isShowQrButton: true
        });

        state.auth.processedAccount.allowed_auth_methods = ['magic'];
        state.auth.processedAccount.preferred_auth_method = 'magic';
        result = mapStateToProps(state, {});

        expect(result.isMagicAuth).toEqual(true);
    });
});
