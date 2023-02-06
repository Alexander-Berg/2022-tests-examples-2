import mapStateToProps from '../mapStateToProps';

import metrics from '../../../../metrics';
jest.mock('../../../../metrics', () => ({
    send: jest.fn()
}));

import {SHOW_LOGIN_FORM, CLICK_RESTORE_ACCESS_LINK} from '../../../metrics_constants';

describe('Components: LoginField.mapStateToProps', () => {
    it('should return valid props', () => {
        const state = {
            settings: {
                isNoTabletTouch: true,
                ua: {
                    BrowserName: 'Chrome'
                }
            },
            common: {
                restoreLoginUrl: 'restoreLoginUrl'
            },
            auth: {
                loginError: 'loginError',
                form: {
                    login: 'test'
                }
            }
        };

        const result = mapStateToProps(state);

        expect(result.isNoTabletTouch).toBe(true);
        expect(result.fieldError).toBe('_AUTH_.Errors.internal');
        expect(result.fieldLink.url).toBe('restoreLoginUrl');
        expect(result.fieldLink.text).toBe(i18n('_AUTH_.restore_id_link'));

        result.fieldLink.onClick();
        expect(metrics.send).toBeCalled();
        expect(metrics.send).toBeCalledWith([SHOW_LOGIN_FORM, CLICK_RESTORE_ACCESS_LINK]);
    });
});
