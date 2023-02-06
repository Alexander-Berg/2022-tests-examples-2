import * as React from 'react';
import { cleanup } from 'react-testing-library';
import { Value, ValueProps } from '..';
import { jestSnapshotRenderTest } from 'utils/jest-utils';

afterEach(cleanup);

jestSnapshotRenderTest(
    ['s', 'm'].reduce(
        (accumulator, size: ValueProps['size']) => ({
            ...accumulator,
            [`empty size ${size}`]: <Value size={size} />,
            [`with main size ${size}`]: (
                <Value size={size}>
                    <Value.Main>anything</Value.Main>
                </Value>
            ),
            [`with secondary size ${size}`]: (
                <Value size={size}>
                    <Value.Secondary>anything</Value.Secondary>
                </Value>
            ),
            [`with main and secondary size ${size}`]: (
                <Value size={size}>
                    <Value.Main>anything</Value.Main>
                    <Value.Secondary>anything</Value.Secondary>
                </Value>
            ),
        }),
        {},
    ),
);
