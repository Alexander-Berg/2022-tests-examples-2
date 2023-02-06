import * as React from 'react';
import { render, cleanup } from 'react-testing-library';
import { Highlight, Substr } from '..';

afterEach(cleanup);

describe('Highlight', () => {
    it('работает по строке', () => {
        const { container } = render(
            <Highlight pattern="екс">текст</Highlight>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с вложенными строками', () => {
        const { container } = render(
            <Highlight pattern="екс">
                <span>текст</span>
            </Highlight>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с несколькими вложенными строками', () => {
        const { container } = render(
            <Highlight pattern="екс">
                <span>текст</span>
                <span>текст</span>
            </Highlight>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с несколькими паттернами через пробел', () => {
        const { container } = render(
            <Highlight pattern="ако екс">
                <span>какой-то текст</span>
                <span>какой-то текст</span>
            </Highlight>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с паттернами через массив', () => {
        const { container } = render(
            <Highlight pattern={['ако', 'екс']}>
                <span>какой-то текст</span>
                <span>какой-то текст</span>
            </Highlight>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает с подсветкой бэкграунда', () => {
        const { container } = render(
            <Highlight pattern={['ако', 'екс']} highlight="background">
                <span>какой-то текст</span>
                <span>какой-то текст</span>
            </Highlight>,
        );

        expect(container).toMatchSnapshot();
    });
    it('работает позиционная подсветка', () => {
        const { container } = render(
            <Substr match={{ start: 1, end: 3 }}>Here comes Johny!</Substr>,
        );

        expect(container).toMatchSnapshot();
    });
});
