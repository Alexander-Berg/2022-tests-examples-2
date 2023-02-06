import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { Main } from '@client-libs/mindstorms/components/copyright/copyright.stories';

describe('copyright', () => {
    it('screenshot', async () => {
        await makeScreenshot(<Main />);
    });
});
