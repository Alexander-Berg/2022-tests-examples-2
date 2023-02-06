import React from 'react';
import {shallow} from 'enzyme';
import RegistrationEmailInput from '../RegistrationEmailInput.jsx';
import UserPassword from '../../../registration/fieldComponents/userpassword.jsx';
import {RegistrationFields, NameControls, PasswordControls} from '../RegistrationFields.jsx';

describe('RegistrationFields component', () => {
    const props = {
        form: {
            activeField: '',
            errors: {},
            formErrors: [],
            isEulaShowedInPopup: false,
            states: {},
            values: {},
            type: '',
            showPasswordFields: false
        },
        dispatch: jest.fn(),
        showPasswordFields: jest.fn(),
        isPasswordStepVisible: false
    };

    describe('render form', () => {
        it('should renders with correct fields', () => {
            const propsToRender = Object.assign({}, props, {
                isPasswordStepVisible: false
            });
            const wrapper = shallow(<RegistrationFields {...propsToRender} />);

            expect(wrapper.find(NameControls).length).toBe(1);
            expect(wrapper.find(PasswordControls).length).toBe(1);
        });

        it('should not render password fields on the first step', () => {
            const isFirstStep = true;
            const props = {
                isPasswordControlsRendered: !isFirstStep,
                states: {},
                values: {},
                errors: {},
                dispatch: jest.fn()
            };
            const wrapper = shallow(<PasswordControls {...props} />);

            expect(wrapper.find(UserPassword).length).toBe(0);
        });

        it('should render password fields on the second step', () => {
            const isSecondStep = true;
            const props = {
                isPasswordStepVisible: isSecondStep,
                states: {},
                values: {},
                errors: {},
                dispatch: jest.fn()
            };
            const wrapper = shallow(<PasswordControls {...props} />);

            expect(wrapper.find(UserPassword).length).toBe(1);
            expect(wrapper.find(RegistrationEmailInput).length).toBe(0);
            expect(wrapper.find(PasswordControls).length).toBe(0);
        });
    });
});
