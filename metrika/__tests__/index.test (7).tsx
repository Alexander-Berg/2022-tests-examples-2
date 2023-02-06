/**
 * @jest-environment jsdom
 */
import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotShallowTest } from 'testing/jest-utils';
import { Hint } from '..';

const snapshots: ReactElementsList = {
    'with hint prop': <Hint hint="test">test</Hint>,
};

describe('Hint', () => {
    describe('renders', () => {
        jestSnapshotShallowTest(snapshots);
    });
});
