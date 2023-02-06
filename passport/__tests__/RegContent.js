import React from 'react';
import {shallow} from 'enzyme';
import {RegContent} from '../registration.jsx';
import RegistrationForm from '../registration_form.jsx';
import RegistrationLite from '../../../registration-lite/RegistrationLite';

describe('RegContent component', () => {
    const errorsObj = {};

    it('should render default registration component if registrationType prop is not defined', () => {
        const wrapper = shallow(<RegContent errors={errorsObj} registrationType='default' />);

        expect(wrapper.find(RegistrationForm).length).toBe(1);
    });
    it('should render RegistrationLightForm component if registrationType prop is "lite"', () => {
        const wrapper = shallow(<RegContent errors={errorsObj} registrationType='lite' />);

        expect(wrapper.find(RegistrationLite).length).toBe(1);
    });
});
