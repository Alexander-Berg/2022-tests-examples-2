import mockData from './__mocks__/data';
import updateFieldStatus from '../methods/updateFieldStatus';
import checkIfFieldEmpty from '../methods/checkIfFieldEmpty';
import findFieldsWithErrors from '../methods/findFieldsWithErrors';
import validatePasswordConfirm from '../methods/validatePasswordConfirm';

jest.mock('../methods/updateFieldStatus');
jest.mock('../methods/findFieldsWithErrors');
jest.mock('../methods/checkIfFieldEmpty');

describe('validatePasswordConfirm', () => {
    checkIfFieldEmpty.mockImplementation(() => () => false);
    updateFieldStatus.mockImplementation(() => () => ({field: 'password_confirm'}));
    findFieldsWithErrors.mockImplementation(() => () => jest.fn());

    it('should check if field empty', () => {
        validatePasswordConfirm('testpass', 'testpass')(mockData.props.dispatch, mockData.getState);
        expect(checkIfFieldEmpty).toBeCalled();
    });

    it('should call updateFieldStatus with arg "valid" if confirm equals password', () => {
        validatePasswordConfirm('testpass', 'testpass')(mockData.props.dispatch, mockData.getState);
        expect(updateFieldStatus).toBeCalled();
        expect(updateFieldStatus).toBeCalledWith('password_confirm', 'valid');
    });

    it('should dispatch findFieldsWithErrors if confirm equals password', () => {
        validatePasswordConfirm('testpass', 'testpass')(mockData.props.dispatch, mockData.getState);
        expect(findFieldsWithErrors).toBeCalled();
    });

    it('should call updateFieldStatus with arg "not_valid" if confirm not equals password', () => {
        validatePasswordConfirm('testpass', 'testpass123')(mockData.props.dispatch, mockData.getState);
        expect(updateFieldStatus).toBeCalled();
        expect(updateFieldStatus).toBeCalledWith('password_confirm', 'not_valid');
    });
});
