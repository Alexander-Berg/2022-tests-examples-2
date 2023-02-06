import React from 'react';
import {shallow} from 'enzyme';

import AppstoreBadge from '../AppstoreBadge';

describe('Components/appstore-badge', () => {
    it('Возвращает ссылку если указана платформа', () => {
        const wrapper = shallow(<AppstoreBadge platform="ios" lang="ru" size="m" />);
        expect(wrapper.find('a').exists()).toBeTruthy();
    });

    it('Если передан англ. язык - рисуется англ. бейдж', () => {
        const wrapper = shallow(<AppstoreBadge platform="ios" lang="en" size="m" />);
        expect(wrapper.find('a').prop('lang')).toBe('en');
    });
});
