import {push} from 'react-router-redux';

import api from '@blocks/api';
import reloadCaptcha from '@components/Captcha/actions/reloadCaptcha';
import {setAppPasswordsNumber} from '@blocks/morda/app_passwords/actions';

import * as extracted from '../password.js';

jest.mock('@blocks/metrics', () => ({
    send: jest.fn()
}));
jest.mock('@blocks/api', () => {
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
jest.mock('react-dom', () => ({
    findDOMNode: () => ({
        querySelector: () => ({
            focus: jest.fn(),
            click: jest.fn()
        })
    })
}));
jest.mock('@components/Captcha/actions/reloadCaptcha');
jest.mock('react-router-redux', () => ({
    push: jest.fn()
}));
jest.mock('@blocks/morda/app_passwords/actions', () => ({
    setAppPasswordsNumber: jest.fn()
}));

describe('Morda.Forms.Password', () => {
    const getState = () => ({
        common: {
            retpath: '',
            isPDD: false,
            origin: 'origin',
            csrf: 'csrf',
            track_id: 'track_id'
        },
        person: {}
    });

    let obj = null;

    beforeEach(() => {
        obj = {
            inputFields: {},
            data: {
                revoke_app_passwords: false,
                revoke_tokens: false,
                revoke_web_sessions: false,
                tokens: [1, 2],
                passTokens: [],
                otherTokens: [3, 4, 5]
            },
            state: {
                showCheckList: false,
                revokers: {
                    loading: true
                },
                currentPassword: '',
                newPassword: '',
                repeatPassword: '',
                captcha: '',
                errors: {},
                passwordStrength: {
                    value: -1,
                    code: ''
                },
                loading: false,
                showPasswordTips: false,
                showPassword: false
            },
            props: {
                dispatch: jest.fn(),
                captcha: {
                    key: 'key'
                }
            }
        };
        obj.setState = jest.fn((any) => {
            obj.state = Object.assign({}, obj.state, typeof any === 'function' ? any(obj.state) : any);
        });
    });
    afterEach(() => {
        reloadCaptcha.mockClear();
    });

    describe('getError', () => {
        it('should return "empty"', () => {
            expect(extracted.getError.call(obj, '', '')).toBe('empty');
        });
        it('should return "not_matched"', () => {
            expect(extracted.getError.call(obj, 'repeatPassword', 'a', 'b')).toBe('not_matched');
        });
        it('should return false', () => {
            expect(extracted.getError.call(obj, '', 'a')).toBe(false);
        });
    });

    describe('getErrors', () => {
        it('should return same state', () => {
            expect(extracted.getErrors.call(obj, 'currentPassword', 'a')).toBe(obj.state.errors);
            obj.state.errors.currentPassword = 'empty';
            expect(extracted.getErrors.call(obj, 'currentPassword', '')).toBe(obj.state.errors);
        });
        it('should add error', () => {
            const errors = extracted.getErrors.call(obj, 'currentPassword', '');

            expect(errors.currentPassword).toBe('empty');
        });
        it('should remove error', () => {
            obj.state.errors.currentPassword = 'empty';

            const errors = extracted.getErrors.call(obj, 'currentPassword', 'a');

            expect(errors.currentPassword).toBe(undefined);
        });
    });

    describe('changeText', () => {
        it('should set currentPassword state', () => {
            extracted.changeText.call(obj, {name: 'currentPassword', text: 'text'});
            expect(obj.state.currentPassword).toBe('text');
        });
        it('should set error state', () => {
            extracted.changeText.call(obj, {name: 'repeatPassword', text: 'text'});
            expect(obj.state.errors.repeatPassword).toBe('not_matched');
            delete obj.state.errors.repeatPassword;
            extracted.changeText.call(obj, {name: 'newPassword', text: 'text2'});
            expect(obj.state.errors.repeatPassword).toBe('not_matched');
        });
        it('should remove error from state', () => {
            obj.state.repeatPassword = 'pass';
            obj.state.errors.repeatPassword = 'not_matched';

            extracted.changeText.call(obj, {name: 'newPassword', text: obj.state.repeatPassword});
            expect(obj.state.errors.repeatPassword).toBe(undefined);
        });
    });

    describe('checkForErrors', () => {
        it('should return object with 4 keys', () => {
            expect(Object.keys(extracted.checkForErrors.call(obj)).length).toBe(4);
        });
        it('should return empty object', () => {
            obj.state.currentPassword = 'a';
            obj.state.newPassword = 'a';
            obj.state.repeatPassword = 'a';
            obj.state.captcha = 'a';
            expect(Object.keys(extracted.checkForErrors.call(obj)).length).toBe(0);
        });
    });

    describe('submitPassword', () => {
        const dispatch = jest.fn();

        beforeEach(() => {
            obj.state.currentPassword = 'a';
            obj.state.newPassword = 'a';
            obj.state.repeatPassword = 'a';
            obj.state.captcha = 'a';
            obj.state.passwordStrength.value = 1;
        });
        afterEach(() => {
            dispatch.mockClear();
        });

        test('path and options', () => {
            const {
                common: {retpath, isPDD, origin, csrf, track_id}
            } = getState();
            const {
                captcha: {key: captchaKey}
            } = obj.props;
            const {captcha, currentPassword, newPassword} = obj.state;

            extracted.submitPassword.call(obj)(dispatch, getState);
            expect(api.path).toBe('/profile/password/submit');
            expect(api.options).toEqual({
                retpath,
                is_pdd: isPDD,
                origin,
                csrf,
                track_id,
                captcha,
                captcha_key: captchaKey,
                csrf_token: csrf,
                current_password: currentPassword,
                password: newPassword,
                lang: obj.props.language,
                revoke_web_sessions: obj.data.revoke_web_sessions,
                revoke_tokens: obj.data.revoke_tokens,
                revoke_app_passwords: obj.data.revoke_app_passwords
            });
        });
        it('should set errors state', () => {
            obj.inputFields.captcha = {
                focus: jest.fn()
            };
            obj.state.captcha = '';
            extracted.submitPassword.call(obj)(dispatch, getState);
            expect(obj.state.errors).toEqual({captcha: 'empty'});
        });
        it('should not call any setState', () => {
            obj.state.passwordStrength.value = -1;
            extracted.submitPassword.call(obj)(dispatch, getState);
            expect(obj.setState).toHaveBeenCalledTimes(1);
        });
        it('should always set loading state to true, if not error', () => {
            extracted.submitPassword.call(obj)(dispatch, getState);
            expect(obj.state.loading).toBe(true);
        });
        it('should call revokeTokens', () => {
            const revokeTokens = jest.fn();

            extracted.submitPassword.call(obj, revokeTokens)(dispatch, getState);
            api.onDone();
            expect(revokeTokens).toHaveBeenCalledTimes(1);
            expect(revokeTokens).toHaveBeenCalledWith(getState().common.retpath);
        });
        it('should set error state and dispatch reloadCaptcha', () => {
            extracted.submitPassword.call(obj)(dispatch, getState);
            api.onFail({errors: ['password.equals_previous', 'captcha.required', 'password.empty']});
            expect(obj.setState).toHaveBeenCalledTimes(2);
            expect(obj.setState.mock.calls[1][0]).toEqual({
                loading: false,
                captcha: '',
                errors: obj.state.errors
            });
            expect(obj.state.errors).toEqual({
                newPassword: 'equals_previous',
                currentPassword: 'empty'
            });
            expect(dispatch).toHaveBeenCalledTimes(1);
            expect(reloadCaptcha).toHaveBeenCalledTimes(1);
        });
    });

    describe('setInputField', () => {
        it('should set field', () => {
            extracted.setInputField.call(obj, true, 'name');
            expect(obj.inputFields.name).not.toBe(undefined);
        });
        it('should remove field', () => {
            obj.inputFields.name = true;
            extracted.setInputField.call(obj, undefined, 'name');
            expect(obj.inputFields.name).toBe(undefined);
        });
    });

    describe('revokeTokens', () => {
        test('path and options', () => {
            extracted.revokeTokens.call(obj);
            expect(api.path).toBe('/profile/password/revoke');
            expect(api.options).toEqual({
                lang: obj.props.language,
                tokens: obj.data.tokens.join(','),
                passTokens: obj.data.passTokens.join(','),
                otherYandexTokens: '',
                otherTokens: ''
            });
        });
        it('should dispatch push', () => {
            extracted.revokeTokens.call(obj);
            api.onDone();
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledTimes(1);
            expect(push).toHaveBeenCalledWith('/profile');
        });
        it('should call closeModal', () => {
            obj.props.closeModal = jest.fn();
            extracted.revokeTokens.call(obj);
            api.onDone();
            expect(obj.props.closeModal).toHaveBeenCalledTimes(1);
        });
        it('should dispatch setAppPasswordsNumber', () => {
            obj.state.revokers.passTokens = [1, 2, 3];
            obj.data.passTokens = [1, 2];
            obj.props.closeModal = () => {};
            extracted.revokeTokens.call(obj);
            api.onDone({
                status: 'ok',
                failed: {
                    passwords: 1
                }
            });
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(setAppPasswordsNumber).toHaveBeenCalledTimes(1);
            expect(setAppPasswordsNumber).toHaveBeenCalledWith(2);
        });
    });

    describe('toggleShowPassword', () => {
        it('should toggle showPassword state', () => {
            const showPassword = obj.state.showPassword;

            extracted.toggleShowPassword.call(obj);
            expect(obj.state.showPassword).toBe(!showPassword);
        });
    });

    describe('getPasswordStrength', () => {
        beforeEach(() => {
            obj.props.dispatch = jest.fn((f) => f(null, getState));
        });

        test('path and options', () => {
            const {
                common: {track_id, uid},
                person: {login}
            } = getState();
            const password = 'password';

            extracted.getPasswordStrength.call(obj, password);
            expect(api.path).toBe('password');
            expect(api.options).toEqual({password, track_id, uid, login});
        });
        it('should not call dispatch', () => {
            extracted.getPasswordStrength.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(0);
        });
        it('should change passwordLineLastUpdate', () => {
            const passwordLineLastUpdate = obj.passwordLineLastUpdate;

            extracted.getPasswordStrength.call(obj, 'pass');
            api.onDone({});
            expect(obj.passwordLineLastUpdate).not.toBe(passwordLineLastUpdate);
        });
        it('should set value to -1', () => {
            const code = 'code';

            extracted.getPasswordStrength.call(obj, 'pass');
            api.onDone({validation_errors: [{code}]});
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                passwordStrength: {
                    value: -1,
                    code
                }
            });
            expect(obj.state.passwordStrength.value).toBe(-1);
        });
        it('should set value to 0', () => {
            const code = 'code';

            extracted.getPasswordStrength.call(obj, 'pass');
            api.onDone({validation_warnings: [{code}]});
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                passwordStrength: {
                    value: 0,
                    code
                }
            });
            expect(obj.state.passwordStrength.value).toBe(0);
        });
        it('should set value to 1', () => {
            extracted.getPasswordStrength.call(obj, 'pass');
            api.onDone({});
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                passwordStrength: {
                    value: 1,
                    code: 'strong'
                }
            });
            expect(obj.state.passwordStrength.value).toBe(1);
        });
    });

    describe('getRevokers', () => {
        test('path and options', () => {
            const {
                common: {retpath, isPDD, track_id: trackID}
            } = getState();

            extracted.getRevokers.call(obj)(null, getState);
            expect(api.path).toBe('/profile/password/revokers');
            expect(api.options).toEqual({
                is_pdd: isPDD,
                track_id: trackID,
                retpath,
                lang: obj.props.language
            });
        });
        it('should set revokers error', () => {
            const revokers = {state: 'state'};

            extracted.getRevokers.call(obj)(null, getState);
            api.onDone(revokers);
            expect(obj.state.revokers).toEqual({error: revokers.state});
            api.onDone();
            expect(obj.state.revokers).toEqual({error: 'exception.unhandled'});
        });
        it('should set revokers state and self data', () => {
            const revokers = {
                default: {
                    revoke_tokens: 'tokens'
                },
                otherTokens: [{token: 1}],
                tokens: [{token: 1}]
            };

            extracted.getRevokers.call(obj)(null, getState);
            api.onDone({revokers});
            expect(obj.state.revokers).toEqual(
                Object.assign({}, revokers, {
                    passTokens: []
                })
            );
            expect(obj.data).toEqual(
                Object.assign({}, obj.data, {
                    revoke_tokens: revokers.default.revoke_tokens,
                    otherTokens: extracted.reduceTokens(revokers.otherTokens),
                    tokens: extracted.reduceTokens(revokers.tokens),
                    passTokens: []
                })
            );
        });
        it('should set revokers with error state', () => {
            const exception = 'exception';

            extracted.getRevokers.call(obj)(null, getState);
            api.onFail({});
            expect(obj.state.revokers).toEqual({
                error: 'exception.unhandled'
            });
            api.onFail({errors: [exception]});
            expect(obj.state.revokers).toEqual({
                error: exception
            });
        });
    });

    describe('checkForNumbersOrSpecialSymbols', () => {
        it('should return false', () => {
            expect(extracted.checkForNumbersOrSpecialSymbols('asdf')).toBe(false);
        });
        it('should return true', () => {
            expect(extracted.checkForNumbersOrSpecialSymbols('0\':"')).toBe(true);
        });
    });

    describe('onFormSubmit', () => {
        it('should call preventDefault of event and dispatch something', () => {
            const preventDefault = jest.fn();

            extracted.onFormSubmit.call(obj, {preventDefault});
            expect(preventDefault).toHaveBeenCalledTimes(1);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
        });
    });

    describe('onFieldFocus', () => {
        it('should set activeField', () => {
            const target = {name: 'repeatPassword'};

            extracted.onFieldFocus.call(obj, {target});
            expect(obj.activeField).toBe(target.name);
        });
        it('should set showPasswordTips state to true', () => {
            const target = {name: 'newPassword'};

            extracted.onFieldFocus.call(obj, {target});
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({showPasswordTips: true});
        });
    });

    describe('onTextChange', () => {
        it('should not dispatch anything', () => {
            extracted.onTextChange.call(obj, {target: {value: '', name: ''}});
            expect(obj.props.dispatch).toHaveBeenCalledTimes(0);
        });
        it('should call self getPasswordStrength', () => {
            obj.getPasswordStrength = jest.fn();
            extracted.onTextChange.call(obj, {target: {value: 'pass', name: 'newPassword'}});
            expect(obj.getPasswordStrength).toHaveBeenCalledTimes(1);
            expect(obj.getPasswordStrength).toHaveBeenCalledWith('pass');
        });
    });

    describe('findError', () => {
        it('should return "captcha"', () => {
            obj.state.errors.captcha = 'empty';
            expect(extracted.findError(obj.state.errors)).toBe('captcha');
        });
        it('should return null', () => {
            expect(extracted.findError(obj.state.errors)).toBe(null);
        });
    });

    describe('setActiveError', () => {
        it('should not change activeError', () => {
            const activeError = obj.activeError;

            extracted.setActiveError.call(obj, obj.state.errors);
            expect(obj.activeError).toBe(activeError);
        });
        it('should set activeError to null', () => {
            extracted.setActiveError.call(obj, {});
            expect(obj.activeError).toBe(null);
        });
        it('should set activeError to "captcha"', () => {
            obj.activeField = 'captcha';
            extracted.setActiveError.call(obj, {captcha: 'empty'});
            expect(obj.activeError).toBe('captcha');
        });
        it('should set activeError to "currentPassword"', () => {
            extracted.setActiveError.call(obj, {currentPassword: 'empty', captcha: 'empty'});
            expect(obj.activeError).toBe('currentPassword');
        });
    });

    describe('getNamesByTokens', () => {
        it('should return string with tokens', () => {
            const tokens = [345, 456];

            obj.state.revokers = {
                key: [
                    {token: 123, title: 'a'},
                    {token: 123, title: 'b'},
                    {token: tokens[0], title: 'c'},
                    {token: tokens[1], title: 'd'}
                ]
            };
            expect(extracted.getNamesByTokens.call(obj, 'key', tokens)).toBe('«a», «b»');
        });
    });

    describe('reduce', () => {
        it('should return array with tokens', () => {
            const arr = [{token: 1}, {token: 2}];

            expect(extracted.reduceTokens(arr)).toEqual([1, 2]);
        });
    });
});
