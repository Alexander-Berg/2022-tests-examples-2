import React from 'react';
import {mount} from 'enzyme';
import EmailCheck from '../emailCheck.jsx';

describe('EmailCheck component', () => {
    describe('render component', () => {
        const props = {
            checkStatus: jest.fn(),
            confirmation: {
                method: 'email',
                emails: [{text: 'test@example.com', value: 'test@example.com'}],
                status: 'unconfirmed'
            },
            error: {},
            form: {
                captcha: '',
                email: 'test@example.com',
                code: ''
            },
            dispatch: jest.fn(),
            onClose: jest.fn()
        };
        const wrapper = mount(<EmailCheck {...props} />);

        it('should renders block with user email', () => {
            expect(wrapper.find('.user-email').length).toBe(1);
        });

        describe('render emails list', () => {
            it('should render select if emails length > 1', () => {
                const props = {
                    checkStatus: jest.fn(),
                    confirmation: {
                        method: 'email',
                        emails: [
                            {text: 'test@example.com', value: 'test@example.com'},
                            {text: 'test-another@example.com', value: 'test-another@example.com'}
                        ],
                        status: 'unconfirmed'
                    },
                    error: {},
                    form: {
                        captcha: '',
                        email: 'test@example.com',
                        code: ''
                    },
                    isMobile: false,
                    dispatch: jest.fn()
                };
                const wrapper = mount(<EmailCheck {...props} />);

                expect(wrapper.find('.delete-account_email-field').length).toBe(1);
            });
        });
    });
});
