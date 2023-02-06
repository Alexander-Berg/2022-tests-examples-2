import * as React from 'react';
import { cleanup } from 'react-testing-library';
import { SimpleDimension } from '..';
import { jestSnapshotRenderTest } from 'utils/jest-utils';

afterEach(cleanup);

jestSnapshotRenderTest({
    'without label': (
        <SimpleDimension
            hasLabel={false}
            id="test"
            expandable={false}
            expandedState="hidden"
            selectable={true}
            selected={true}
            size="s"
            onSelect={() => undefined}
        />
    ),
    'with label': (
        <SimpleDimension
            hasLabel={true}
            id="test"
            expandable={false}
            expandedState="hidden"
            selectable={true}
            selected={true}
            size="s"
            onSelect={() => undefined}
        />
    ),
    'without checkbox': (
        <SimpleDimension
            hasLabel={true}
            id="test"
            expandable={false}
            expandedState="hidden"
            selectable={false}
            selected={false}
            size="s"
            onSelect={() => undefined}
        />
    ),
});
