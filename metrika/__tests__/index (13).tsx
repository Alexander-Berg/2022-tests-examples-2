import * as React from 'react';
import { cleanup, render, fireEvent } from 'react-testing-library';
import { Dimension, DimensionProps } from '..';
import { jestSnapshotRenderTest, LeftMouseEvent } from 'utils/jest-utils';

afterEach(cleanup);

jestSnapshotRenderTest(
    ['s', 'm'].reduce(
        (accumulator, size: DimensionProps['size']) => ({
            ...accumulator,
            [`default state size ${size}`]: <Dimension size={size} />,
            [`selectable size ${size}`]: <Dimension size={size} selectable />,
            [`selectable and selected size ${size}`]: (
                <Dimension size={size} selectable selected />
            ),
            [`expandable size ${size}`]: <Dimension size={size} expandable />,
            ...['opened', 'closed', 'loading', 'hidden'].reduce(
                (accum, expandedState: DimensionProps['expandedState']) => ({
                    ...accum,
                    [`expandable and ${expandedState} size ${size}`]: (
                        <Dimension
                            size={size}
                            expandable
                            expandedState={expandedState}
                        />
                    ),
                }),
                {},
            ),
        }),
        {},
    ),
);

describe('callbacks', () => {
    describe('onSelect', () => {
        it('selected', () => {
            const spy = jest.fn();
            const id = 'test';
            const { getByTestId } = render(
                <Dimension selectable selected size="s" id={id} onSelect={spy}>
                    <label htmlFor={id} data-testid="label">
                        content
                    </label>
                </Dimension>,
            );

            fireEvent(getByTestId('label'), LeftMouseEvent);
            expect(spy).toHaveBeenCalledTimes(1);
        });
        it('not selected', () => {
            const spy = jest.fn();
            const id = 'test2';
            const { getByTestId } = render(
                <Dimension selectable size="s" id={id} onSelect={spy}>
                    <label htmlFor={id} data-testid="label">
                        content
                    </label>
                </Dimension>,
            );

            fireEvent(getByTestId('label'), LeftMouseEvent);
            expect(spy).toHaveBeenCalledTimes(1);
        });
    });
});
