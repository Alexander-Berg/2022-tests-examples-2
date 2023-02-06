import * as React from 'react';
import { shallow } from 'enzyme';

import { Title } from './Title';

describe('Title', () => {
    it('Должен отрендериться заголовок 1 уровня', () => {
        expect(shallow(<Title level="1">Заголовок</Title>)).toMatchSnapshot();
    });

    it('Должен отрендериться заголовок 3 уровня', () => {
        expect(shallow(<Title level="3">Заголовок</Title>)).toMatchSnapshot();
    });

    it('Должен отрендериться заголовок 5 уровня', () => {
        expect(shallow(<Title level="5">Заголовок</Title>)).toMatchSnapshot();
    });
});
