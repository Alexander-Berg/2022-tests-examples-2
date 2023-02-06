import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotRenderTest } from 'testing/jest-utils';
import { ControlsBar } from '..';

const componentsForSnapshotRenderTest: ReactElementsList = {
    correctly: (
        <ControlsBar size="s">
            {'один'}
            {'два'}
            {'три'}
        </ControlsBar>
    ),
    'incoming className': (
        <ControlsBar size="s" className="className">
            раз
        </ControlsBar>
    ),
};

describe('ControlsBar', () => {
    describe('renders', () => {
        jestSnapshotRenderTest(componentsForSnapshotRenderTest);
    });
});
