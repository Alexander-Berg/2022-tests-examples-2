import * as React from 'react';

import { render, configure } from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';

import { Highlight, Substr } from '..';
configure({ adapter: new Adapter() });

describe('Highlight', () => {
    it('работает по строке', () => {
        const container = render(
            <div>
                <Highlight pattern="екс">текст</Highlight>
            </div>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с вложенными строками', () => {
        const container = render(
            <div>
                <Highlight pattern="екс">
                    <span>текст</span>
                </Highlight>
            </div>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с несколькими вложенными строками', () => {
        const container = render(
            <div>
                <Highlight pattern="екс">
                    <span>текст</span>
                    <span>текст</span>
                </Highlight>
            </div>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с несколькими паттернами через пробел', () => {
        const container = render(
            <div>
                <Highlight pattern="ако екс">
                    <span>какой-то текст</span>
                    <span>какой-то текст</span>
                </Highlight>
            </div>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с паттернами через массив', () => {
        const container = render(
            <div>
                <Highlight pattern={['ако', 'екс']}>
                    <span>какой-то текст</span>
                    <span>какой-то текст</span>
                </Highlight>
            </div>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с подсветкой фона', () => {
        const container = render(
            <div>
                <Highlight pattern={['ако', 'екс']} highlight="background">
                    <span>какой-то текст</span>
                    <span>какой-то текст</span>
                </Highlight>
            </div>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает позиционная подсветка', () => {
        const container = render(
            <div>
                <Substr match={{ start: 1, end: 3 }}>Here comes Johny!</Substr>
            </div>,
        );

        expect(container).toMatchSnapshot();
    });
});
