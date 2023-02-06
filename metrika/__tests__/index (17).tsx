import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotInternationalizedTest } from 'testing/jest-utils';

import { ApplyButton } from '..';
import i18n from 'utils/i18n';
import * as keyset from '../../../FilterCommon.i18n';

const snapshots: ReactElementsList = {
    'apply button': <ApplyButton onClick={jest.fn()} />,
};

describe('ApplyButton', () => {
    describe('renders', () => {
        jestSnapshotInternationalizedTest(snapshots, i18n('ru', keyset));
    });
});
