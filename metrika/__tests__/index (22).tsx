import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotInternationalizedTest } from 'testing/jest-utils';

import { FilterSubstring } from '..';
import i18n from 'utils/i18n';
import * as keyset from '../FilterSubstring.i18n';

const snapshots: ReactElementsList = {
    'filter substring': <FilterSubstring onApply={jest.fn()} />,
};

describe('FilterSubstring', () => {
    describe('renders', () => {
        jestSnapshotInternationalizedTest(snapshots, i18n('ru', keyset));
    });
});
