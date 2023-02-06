import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotInternationalizedTest } from 'testing/jest-utils';

import { ComparableInput } from '..';
import i18n from 'utils/i18n';
import * as keyset from '../ComparableInput.i18n';

const onChange = jest.fn();

const snapshots: ReactElementsList = {
    'with default behavior': <ComparableInput onChange={onChange} />,
    'with behavior contraction': (
        <ComparableInput onChange={onChange} behavior="contraction" />
    ),
    'with behavior restrictToNumber': (
        <ComparableInput onChange={onChange} behavior="restrictToNumber" />
    ),
    'with behavior restrictToUnsignedInt': (
        <ComparableInput onChange={onChange} behavior="restrictToUnsignedInt" />
    ),
    'with single condition value and operator ==': (
        <ComparableInput
            onChange={onChange}
            condition={{ value: '10', operator: '==' }}
        />
    ),
    'with single condition value and operator !=': (
        <ComparableInput
            onChange={onChange}
            condition={{ value: '10', operator: '!=' }}
        />
    ),
    'with single condition value and operator <': (
        <ComparableInput
            onChange={onChange}
            condition={{ value: '10', operator: '<' }}
        />
    ),
    'with single condition value and operator >': (
        <ComparableInput
            onChange={onChange}
            condition={{ value: '10', operator: '>' }}
        />
    ),
    'with range condition value': (
        <ComparableInput
            onChange={onChange}
            condition={{ value: ['10', '20'], operator: '<>' }}
        />
    ),
};

describe('ComparableInput', () => {
    describe('renders', () => {
        jestSnapshotInternationalizedTest(snapshots, i18n('ru', keyset));
    });
});
