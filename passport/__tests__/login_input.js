import validateConnectLogin from '@blocks/registration/methods/validateConnectLogin';
import checkIfInvalid from '@blocks/registration/methods/checkIfInvalid';
import {updateStates, updateErrors, updateValues, updateErrorsValid} from '@blocks/actions/form';

import * as extracted from '../login_input.js';

jest.mock('@blocks/actions/form', () => ({
    updateStates: jest.fn(),
    updateErrors: jest.fn(),
    updateValues: jest.fn(),
    updateErrorsValid: jest.fn()
}));

jest.mock('@blocks/registration/methods/validateConnectLogin');
jest.mock('@blocks/registration/methods/checkIfInvalid');
jest.mock('lodash/debounce', () => (method) => method);

describe('Connect.LoginInput', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            state: {
                placeholderHidden: false
            },
            setState: jest.fn(),
            stopNumbers: {
                main: 0
            },
            props: {
                dispatch: jest.fn(),
                values: {
                    domain: ''
                },
                states: {},
                errors: {}
            }
        };
    });

    afterEach(() => {
        updateValues.mockClear();
        updateErrorsValid.mockClear();
        validateConnectLogin.mockClear();
        checkIfInvalid.mockClear();
    });
    describe('handleInput', () => {
        beforeEach(() => {
            obj.handleValidation = jest.fn();
        });

        it('should dispatch updateValues and updateErrorsValid, and call handleValidation', () => {
            const field = 'login';

            extracted.handleInput.call(obj, {target: {value: ''}});
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(updateValues).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledWith({field, value: ''});
            expect(updateErrorsValid).toHaveBeenCalledTimes(1);
            expect(updateErrorsValid).toHaveBeenCalledWith(field);
            expect(obj.handleValidation).toHaveBeenCalledTimes(1);
        });
        it('sohuld call setState', () => {
            obj.stopNumbers.main = 15;

            jest.useFakeTimers();
            extracted.handleInput.call(obj, {target: {value: 'asd'}});
            jest.runAllTimers();
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({placeholderHidden: true});
        });
        it('should call clearTimeout', () => {
            obj.timer = true;

            extracted.handleInput.call(obj, {target: {value: ''}});
            expect(clearTimeout).toHaveBeenCalledTimes(1);
            expect(clearTimeout).toHaveBeenCalledWith(true);
        });
        it('should call setState', () => {
            obj.state.placeholderHidden = true;

            extracted.handleInput.call(obj, {target: {value: ''}});
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({placeholderHidden: false});
        });
    });
    describe('handleValidation', () => {
        it('should call validateConnectLogin', () => {
            const value = 'value';

            obj.props.values.domain = 'domain';

            extracted.handleValidation.call(obj, value);
            expect(validateConnectLogin).toHaveBeenCalledTimes(1);
            expect(validateConnectLogin).toHaveBeenCalledWith(value);
        });
        it('should dispatch updateStates and updateErrors', () => {
            const field = 'login';

            extracted.handleValidation.call(obj, '');
            expect(obj.props.dispatch).toHaveBeenCalledTimes(2);
            expect(updateStates).toHaveBeenCalledTimes(1);
            expect(updateStates).toHaveBeenCalledWith({field, status: 'not_valid'});
            expect(updateErrors).toHaveBeenCalledTimes(1);
            expect(updateErrors).toHaveBeenCalledWith({
                field,
                error: {
                    code: 'login.no_domain',
                    text: i18n('Frontend.login.no_domain.error'),
                    descriptionText: i18n('Frontend.login.no_domain.desc')
                },
                active: true
            });
        });
    });
    describe('handleFocus', () => {
        it('should call setState and dispatch checkIfInvalid', () => {
            extracted.handleFocus.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                focused: true
            });
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(checkIfInvalid).toHaveBeenCalledTimes(1);
            expect(checkIfInvalid).toHaveBeenCalledWith('login');
        });
    });
    describe('construct', () => {
        test('if desktop', () => {
            extracted.construct.call(obj, obj.props);
            expect(obj.stopNumbers.main).toBe(0);
        });
        test('if mobile', () => {
            obj.props.isMobile = true;

            extracted.construct.call(obj, obj.props);
            expect(obj.stopNumbers.main).toBe(2);
        });
    });
    describe('shouldComponentUpdate', () => {
        it('should always return true', () => {
            const nextProps = {
                states: {},
                values: {},
                errors: {
                    login: {}
                }
            };
            const errors = obj.props.errors;
            const states = obj.props.states;
            const values = obj.props.values;

            expect(extracted.shouldComponentUpdate.call(obj, {}, {focused: true})).toBeTruthy();

            errors.login = {code: 1};
            expect(extracted.shouldComponentUpdate.call(obj, nextProps, {})).toBeTruthy();
            nextProps.errors.login = errors.login;

            states.login = 'login';
            expect(extracted.shouldComponentUpdate.call(obj, nextProps, {})).toBeTruthy();
            delete states.login;

            states.domain = 'domain';
            expect(extracted.shouldComponentUpdate.call(obj, nextProps, {})).toBeTruthy();
            delete states.domain;

            values.login = 'login';
            expect(extracted.shouldComponentUpdate.call(obj, nextProps, {})).toBeTruthy();
            delete values.login;

            values.domain = 'domain';
            expect(extracted.shouldComponentUpdate.call(obj, nextProps, {})).toBeTruthy();
            delete values.domain;

            errors.active = 'login';
            expect(extracted.shouldComponentUpdate.call(obj, nextProps, {})).toBeTruthy();
            delete errors.active;

            errors.hintActive = true;
            expect(extracted.shouldComponentUpdate.call(obj, nextProps, {})).toBeTruthy();
        });
    });
    describe('onBlur', () => {
        it('should call setState', () => {
            extracted.onBlur.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                focused: false
            });
        });
    });
    describe('getDomainLength', () => {
        it('should return 4', () => {
            expect(extracted.getDomainLength.call(obj)).toBe(4);
        });
        it('should return 12', () => {
            obj.props.states.domain = 'valid';
            obj.props.values.domain = 'domaindomain';

            expect(extracted.getDomainLength.call(obj)).toBe(12);
        });
        it('should return 4', () => {
            obj.props.states.domain = 'valid';
            obj.props.values.domain = 'd';

            expect(extracted.getDomainLength.call(obj)).toBe(4);
        });
        it('should return 6', () => {
            obj.props.states.domain = 'valid';
            obj.props.values.domain = 'domain';

            expect(extracted.getDomainLength.call(obj)).toBe(6);
        });
    });
    describe('isValueTooLong', () => {
        it('should return true', () => {
            obj.stopNumbers.main = 15;

            expect(extracted.isValueTooLong.call(obj, 'domain')).toBeTruthy();
        });
        it('should return false', () => {
            expect(extracted.isValueTooLong.call(obj, 'domain')).toBeFalsy();
        });
    });
});
