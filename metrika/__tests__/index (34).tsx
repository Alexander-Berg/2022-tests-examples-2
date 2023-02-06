import React from 'react';
import { cleanup } from 'react-testing-library';
import { jestSnapshotRenderTest } from 'client/utils/jest-utils';
import { Notifications } from '..';

afterEach(cleanup);

jestSnapshotRenderTest({
    'without notifications prop provided': <Notifications notifications={[]} />,
    'with notifications prop provided': (
        <Notifications notifications={[<div key="id">Notification</div>]} />
    ),
});
