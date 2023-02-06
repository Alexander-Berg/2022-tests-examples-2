import checkIfFieldEmpty from '../methods/checkIfFieldEmpty';
import {updateStates, updateErrors} from '@blocks/actions/form';

jest.mock('@blocks/actions/form', () => ({
    updateStates: jest.fn(),
    updateErrors: jest.fn()
}));

const props = {
    dispatch: jest.fn()
};

describe('checkIfFieldEmpty', () => {
    const errorObj = {
        code: 'missingvalue',
        text: 'Необходимо ввести данные'
    };

    it('should return true if field is empty', () => {
        const result = checkIfFieldEmpty('', 'login')(props.dispatch, errorObj);

        expect(result).toBeTruthy();
    });

    it('should dispatch updateStates if field is empty', () => {
        checkIfFieldEmpty('', 'login')(props.dispatch, errorObj);
        expect(updateStates).toBeCalled();
    });

    it('should dispatch updateErrors if field is empty', () => {
        checkIfFieldEmpty('', 'login')(props.dispatch, errorObj);
        expect(updateErrors).toBeCalled();
    });

    it('should return false if field is filled', () => {
        const result = checkIfFieldEmpty('testlogin', 'login')(props.dispatch, errorObj);

        expect(result).toBeFalsy();
    });
});
