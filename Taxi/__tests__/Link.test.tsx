import React from 'react';
import {shallow} from 'enzyme';
import Link from '../Link';

const url = 'http://yandex.ru';
describe('Components/link', () => {
    it('Если есть параметр disabled - тег блока span', () => {
        const wrapper = shallow(<Link url={url} disabled/>);
        expect(wrapper.find('span').exists()).toBeTruthy();
    });

    it('Если есть параметр onClick - проверяем что событие вызвалось 1 раз', () => {
        const onLinkClick = jest.fn();
        const wrapper = shallow(<Link url={url} onClick={onLinkClick}/>);
        wrapper.simulate('click');
        expect(onLinkClick.mock.calls.length).toBe(1);
    });

    it('Если есть параметр url - выставяется аттрибут href', () => {
        const wrapper = shallow(<Link url={url}/>);
        expect(wrapper.prop('href')).toEqual(url);
    });

    it('Выставление темы в className', () => {
        const theme = 'header-nav';
        const wrapper = shallow(<Link theme={theme} url={url}/>);
        expect(wrapper.prop('className')).toContain(theme);
    });
});
