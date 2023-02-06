import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { TreeMultiselectLabel } from '..';
import { jestSnapshotShallowTest } from 'testing/jest-utils';

const snapshots: ReactElementsList = {
    'checked="yes"': (
        <TreeMultiselectLabel
            checked="yes"
            collapsed={false}
            loading={false}
            disableExpand={false}
            onCheckboxToggle={jest.fn()}
            onCollapserToggle={jest.fn()}
        >
            Россия
        </TreeMultiselectLabel>
    ),
    'checked="no"': (
        <TreeMultiselectLabel
            checked="no"
            collapsed={false}
            loading={false}
            disableExpand={false}
            onCheckboxToggle={jest.fn()}
            onCollapserToggle={jest.fn()}
        >
            Россия
        </TreeMultiselectLabel>
    ),
    'checked="indeterminate"': (
        <TreeMultiselectLabel
            checked="indeterminate"
            collapsed={false}
            loading={false}
            disableExpand={false}
            onCheckboxToggle={jest.fn()}
            onCollapserToggle={jest.fn()}
        >
            Россия
        </TreeMultiselectLabel>
    ),
    collapsed: (
        <TreeMultiselectLabel
            checked="no"
            collapsed
            loading={false}
            disableExpand={false}
            onCheckboxToggle={jest.fn()}
            onCollapserToggle={jest.fn()}
        >
            Россия
        </TreeMultiselectLabel>
    ),
    loading: (
        <TreeMultiselectLabel
            checked="no"
            collapsed
            loading
            disableExpand={false}
            onCheckboxToggle={jest.fn()}
            onCollapserToggle={jest.fn()}
        >
            Россия
        </TreeMultiselectLabel>
    ),
    disableExpand: (
        <TreeMultiselectLabel
            checked="no"
            collapsed={false}
            loading={false}
            disableExpand
            onCheckboxToggle={jest.fn()}
            onCollapserToggle={jest.fn()}
        >
            Россия
        </TreeMultiselectLabel>
    ),
};

describe('TreeMultiselectLabel', () => {
    describe('renders', () => {
        jestSnapshotShallowTest(snapshots);
    });
});
