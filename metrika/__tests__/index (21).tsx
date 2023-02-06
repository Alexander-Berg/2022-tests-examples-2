import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotInternationalizedTest } from 'testing/jest-utils';

import { FilterComparable } from '..';
import i18n from 'utils/i18n';
import * as keyset from '../FilterComparable.i18n';

const snapshots: ReactElementsList = {
    'restrict to number': (
        <FilterComparable onApply={jest.fn()} behavior="restrictToNumber" />
    ),
    'restrict to unsigned int': (
        <FilterComparable
            onApply={jest.fn()}
            behavior="restrictToUnsignedInt"
        />
    ),
};

describe('FilterComparable', () => {
    describe('renders', () => {
        jestSnapshotInternationalizedTest(snapshots, i18n('ru', keyset));
    });
});
