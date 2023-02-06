import * as React from 'react';
import {
    cleanup,
    render,
    fireEvent,
    RenderResult,
} from 'react-testing-library';
import { SortableHeader } from '..';
import { jestSnapshotRenderTest, LeftMouseEvent } from 'utils/jest-utils';

afterEach(cleanup);

jestSnapshotRenderTest({
    'with default params': <SortableHeader>Заголовок</SortableHeader>,
    'direction asc': <SortableHeader direction="asc">Заголовок</SortableHeader>,
    'direction desc': (
        <SortableHeader direction="desc">Заголовок</SortableHeader>
    ),
    'with direction and hint': (
        <SortableHeader direction="asc" hint="Подсказка">
            Заголовок
        </SortableHeader>
    ),
});

describe('sort callback', () => {
    let spy: jest.Mock;
    let rerender: RenderResult['rerender'];
    let getByText: RenderResult['getByText'];

    beforeEach(() => {
        spy = jest.fn();

        const renderResult = render(
            <SortableHeader onSort={spy}>Визиты</SortableHeader>,
        );
        rerender = renderResult.rerender;
        getByText = renderResult.getByText;
    });
    it('works', () => {
        fireEvent(getByText('Визиты'), LeftMouseEvent);
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('desc');
    });

    it('desc -> asc', () => {
        rerender(
            <SortableHeader onSort={spy} direction="desc">
                Визиты
            </SortableHeader>,
        );
        fireEvent(getByText('Визиты'), LeftMouseEvent);
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('asc');
    });
});
