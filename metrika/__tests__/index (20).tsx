import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotInternationalizedTest } from 'testing/jest-utils';

import { Search } from '..';
import i18n from 'utils/i18n';
import * as keyset from '../../../FilterCommon.i18n';

const snapshots: ReactElementsList = {
    'without text': <Search text="" onSearch={jest.fn()} />,
    'with text': <Search text="text" onSearch={jest.fn()} />,
};

describe('Search', () => {
    describe('renders', () => {
        jestSnapshotInternationalizedTest(snapshots, i18n('ru', keyset));
    });
});
