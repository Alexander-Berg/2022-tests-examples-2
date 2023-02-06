import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { TestExample } from '../horizontal-icon-menu.stories';

describe('horizontal-icon-menu', () => {
    describe('screenshot', () => {
        it('default', async () => {
            await makeScreenshot(<TestExample />, { width: 500, height: 400 });
        });
    });
});
