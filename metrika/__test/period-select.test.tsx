import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { ForScreenshot } from '../period-select.stories';

describe('PeriodSelect', () => {
    beforeAll(() => {
        jest.useFakeTimers('modern');
        jest.setSystemTime(new Date(2022, 6, 15));
    });

    afterAll(() => {
        jest.useRealTimers();
    });

    it('default', async () => {
        await makeScreenshot(<ForScreenshot />, { width: 400, height: 400 });
    });
});
