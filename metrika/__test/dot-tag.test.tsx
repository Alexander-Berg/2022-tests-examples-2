import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import React from 'react';
import { View } from '@client-libs/mindstorms/components/dot-tag/dot-tag.stories';

describe('DotTag', () => {
    describe('screenshot', () => {
        it('view', async () => {
            await makeScreenshot(<View />);
        });
    });
});
