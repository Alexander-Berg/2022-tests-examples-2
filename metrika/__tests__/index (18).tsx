import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotInternationalizedTest } from 'testing/jest-utils';

import { EmptyList } from '..';
import i18n from 'utils/i18n';
import * as keyset from '../../../FilterCommon.i18n';

const snapshots: ReactElementsList = {
    'empty list message': <EmptyList />,
};

describe('FilterCommon', () => {
    describe('renders', () => {
        jestSnapshotInternationalizedTest(snapshots, i18n('ru', keyset));
    });
});
