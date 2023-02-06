import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotInternationalizedTest } from 'testing/jest-utils';

import { FilterConditionToggler } from '..';
import i18n from 'utils/i18n';
import * as keyset from '../../../FilterCommon.i18n';

const snapshots: ReactElementsList = {
    include: <FilterConditionToggler inverted={false} onChange={jest.fn()} />,
    exclude: <FilterConditionToggler inverted onChange={jest.fn()} />,
};

describe('FilterConditionToggler', () => {
    describe('renders', () => {
        jestSnapshotInternationalizedTest(snapshots, i18n('ru', keyset));
    });
});
