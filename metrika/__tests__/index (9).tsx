import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotShallowTest } from 'testing/jest-utils';

import { NumberRange } from '..';

const onChange = jest.fn();
const range: [string, string] = ['10', '20'];

const snapshots: ReactElementsList = {
    'with range': <NumberRange range={range} onChange={onChange} />,
};

describe('NumberRange', () => {
    describe('renders', () => {
        jestSnapshotShallowTest(snapshots);
    });
});
