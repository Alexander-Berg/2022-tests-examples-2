import {updateValues, updateStates} from '@blocks/actions/form';
import {clearSuggestedLogins} from '@blocks/registration/actions';
import validateLogin from '@blocks/registration/methods/validateLogin';
import getSuggestedLogins from '@blocks/registration/methods/getSuggestedLogins';
import checkIfInvalid from '@blocks/registration/methods/checkIfInvalid';

import * as extracted from '../login_field.js';

jest.mock('react-dom', () => ({
    findDOMNode: () => ({
        querySelector: () => ({
            focus: () => {},
            click: () => {}
        })
    })
}));

jest.mock('@blocks/actions/form', () => ({
    updateValues: jest.fn(),
    updateStates: jest.fn()
}));

jest.mock('@blocks/registration/actions', () => ({
    clearSuggestedLogins: jest.fn()
}));

jest.mock('@blocks/registration/methods/validateLogin');
jest.mock('@blocks/registration/methods/getSuggestedLogins');
jest.mock('@blocks/registration/methods/checkIfInvalid');

jest.useFakeTimers();

describe('Registration.Mobile.Components.LoginField', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            state: {},
            props: {
                dispatch: jest.fn(),
                fieldValue: ''
            }
        };
        obj.setState = jest.fn((any) => {
            obj.state = Object.assign({}, obj.state, typeof any === 'function' ? any(obj.state) : any);
        });
    });
    afterEach(() => {
        updateStates.mockClear();
        updateValues.mockClear();
    });

    describe('clearAll', () => {
        beforeEach(() => {
            obj.handleValidation = {
                cancel: jest.fn()
            };
        });

        it('should call clearTimeout on loginFieldFocusTimeout', () => {
            const clearTimeout = jest.spyOn(global, 'clearTimeout');

            obj.loginFieldFocusTimeout = 1;
            extracted.clearAll.call(obj);
            expect(clearTimeout).toHaveBeenCalledTimes(1);
            expect(clearTimeout).toHaveBeenCalledWith(1);

            clearTimeout.mockReset();
        });
        it('should call clearTimeout on loginFieldFocusOutTimeout', () => {
            const clearTimeout = jest.spyOn(global, 'clearTimeout');

            obj.loginFieldFocusOutTimeout = 1;
            extracted.clearAll.call(obj);
            expect(clearTimeout).toHaveBeenCalledTimes(1);
            expect(clearTimeout).toHaveBeenCalledWith(1);

            clearTimeout.mockReset();
        });
        it('should call cancel of handleValidation', () => {
            extracted.clearAll.call(obj);
            expect(obj.handleValidation.cancel).toHaveBeenCalledTimes(1);
        });
    });

    describe('updateUserField', () => {
        it('should dispatch updateValues', () => {
            const fieldInfo = {
                field: 'field',
                value: 'value'
            };

            extracted.updateUserField.call(obj, fieldInfo.value, {name: fieldInfo.field});
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledWith(fieldInfo);
        });
    });

    describe('handleInput', () => {
        beforeEach(() => {
            clearSuggestedLogins.mockClear();
        });

        it('should dispatch updateStates and updateValues, and call handleValidation', () => {
            const value = 'value';
            const fieldInfo = {
                field: 'login',
                value
            };

            obj.handleValidation = jest.fn();
            extracted.handleInput.call(obj, {target: {value}});
            expect(updateStates).toHaveBeenCalledTimes(1);
            expect(updateStates).toHaveBeenCalledWith({field: 'login', status: 'not_valid'});
            expect(updateValues).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledWith(fieldInfo);
            expect(obj.handleValidation).toHaveBeenCalledTimes(1);
            expect(obj.handleValidation).toHaveBeenCalledWith(value);
        });
        it('should dispatch clearSuggestedLogins', () => {
            obj.handleValidation = () => {};
            extracted.handleInput.call(obj, '');
            expect(clearSuggestedLogins).toHaveBeenCalledTimes(1);
        });
    });

    describe('handleValidation', () => {
        it('should dispatch validateLogin', () => {
            const value = 'value';

            extracted.handleValidation.call(obj, value);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(validateLogin).toHaveBeenCalledTimes(1);
            expect(validateLogin).toHaveBeenCalledWith(value);
        });
    });

    describe('handleFocus', () => {
        it('should call self setState and dispatch checkIfInvalid', () => {
            extracted.handleFocus.call(obj);
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(checkIfInvalid).toHaveBeenCalledTimes(1);
            expect(checkIfInvalid).toHaveBeenCalledWith('login');
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.state.isActive).toBeTruthy();
            expect(obj.state.isValid).toBeFalsy();
        });
        it('should dispatch getSuggestedLogins', () => {
            obj.props.firstname = 'first';
            obj.props.lastname = 'last';
            extracted.handleFocus.call(obj);
            expect(getSuggestedLogins).toHaveBeenCalledTimes(1);
        });
    });

    describe('handleFocusout', () => {
        it('should call self setState and set self loginFieldFocusOutTimeout', () => {
            extracted.handleFocusout.call(obj);
            jest.runAllTimers();
            expect(obj.setState).toHaveBeenCalledTimes(1);
            expect(obj.setState).toHaveBeenCalledWith({
                isActive: false,
                isValid: false
            });
            expect(obj.loginFieldFocusOutTimeout).not.toBe(undefined);
        });
    });
});
