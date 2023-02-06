import React from 'react';
import {shallow} from 'enzyme';
import {Input} from '@components/Input';
import RegistrationSurnameInput from '../surname/surname_input.jsx';
import {updateValues} from '@blocks/actions/form';

jest.mock('@blocks/actions/form', () => ({
    updateValues: jest.fn()
}));

const componentProps = {
    value: 'test',
    state: '',
    error: {
        code: '',
        text: ''
    },
    hintActive: true,
    activeField: 'surname',
    updateUserField: jest.fn(),
    dispatch: jest.fn()
};

describe('RegistrationSurnameInput', () => {
    it('should render hidden fakeSurname input', () => {
        const wrapper = shallow(<RegistrationSurnameInput {...componentProps} />);
        const surnameInput = wrapper.find(Input).filter('#surname');

        expect(surnameInput.length).toBe(1);
    });
    it('should call changeFakeSurname if fakeSurname input changes value', () => {
        const wrapper = shallow(<RegistrationSurnameInput {...componentProps} />);

        wrapper
            .find(Input)
            .filter('#surname')
            .simulate('change', {target: {value: 'Blane', name: 'surname'}});
        expect(updateValues).toBeCalled();
        expect(updateValues).toBeCalledWith({value: 'Blane', field: 'surname'});
    });
});
