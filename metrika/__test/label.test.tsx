import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import React from 'react';
import { View } from '@client-libs/mindstorms/components/label/label.stories';

describe('Label', () => {
    describe('screenshot', () => {
        it('view', async () => {
            await makeScreenshot(<View />);
        });
    });
});
