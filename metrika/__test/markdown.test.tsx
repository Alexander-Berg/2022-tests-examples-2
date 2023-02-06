import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { Component, CustomStyles } from '@client-libs/mindstorms/components/markdown/markdown.stories';

describe('markdown', () => {
    it('default screenshot', async () => {
        await makeScreenshot(<Component />, { width: 1000, height: 1200 });
    });

    it('custom styles screenshot', async () => {
        await makeScreenshot(<CustomStyles />, { width: 1000, height: 1200 });
    });
});
