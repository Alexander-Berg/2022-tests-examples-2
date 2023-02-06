import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotRenderTest } from 'testing/jest-utils';
import { Heading, HeadingLevel } from '..';

const levels: Array<HeadingLevel> = ['1', '2', '3'];
const allPossibleLevels: ReactElementsList = levels.reduce(
    (list, level) => ({
        ...list,

        [`with defined level=${level}`]: <Heading {...{ level }}>Test</Heading>,

        [`with defined level=${level}&margin=false`]: (
            <Heading {...{ level, margin: false }}>Test</Heading>
        ),
    }),
    {},
);

const simpleCases: ReactElementsList = {
    'correctly with default props': <Heading>Test</Heading>,
    'with passed className': <Heading className="className">Test</Heading>,
};

const componentsForSnapshotRenderTest: ReactElementsList = {
    ...simpleCases,
    ...allPossibleLevels,
};

describe('Heading', () => {
    describe('renders', () => {
        jestSnapshotRenderTest(componentsForSnapshotRenderTest);
    });
});
