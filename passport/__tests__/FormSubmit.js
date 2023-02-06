import React from 'react';
import {shallow} from 'enzyme';
import {Button} from '@components/Button';
import EulaPopup from '../../desktop/eula/EulaPopup.jsx';
import FormSubmit from '../FormSubmit.jsx';

describe('FormSubmit component', () => {
    const props = {
        onSubmit: jest.fn(),
        isEulaByPopup: false,
        sendData: jest.fn(),
        disable: false
    };

    it('should renders with Button', () => {
        const submitWrapper = shallow(<FormSubmit {...props} />);

        expect(submitWrapper.find(Button).length).toBe(1);
    });
    it('should renders without Eula component if prop isEulaByPopup is false', () => {
        const submitWrapper = shallow(<FormSubmit {...props} />);

        expect(submitWrapper.find(EulaPopup).length).toBe(0);
    });
    it('should renders with Eula component if prop isEulaByPopup is true', () => {
        props.isEulaByPopup = true;
        const submitWrapper = shallow(<FormSubmit {...props} />);

        expect(submitWrapper.find(EulaPopup).length).toBe(1);
    });
});
