import api from '../../../api';
import {saveActionForRepeat, setEditMode} from '../../../common/actions';
import passport from '@plibs/pclientjs/js/passport';

import * as actions from '../actions';

jest.mock('../../../api', () => {
    class Request {
        request(path, opts) {
            this.path = path;
            this.options = opts;
            return this;
        }
        done(func) {
            this.onDone = func;
            return this;
        }
        fail(func) {
            this.onFail = func;
            return this;
        }
        always(func) {
            this.onAlways = func;
            return this;
        }
    }

    return new Request();
});

jest.mock('../../../utils', () => ({
    isThirdPartyUrl: jest.fn((retpath) => retpath === 'xxx')
}));

jest.mock('../../../common/actions', () => ({
    saveActionForRepeat: jest.fn(),
    setEditMode: jest.fn()
}));

jest.mock('@plibs/pclientjs/js/passport', () => ({
    basePath: 'basePath'
}));

describe('Morda.Emails.actions', () => {
    const getState = () => ({
        emails: {
            states: []
        },
        person: {
            havePassword: true
        },
        common: {
            csrf: 'value',
            retpath: 'xxx'
        },
        settings: {
            language: 'ru'
        }
    });
    const dispatch = jest.fn();

    afterEach(() => {
        dispatch.mockClear();
        setEditMode.mockClear();
        saveActionForRepeat.mockClear();
    });

    test('toggleAliasesList', () => {
        expect(actions.toggleAliasesList()).toEqual({
            type: actions.TOGGLE_ALIASES_LIST
        });
    });
    test('toggleEmailSelection', () => {
        const email = 'value';

        expect(actions.toggleEmailSelection(email)).toEqual({
            type: actions.TOGGLE_EMAIL_SELECTION,
            email
        });
    });
    test('showDeleteRequestPopup', () => {
        const email = 'value';

        expect(actions.showDeleteRequestPopup(email)).toEqual({
            type: actions.SHOW_EMAIL_DELETE_REQUEST_POPUP,
            email
        });
    });
    test('setError', () => {
        const error = 'value';

        expect(actions.setError(error)).toEqual({
            type: actions.SET_EMAIL_ERROR,
            error
        });
    });
    describe('changeEmailsState', () => {
        it('should dispatch setEditMode', () => {
            const state = getState();

            actions.changeEmailsState(actions.EMAILS_STATES.root)(dispatch, () =>
                Object.assign({}, state, {
                    emails: Object.assign({}, state.emails, {
                        states: [actions.EMAILS_STATES.add]
                    })
                })
            );
            expect(dispatch).toHaveBeenCalledTimes(1);
            expect(setEditMode).toHaveBeenCalledWith(null);
        });
        it('should dispatch setEditMode', () => {
            const emailState = 'value';

            actions.changeEmailsState(emailState)(dispatch, getState);
            expect(dispatch).toHaveBeenCalledTimes(1);
            expect(dispatch).toHaveBeenCalledWith({
                type: actions.CHANGE_EMAILS_STATE,
                state: emailState
            });
        });
    });
    describe('changeEmail', () => {
        const email = 'value';

        test('api params', () => {
            actions.changeEmail(email)(dispatch, getState);
            expect(api.path).toBe('email/delete');
            expect(api.options).toEqual({email, csrf_token: getState().common.csrf});
        });
        test('success', () => {
            actions.changeEmail(email)(dispatch, getState);
            api.onDone();
            expect(dispatch).toHaveBeenCalledTimes(4);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.DELETE_EMAIL
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.DELETE_EMAIL_SUCCESS,
                email
            });
            expect(dispatch.mock.calls[3][0]).toEqual({
                type: actions.CHANGE_EMAILS_STATE,
                state: actions.EMAILS_STATES.root
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
        test('fail', () => {
            const error = {
                errors: []
            };

            actions.changeEmail(email)(dispatch, getState);
            api.onFail(error);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.DELETE_EMAIL
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.DELETE_EMAIL_ERROR,
                errors: error.errors
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
    });
    describe('getEmails', () => {
        test('api params', () => {
            actions.getEmails()(dispatch, getState);
            expect(api.path).toBe('email/list');
            expect(api.options).toEqual({csrf_token: getState().common.csrf});
        });
        test('success', () => {
            const result = {
                emails: []
            };

            actions.getEmails()(dispatch, getState);
            api.onDone(result);
            expect(dispatch).toHaveBeenCalledTimes(2);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.GET_EMAILS
            });
            expect(dispatch.mock.calls[1][0]).toEqual({
                type: actions.GET_EMAILS_SUCCESS,
                emails: result.emails
            });
        });
        test('fail', () => {
            const error = {
                errors: []
            };

            actions.getEmails()(dispatch, getState);
            api.onFail(error);
            expect(dispatch).toHaveBeenCalledTimes(2);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.GET_EMAILS
            });
            expect(dispatch.mock.calls[1][0]).toEqual({
                type: actions.GET_EMAILS_ERROR,
                errors: error.errors
            });
        });
    });
    describe('addEmail', () => {
        const email = 'value';

        test('api params', () => {
            actions.addEmail(email)(dispatch, getState);
            expect(api.path).toBe('email/send-confirmation-email');
            expect(api.options).toEqual({
                csrf_token: getState().common.csrf,
                email,
                is_safe: true,
                retpath: 'xxx',
                validator_ui_url: `https://${location.hostname}${passport.basePath}email/confirm-by-link`,
                language: getState().settings.language
            });
        });
        test('success', () => {
            const result = {
                emails: []
            };
            const state = getState();

            actions.addEmail(email)(dispatch, () =>
                Object.assign({}, state, {
                    common: Object.assign({}, state.common, {
                        retpath: 'value'
                    })
                })
            );
            api.onDone(result);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.SEND_CONFIRMATION_EMAIL
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.SEND_CONFIRMATION_EMAIL_SUCCESS,
                emails: result.emails,
                email
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
        test('fail', () => {
            const error = {
                errors: []
            };
            const state = getState();

            actions.addEmail(email)(dispatch, () =>
                Object.assign({}, state, {
                    common: Object.assign({}, state.common, {
                        retpath: null
                    })
                })
            );
            api.onFail(error);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.SEND_CONFIRMATION_EMAIL
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.SEND_CONFIRMATION_EMAIL_ERROR,
                errors: error.errors
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
    });
    describe('deleteEmail', () => {
        const email = 'value';

        test('api params', () => {
            actions.deleteEmail(email)(dispatch, getState);
            expect(api.path).toBe('email/delete');
            expect(api.options).toEqual({email, csrf_token: getState().common.csrf});
        });
        test('success', () => {
            actions.deleteEmail(email)(dispatch, getState);
            api.onDone();
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.DELETE_EMAIL
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.DELETE_EMAIL_SUCCESS,
                email
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
        test('fail', () => {
            const error = {
                errors: []
            };

            actions.deleteEmail(email)(dispatch, getState);
            api.onFail(error);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.DELETE_EMAIL
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.DELETE_EMAIL_ERROR,
                email,
                errors: error.errors
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
        it('should dispatch showDeleteRequestPopup', () => {
            const error = {
                errors: ['password.required']
            };

            actions.deleteEmail(email)(dispatch, getState);
            api.onFail(error);
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.SHOW_EMAIL_DELETE_REQUEST_POPUP,
                email: null
            });
        });
    });
    describe('setSafeEmail', () => {
        const email = 'value';

        test('api params', () => {
            actions.setSafeEmail(email)(dispatch, getState);
            expect(api.path).toBe('email/setup-confirmed');
            expect(api.options).toEqual({email, csrf_token: getState().common.csrf, is_safe: true});
        });
        test('success', () => {
            const result = {
                emails: []
            };

            actions.setSafeEmail(email)(dispatch, getState);
            api.onDone(result);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.EMAIL_SET_SAFE
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.EMAIL_SET_SAFE_SUCCESS,
                emails: result.emails
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
        test('fail', () => {
            const error = {
                errors: []
            };

            actions.setSafeEmail(email)(dispatch, getState);
            api.onFail(error);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.EMAIL_SET_SAFE
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.EMAIL_SET_SAFE_ERROR,
                errors: error.errors
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
    });
    describe('confirmEmail', () => {
        const code = 'value';

        test('api params', () => {
            actions.confirmEmail(code)(dispatch, getState);
            expect(api.path).toBe('email/confirm-by-code');
            expect(api.options).toEqual({csrf_token: getState().common.csrf, key: code});
        });
        test('success', () => {
            const result = {
                emails: []
            };

            actions.confirmEmail(code)(dispatch, getState);
            api.onDone(result);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.CONFIRM_EMAIL_BY_CODE
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.CONFIRM_EMAIL_BY_CODE_SUCCESS,
                emails: result.emails
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(code);
        });
        test('fail', () => {
            const error = {
                errors: []
            };

            actions.confirmEmail(code)(dispatch, getState);
            api.onFail(error);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.CONFIRM_EMAIL_BY_CODE
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.CONFIRM_EMAIL_BY_CODE_ERROR,
                errors: error.errors
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(code);
        });
    });
    describe('resendCode', () => {
        const email = 'value';

        test('api params', () => {
            actions.resendCode(email)(dispatch, getState);
            expect(api.path).toBe('email/send-confirmation-email');
            expect(api.options).toEqual({
                csrf_token: getState().common.csrf,
                email,
                is_safe: true,
                retpath: `https://${location.hostname}xxx`,
                // eslint-disable-next-line compat/compat
                validator_ui_url: `${location.origin}${passport.basePath}email/confirm-by-link`,
                language: getState().settings.language
            });
        });
        test('success', () => {
            const result = {
                emails: []
            };
            const state = getState();

            actions.resendCode(email)(dispatch, () =>
                Object.assign({}, state, {
                    common: Object.assign({}, state.common, {
                        retpath: 'https://retpath'
                    })
                })
            );
            api.onDone(result);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.RESEND_CONFIRMATION_EMAIL
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.RESEND_CONFIRMATION_EMAIL_SUCCESS
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
        test('fail', () => {
            const error = {
                errors: []
            };
            const state = getState();

            actions.resendCode(email)(dispatch, () =>
                Object.assign({}, state, {
                    common: Object.assign({}, state.common, {
                        retpath: null
                    })
                })
            );
            api.onFail(error);
            expect(dispatch).toHaveBeenCalledTimes(3);
            expect(dispatch.mock.calls[0][0]).toEqual({
                type: actions.RESEND_CONFIRMATION_EMAIL
            });
            expect(dispatch.mock.calls[2][0]).toEqual({
                type: actions.RESEND_CONFIRMATION_EMAIL_ERROR,
                errors: error.errors
            });
            expect(saveActionForRepeat).toHaveBeenCalledTimes(1);
            expect(saveActionForRepeat.mock.calls[0][1]).toBe(email);
        });
    });
});
