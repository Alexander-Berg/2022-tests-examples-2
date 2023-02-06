import React from 'react';

import {shallow} from 'enzyme';

import LangSwitcher from './index';

describe('LangSwitcher', () => {
    it('Не рендерит список языков по дефолту', () => {
        const handler = jest.fn();
        const wrapper = shallow(
            <LangSwitcher selectedLanguage="ru" languages={['ru', 'en']} onChange={handler} />,
        );
        expect(wrapper).toMatchSnapshot();
    });

    it('Рендерит список языков после клика', () => {
        const handler = jest.fn();
        const wrapper = shallow(
            <LangSwitcher selectedLanguage="ru" languages={['ru', 'en']} onChange={handler} />,
        );
        wrapper.find('.LangSwitcher__selected-language').simulate('click');
        expect(wrapper.find('.LangSwitcher__dropdown').exists).toBeTruthy();
        expect(wrapper.find('.LangSwitcher__language').length).toBe(2);
        expect(wrapper).toMatchSnapshot();
    });

    it('Вызывает обработчик изменения при клике', () => {
        const handler = jest.fn();
        const wrapper = shallow(
            <LangSwitcher selectedLanguage="ru" languages={['ru', 'en']} onChange={handler} />,
        );
        wrapper.find('.LangSwitcher__selected-language').simulate('click');
        wrapper.find('.LangSwitcher__language').last().simulate('click');
        expect(handler).toBeCalledTimes(1);
        expect(handler).toBeCalledWith('en');
    });
});
