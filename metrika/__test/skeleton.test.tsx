import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { Main } from '@client-libs/mindstorms/components/skeleton/skeleton.stories';

describe('Skeleton', () => {
    it('default', async () => {
        await makeScreenshot(<Main />, { width: 400, height: 80 });
    });
});
