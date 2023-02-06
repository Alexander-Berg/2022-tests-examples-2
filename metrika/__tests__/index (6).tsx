import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotInternationalizedTest } from 'testing/jest-utils';

import { DatePicker } from '..';
import i18n from 'utils/i18n';
import * as keyset from '../DatePicker.i18n';

const onChange = jest.fn();

const snapshots: ReactElementsList = {
    'with error': (
        <DatePicker
            startDate={new Date('2000-02-02')}
            endDate={new Date('2000-02-20')}
            onChange={onChange}
            error
        />
    ),
    'with predefined period': (
        <DatePicker
            startDate={new Date('2000-02-02')}
            endDate={new Date('2000-02-20')}
            onChange={onChange}
        />
    ),
};

describe('ControlsList', () => {
    describe('renders', () => {
        jestSnapshotInternationalizedTest(snapshots, i18n('ru', keyset));
    });
});
