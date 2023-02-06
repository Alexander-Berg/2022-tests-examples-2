import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { TestScreenshot } from '@client-libs/mindstorms/components/text-cutter/text-cutter.stories';

describe('markdown', () => {
    describe('screenshot', () => {
        it('clamped', async () => {
            await makeScreenshot(<TestScreenshot />, { width: 700, height: 200 });
        });

        it('opened', async () => {
            await makeScreenshot(<TestScreenshot initialIsClamped={false} />, { width: 700, height: 500 });
        });
    });
});
