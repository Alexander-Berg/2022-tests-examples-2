import React from 'react';
import { cleanup } from 'react-testing-library';
import { ChartWidget } from '..';
import { jestSnapshotRenderTest } from 'client/utils/jest-utils';

afterEach(cleanup);

jestSnapshotRenderTest({
    'with status loading': (
        <ChartWidget
            status="loading"
            referenceTitle="Plan"
            title="Chart widget caption"
        />
    ),
    'with status error': (
        <ChartWidget
            status="error"
            referenceTitle="Plan"
            title="Chart widget caption"
        />
    ),
});
