import React from 'react';
import {shallow} from 'enzyme';
import DeletionChecks, {FormButtons, ConfirmationComponent} from '../deletionChecks';
import WrappedCaptchaContainer from '../../captchaContainer.jsx';

describe('DeletionChecks component', () => {
    describe('initial render', () => {
        const props = {
            confirmation: {
                method: 'phone',
                status: 'unconfirmed',
                phone: '+7 495 ***-**-24'
            },
            error: {},
            form: {
                captcha: '',
                phone: ''
            },
            isFetching: false,
            isMobile: false,
            dispatch: jest.fn()
        };
        const wrapper = shallow(<DeletionChecks {...props} />);

        it('should render ConfirmationComponent', () => {
            expect(wrapper.find(ConfirmationComponent).length).toBe(1);
        });

        it('should render FormButtons', () => {
            expect(wrapper.find(FormButtons).length).toBe(1);
        });

        it('should render captcha if status = unconfirmed', () => {
            expect(wrapper.find(WrappedCaptchaContainer).length).toBe(1);
        });
    });

    describe('status != unconfirmed render', () => {
        const props = {
            confirmation: {
                method: 'phone',
                status: 'code_sent',
                phone: '+7 495 ***-**-24'
            },
            error: {},
            form: {
                captcha: '',
                phone: ''
            },
            isFetching: false,
            isMobile: false,
            dispatch: jest.fn()
        };
        const wrapper = shallow(<DeletionChecks {...props} />);

        it('should not render captcha if status not equal unconfirmed', () => {
            expect(wrapper.find(WrappedCaptchaContainer).length).toBe(0);
        });
    });
});
