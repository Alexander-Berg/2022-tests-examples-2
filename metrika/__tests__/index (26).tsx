import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { TristateCheckBox } from '..';
import { jestSnapshotShallowTest } from 'testing/jest-utils';

const snapshots: ReactElementsList = {
    'checked="yes"': (
        <TristateCheckBox theme="normal" size="s" checked="yes">
            checked="yes"
        </TristateCheckBox>
    ),
    'checked="no"': (
        <TristateCheckBox theme="normal" size="s" checked="no">
            checked="no"
        </TristateCheckBox>
    ),
    'checked="indeterminate"': (
        <TristateCheckBox theme="normal" size="s" checked="indeterminate">
            checked="indeterminate"
        </TristateCheckBox>
    ),
};

describe('TristateCheckBox', () => {
    describe('renders', () => {
        jestSnapshotShallowTest(snapshots);
    });
});
