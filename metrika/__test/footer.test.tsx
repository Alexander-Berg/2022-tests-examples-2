import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { Main } from '@client-libs/mindstorms/components/footer/footer.stories';

describe('footer', () => {
    it('screenshot', async () => {
        await makeScreenshot(<Main />, { width: 1000, height: 200 });
    });
});
