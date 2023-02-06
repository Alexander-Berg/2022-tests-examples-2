import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import React from 'react';
import { TestExample } from '../promo-modal.stories';

describe('Modal', () => {
    describe('screenshot', () => {
        it('default', async () => {
            await makeScreenshot(<TestExample />, { width: 800, height: 800 });
        });

        it('with image with custom position ', async () => {
            await makeScreenshot(<TestExample withCustomImagePosition />, { width: 800, height: 800 });
        });
    });
});
