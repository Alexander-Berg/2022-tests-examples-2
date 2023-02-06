import mapStateToProps from '../mapStateToProps';
import {
    SHOW_PASSWORD_FORM,
    SHOW_SOCIAL_WITH_PASSWORD_FORM,
    CLICK_RESTORE_ACCESS_LINK
} from '../../../metrics_constants';
import metrics from '../../../../metrics';

jest.mock('../../../../metrics', () => ({
    send: jest.fn()
}));

describe('Components: PasswordField.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            auth: {
                passwordError: 'passwordError',
                inputLogins: {
                    123: {
                        uid: 123
                    }
                },
                processedAccount: {
                    uid: 123
                },
                form: {
                    login: 'formLogin',
                    password: 'password'
                }
            },
            common: {
                restoration_url: 'restorationUrl?login=login',
                experiments: {
                    flags: []
                }
            }
        };

        const ownProps = {
            hasSocialButton: true
        };

        let result = mapStateToProps(state, ownProps);

        expect(result.fieldError).toBe('_AUTH_.Errors.internal');
        expect(result.fieldLink.url).toBe('restorationUrl?login=formLogin');
        expect(result.fieldLink.text).toBe(i18n('_AUTH_.restore_access'));

        result.fieldLink.onClick();
        expect(metrics.send).toBeCalled();
        expect(metrics.send).toBeCalledWith([SHOW_SOCIAL_WITH_PASSWORD_FORM, CLICK_RESTORE_ACCESS_LINK]);

        ownProps.hasSocialButton = false;
        state.auth.form.login = null;
        result = mapStateToProps(state, ownProps);
        expect(result.fieldLink.url).toBe('restorationUrl?');

        result.fieldLink.onClick();
        expect(metrics.send).toBeCalled();
        expect(metrics.send).toBeCalledWith([SHOW_PASSWORD_FORM, CLICK_RESTORE_ACCESS_LINK]);

        state.auth.inputLogins = {};
        result = mapStateToProps(state, ownProps);
        expect(result.inputLogin).toEqual(null);

        state.auth.passwordError = null;
        result = mapStateToProps(state, ownProps);
        expect(result.fieldLink.text).toEqual(i18n('_AUTH_.remind_password'));

        state.common.isWebView = true;
        result = mapStateToProps(state, ownProps);
        expect(result.isShowFieldLink).toBe(false);

        state.am = {isAm: true};
        result = mapStateToProps(state, ownProps);
        expect(result.isShowFieldLink).toBe(true);
    });
});
