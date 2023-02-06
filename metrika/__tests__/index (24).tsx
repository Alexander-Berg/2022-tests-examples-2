import * as React from 'react';
import { cleanup, render, fireEvent } from 'react-testing-library';
import { ShowMore } from '..';
import { jestSnapshotRenderTest, LeftMouseEvent } from 'utils/jest-utils';

afterEach(cleanup);

jestSnapshotRenderTest({
    'with defaults': <ShowMore size="s" />,
    progress: <ShowMore size="s" progress />,
    'only offset passed': <ShowMore size="s" offset={20} />,
    'only total passed': <ShowMore size="s" total={40} />,
    'offset and total passed': <ShowMore size="s" offset={20} total={40} />,
});

describe('callbacks', () => {
    it('onClick works', () => {
        const spy = jest.fn();
        const { container } = render(
            <ShowMore size="s" offset={20} total={40} onClick={spy} />,
        );

        fireEvent(
            (container.firstChild as Element).querySelector('button')!,
            LeftMouseEvent,
        );
        expect(spy).toHaveBeenCalledTimes(1);
    });
});
