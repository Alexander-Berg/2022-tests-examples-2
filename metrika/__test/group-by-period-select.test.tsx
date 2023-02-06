import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { ForScreenshot } from '../group-by-period-interval.stories';

describe('GroupByIntervalSelect', () => {
    it('default', async () => {
        await makeScreenshot(<ForScreenshot />, { width: 400, height: 400 });
    });
});
