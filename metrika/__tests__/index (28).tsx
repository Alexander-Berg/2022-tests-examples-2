import * as React from 'react';
import { ReactElementsList } from 'typings/react';
import { jestSnapshotRenderTest } from 'testing/jest-utils';
import { WrapLinks } from '..';

const componentsForSnapshotRenderTest: ReactElementsList = {
    empty: <WrapLinks text="" legoLinkProps={{ theme: 'normal' }} />,
    'with text': (
        <WrapLinks
            text="one two http://fadfa.com three https://fasfa"
            legoLinkProps={{ theme: 'normal' }}
        />
    ),
};

describe('WrapLinks', () => {
    describe('renders', () => {
        jestSnapshotRenderTest(componentsForSnapshotRenderTest);
    });
});
