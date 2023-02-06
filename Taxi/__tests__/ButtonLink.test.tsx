import React from 'react';
import {mount} from 'enzyme';
import ButtonLink from '../ButtonLink';

describe('Components/button-link', () => {
    it('Можно передать href', () => {
        const url = 'https://yandex.ru';
        const wrapper = mount(<ButtonLink href={url}/>);
        expect(wrapper.find('a').exists()).toBeTruthy();
        expect(wrapper.find('a').prop('href')).toEqual(url);
    });
});
