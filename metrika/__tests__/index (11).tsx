import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotShallowTest } from 'testing/jest-utils';

import { Preloader } from '..';

const snapshots: ReactElementsList = {
    default: <Preloader />,
    'transparent background': <Preloader transparent />,
    'size xs': <Preloader size="xs" />,
    'size s': <Preloader size="s" />,
    'size l': <Preloader size="l" />,
};

describe('Preloader', () => {
    describe('renders', () => {
        jestSnapshotShallowTest(snapshots);
    });
});
