import React from 'react';
import {shallow} from 'enzyme';
import RouteListDumb from './RouteList';

jest.mock('../../hooks', () => ({
    useTariffClass: () => 'default'
}));

jest.mock('_common/static/utils/context/i18n', () => ({
    useI18n: () => ({print: jest.fn()})
}));

jest.mock('_common/static/utils/components-provider', () => {
    return {
        ComponentsConsumer: props => props.children({PointIcon: () => null})
    };
});

describe('Маршрут', () => {
    it('Не рендерится, если маршрут пустой', () => {
        const wrapper = shallow(<RouteListDumb route={[]}/>);
        expect(wrapper.equals(null)).toBeTruthy();
    });

    it('Количество точек === количество элментов в списке', () => {
        for (let i = 1; i < 5; ++i) {
            const route = Array.from({length: i}).map(() => ({}));
            const wrapper = shallow(<RouteListDumb route={route}/>).dive();
            expect(wrapper.find('Item')).toHaveLength(i);
        }
    });
});
