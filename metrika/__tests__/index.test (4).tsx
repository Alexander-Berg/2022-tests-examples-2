import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotRenderTest } from 'testing/jest-utils';
import { Divider } from '..';

const componentsForSnapshotRenderTest: ReactElementsList = {
    correctly: <Divider />,
    'with incoming className': <Divider className="className" />,
};

describe('Divider', () => {
    describe('renders', () => {
        jestSnapshotRenderTest(componentsForSnapshotRenderTest);
    });
});
