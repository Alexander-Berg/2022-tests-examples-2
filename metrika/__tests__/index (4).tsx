import * as React from 'react';
import { cleanup, render, fireEvent } from 'react-testing-library';
import { ColorCheckBox } from '..';
import { jestSnapshotRenderTest, LeftMouseEvent } from 'utils/jest-utils';

afterEach(cleanup);

jestSnapshotRenderTest({
    'with defaults': <ColorCheckBox size="s" theme="normal" />,
    '`color` is passed': (
        <ColorCheckBox size="s" theme="normal" color="black" />
    ),
    '`tickColor` is passed': (
        <ColorCheckBox
            size="s"
            theme="normal"
            color="white"
            tickColor="black"
        />
    ),
});

describe('callbacks', () => {
    it('onChange works', () => {
        const spy = jest.fn();
        const { container } = render(
            <ColorCheckBox
                size="s"
                theme="normal"
                color="black"
                onChange={spy}
            />,
        );

        fireEvent(container.firstChild as HTMLElement, LeftMouseEvent);
        expect(spy).toHaveBeenCalledTimes(1);
    });
});
