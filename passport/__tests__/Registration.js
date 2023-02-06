import React from 'react';
import {shallow} from 'enzyme';
import {Registration} from '../registration.jsx';

const props = {
    tld: 'ru',
    language: 'ru',
    isMobile: false,
    footer: {
        langlist: [{id: 'ru', link: '#'}]
    },
    common: {
        track_id: '12344'
    },
    settings: {
        authUrl: 'https://4020.passportdev.yandex.ru/auth',
        formUrl: '/registration',
        host: 'https://4020.passportdev.yandex.ru',
        tld: 'ru',
        language: 'ru',
        uatraits: {
            BrowserName: 'Test',
            isMobile: false,
            isTouch: false
        }
    },
    registrationErrors: {
        code: '',
        status: 'ok',
        text: ''
    }
};

describe('Registration component', () => {
    describe('Desktop version', () => {
        const updatedProps = Object.assign({}, props, {isMobile: false});

        it('should renders with correct css class', () => {
            const wrapper = shallow(<Registration {...updatedProps} />);

            expect(wrapper.find('.registration__wrapper_desktop').length).toBe(1);
        });
    });
    describe('Mobile version', () => {
        const updatedProps = Object.assign({}, props, {isMobile: true});

        it('should renders with correct css class', () => {
            const wrapper = shallow(<Registration {...updatedProps} />);

            expect(wrapper.find('.registration__wrapper_desktop').length).toBe(0);
            expect(wrapper.find('.is_mobile_reg').length).toBe(1);
        });
    });
});
