import checkIfInvalid from '@blocks/registration/methods/checkIfInvalid';
import {updateValues, updateErrorsValid, updateStates, updateErrors} from '@blocks/actions/form';

import * as extracted from '../current_password.js';

jest.mock('@blocks/registration/methods/checkIfInvalid');

jest.mock('@blocks/actions/form', () => ({
    updateValues: jest.fn(),
    updateErrorsValid: jest.fn(),
    updateStates: jest.fn(),
    updateErrors: jest.fn()
}));

describe('Complete.CurrentPassword', () => {
    let obj = null;

    beforeEach(() => {
        obj = {
            setState: jest.fn((any) => (typeof any === 'function' ? any({}) : any)),
            state: {},
            props: {
                dispatch: jest.fn(),
                state: 'valid'
            }
        };
        checkIfInvalid.mockImplementation(() => () => jest.fn());
    });

    afterEach(() => {
        checkIfInvalid.mockClear();
        updateValues.mockClear();
        updateStates.mockClear();
        updateErrors.mockClear();
        updateErrorsValid.mockClear();
    });

    describe('checkIfInvalid', () => {
        it('should dispatch checkIfValid', () => {
            extracted.checkIfInvalidHandler.call(obj);

            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(checkIfInvalid).toHaveBeenCalledTimes(1);
            expect(checkIfInvalid).toHaveBeenCalledWith('password');
        });
    });

    describe('updateAndCheck', () => {
        it('should dispatch updateValues, updateStates and updateErrors (remove)', () => {
            const value = '';
            const field = 'password';
            const status = 'not_valid';
            const error = {
                code: 'missingvalue',
                text: '_AUTH_.password_current_errors_missingvalue'
            };

            extracted.updateAndCheck.call(obj, {target: {value}});
            expect(obj.props.dispatch).toHaveBeenCalledTimes(3);
            expect(updateValues).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledWith({field, value});
            expect(updateStates).toHaveBeenCalledTimes(1);
            expect(updateStates).toHaveBeenCalledWith({field, status});
            expect(updateErrors).toHaveBeenCalledTimes(1);
            expect(updateErrors).toHaveBeenCalledWith({field, error, errorDescription: '', active: true});
        });

        it('should dispatch updateValues, updateStates and updateErrors (set)', () => {
            const value = 'value';
            const field = 'password';
            const status = 'valid';

            obj.props.state = 'not_valid';

            extracted.updateAndCheck.call(obj, {target: {value}});
            expect(obj.props.dispatch).toHaveBeenCalledTimes(3);
            expect(updateValues).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledWith({field, value});
            expect(updateStates).toHaveBeenCalledTimes(1);
            expect(updateStates).toHaveBeenCalledWith({field, status});
            expect(updateErrorsValid).toHaveBeenCalledTimes(1);
            expect(updateErrorsValid).toHaveBeenCalledWith(field);
        });

        it('should dispatch updateValues', () => {
            const value = 'value';
            const field = 'password';

            extracted.updateAndCheck.call(obj, {target: {value}});
            expect(obj.props.dispatch).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledTimes(1);
            expect(updateValues).toHaveBeenCalledWith({field, value});
        });
    });

    describe('toggleFieldType', () => {
        it('should call setState', () => {
            extracted.toggleFieldType.call(obj);
            expect(obj.setState).toHaveBeenCalledTimes(1);
        });
    });
});
