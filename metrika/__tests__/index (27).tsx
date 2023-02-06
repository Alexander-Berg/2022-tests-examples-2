import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotRenderTest } from 'testing/jest-utils';
import { WidgetTable } from '..';

const componentsForSnapshotRenderTest: ReactElementsList = {
    correctly: (
        <WidgetTable>
            <WidgetTable.Widget colSpan={4} rowSpan={1}>
                Widget 1
            </WidgetTable.Widget>
            <WidgetTable.Widget colSpan={2} rowSpan={1}>
                Widget 2
            </WidgetTable.Widget>
        </WidgetTable>
    ),
    'with incoming className': <WidgetTable className="className" />,
};

describe('WidgetTable', () => {
    describe('renders', () => {
        jestSnapshotRenderTest(componentsForSnapshotRenderTest);
    });
});
