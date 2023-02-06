import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotShallowTest } from 'testing/jest-utils';
import { ControlsList, ControlsListDirections } from '..';

const directions: ControlsListDirections[] = ['vertical', 'horizontal'];
const allPossibleDirections: ReactElementsList = directions.reduce(
    (list, direction) => ({
        ...list,
        [`with direction=${direction} prop`]: (
            <ControlsList direction={direction}>
                {'один'}
                {'два'}
            </ControlsList>
        ),
    }),
    {},
);

const simpleCases: ReactElementsList = {
    'with default props': (
        <ControlsList>
            {'один'}
            {'два'}
        </ControlsList>
    ),
    'with incoming className': (
        <ControlsList className="className">раз</ControlsList>
    ),
};

const componentsForSnapshotShallowTest: ReactElementsList = {
    ...simpleCases,
    ...allPossibleDirections,
};

describe('ControlsList', () => {
    describe('renders', () => {
        // Shallow
        jestSnapshotShallowTest(componentsForSnapshotShallowTest);
    });
});
