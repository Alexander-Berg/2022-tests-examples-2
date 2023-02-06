import * as React from 'react';
import { cleanup, render, fireEvent } from 'react-testing-library';
import { PlusExpander, PlusExpanderProps } from '..';
import { jestSnapshotRenderTest, LeftMouseEvent } from 'utils/jest-utils';

afterEach(cleanup);

type Size = PlusExpanderProps['size'];
type State = PlusExpanderProps['state'];

const sizes: Size[] = ['s', 'm'];
const states: State[] = ['loading', 'opened', 'closed'];

function pairs(sizes: Size[], states: State[]) {
    return sizes.reduce<Array<[Size, State]>>((result, size) => {
        /**
         * не получилось
         * return [
         *      ...result,
         *      ...states.map((state) => [size, state]),
         * ];
         */
        states.forEach((state) => {
            result.push([size, state]);
        });

        return result;
    }, []);
}

const snapshotsMap = pairs(sizes, states).reduce((result, [size, state]) => {
    return {
        ...result,
        [`size "${size}", state "${state}"`]: (
            <PlusExpander size={size} state={state} />
        ),
    };
}, {});

jestSnapshotRenderTest(snapshotsMap);

describe('callbacks', () => {
    it('called with proper state', () => {
        const spy = jest.fn();
        const { container } = render(
            <PlusExpander state="opened" size="s" onClick={spy} />,
        );

        fireEvent(container.firstChild as HTMLElement, LeftMouseEvent);
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('opened');
    });

    it('called with proper state', () => {
        const spy = jest.fn();
        const { container } = render(
            <PlusExpander state="closed" size="s" onClick={spy} />,
        );

        fireEvent(container.firstChild as HTMLElement, LeftMouseEvent);
        expect(spy).toHaveBeenCalledTimes(1);
        expect(spy).toHaveBeenCalledWith('closed');
    });
});
