import updateFormFields from '../update_form_fields';
import {updateError, updateFormDataFields} from '../../actions';

jest.mock('../../actions', () => ({
    updateError: jest.fn(),
    updateFormDataFields: jest.fn()
}));

const dispatch = jest.fn();

describe('updateFormFields', () => {
    it('should dispatch updateError with default values', () => {
        updateFormFields({captcha: 'testcaptha'})(dispatch);
        expect(updateError).toBeCalled();
    });

    it('should dispatch updateFormDataFields', () => {
        updateFormFields({captcha: 'test'})(dispatch);
        expect(updateFormDataFields).toBeCalled();
        expect(updateFormDataFields).toBeCalledWith({captcha: 'test'});
    });
});
