import {shallow} from 'enzyme';
import React from 'react';

import WithoutDraftCheckbox from '../';

jest.mock('_config');

describe('WithoutDraftCheckbox', () => {
    test('В проде ничего не рендерит', () => {
        const component = shallow(<WithoutDraftCheckbox isProduction />);
        expect(component.isEmptyRender()).toBeTruthy();
    });

    test('В анстейбле и тестинге рендерит компонент', () => {
        const component = shallow(<WithoutDraftCheckbox isProduction={false} />);
        expect(component.isEmptyRender()).toBeFalsy();
    });
});
