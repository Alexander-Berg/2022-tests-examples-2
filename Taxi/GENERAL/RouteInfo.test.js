import React from 'react';
import {shallow} from 'enzyme';
import {useComponents} from '_common/static/utils/components-provider';
import {useRequestOrderconcatobtainAPI, useTariffClass} from '../../hooks';
import {RouteInfo} from './RouteInfo';

jest.mock('_common/static/utils/components-provider');

jest.mock('../../hooks');

const components = {
    Car: () => null,
    RoutePoint: () => null
};

describe('RouteInfo', () => {
    it('Верное количество точек', () => {
        useComponents.mockImplementation(() => components);
        useRequestOrderconcatobtainAPI.mockImplementation(() => jest.fn());
        useTariffClass.mockImplementation(() => jest.fn());

        const route = [
            {geopoint: [1, 1], short_text: 'A'},
            {geopoint: [1, 1], short_text: 'B'},
            {geopoint: [1, 1], short_text: 'C'}
        ];

        const wrapper = shallow(<RouteInfo route={route}/>);
        expect(wrapper.find(components.RoutePoint)).toHaveLength(3);
    });
});
