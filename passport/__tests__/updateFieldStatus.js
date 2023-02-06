import {updateStates, updateErrors} from '@blocks/actions/form';
import updateFieldStatus from '../methods/updateFieldStatus';
import mockData from './__mocks__/data';

jest.mock('@blocks/actions/form', () => ({
    updateStates: jest.fn(),
    updateErrors: jest.fn()
}));

describe('updateFieldStatus', () => {
    const props = mockData.props;

    it('should dispatch updateStates if field status valid', () => {
        updateFieldStatus('name', 'valid')(props.dispatch);
        expect(updateStates).toBeCalled();
        expect(updateStates).toBeCalledWith({field: 'name', status: 'valid'});
    });
    it('should dispatch updateErrors if field status valid', () => {
        updateFieldStatus('name', 'valid')(props.dispatch);
        expect(updateErrors).toBeCalled();
        expect(updateErrors).toBeCalledWith({field: 'name', error: {code: '', text: ''}, active: false});
    });
    it('should dispatch updateErrors with error if field status valid is not valid', () => {
        updateFieldStatus('name', 'not_valid')(props.dispatch, {code: 'invalid.name', text: 'error code'});
        expect(updateErrors).toBeCalled();
        expect(updateErrors).toBeCalledWith({
            field: 'name',
            errorDescription: '',
            error: {code: 'invalid.name', text: 'error code'},
            active: true
        });
    });
});
