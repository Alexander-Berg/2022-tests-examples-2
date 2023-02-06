import React from 'react';
import { makeScreenshot } from '@client-libs/test-utils/screenshot';
import { Default, IsLoading } from '../dashboard-settings.stories';

describe('DashboardSettings', () => {
    beforeAll(() => {
        jest.useFakeTimers('modern');
        jest.setSystemTime(new Date(2022, 3, 24));
    });

    afterAll(() => {
        jest.useRealTimers();
    });

    it('default', async () => {
        await makeScreenshot(<Default />, { width: 400, height: 400 });
    });
    it('IsLoading', async () => {
        await makeScreenshot(<IsLoading />, { width: 400, height: 400 });
    });
});
