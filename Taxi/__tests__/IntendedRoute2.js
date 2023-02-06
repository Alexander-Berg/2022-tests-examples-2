import React from 'react';
import {shallow} from 'enzyme';

import {IntendedRoute2Dumb} from '../IntendedRoute2';
import Route from '../Route';

describe('Прогназируемый марщрут', () => {
    it('Строиться только тогда, когда в маршруте 2 точки', () => {
        const route = generateRoute(2);
        const wrapper = shallow(<IntendedRoute2Dumb route={route} coordinates={[]}/>);

        expect(wrapper.find(Route)).toHaveLength(1);
    });

    it('Не строится, если точек не 2', () => {
        const numbers = Array.from({length: 5}).map((_0, i) => i);

        for (let i of numbers) {
            if (i === 2) {
                continue;
            }
            const route = generateRoute(i);
            const wrapper = shallow(<IntendedRoute2Dumb route={route} coordinates={[]}/>);
            expect(wrapper.equals(null)).toBeTruthy();
        }
    });

    it('Не строиться, если не передали текущее положение машины', () => {
        const numbers = Array.from({length: 5}).map((_0, i) => i);

        for (let i of numbers) {
            const route = generateRoute(i);
            const wrapper = shallow(<IntendedRoute2Dumb route={route}/>);
            expect(wrapper.equals(null)).toBeTruthy();
        }
    });
});

function generateRoute(length) {
    return Array.from({length}).map(() => []);
}
