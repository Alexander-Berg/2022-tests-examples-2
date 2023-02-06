import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { ForScreenshot } from '../metrics-aux-settings-menu.stories';

describe('MetricsAuxSettingsMenu', () => {
    describe('screenshot', () => {
        it('default', async () => {
            await makeScreenshot(<ForScreenshot />, { width: 400, height: 400 });
        });
    });
});
