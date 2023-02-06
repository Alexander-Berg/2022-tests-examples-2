import allureReporter from '@wdio/allure-reporter';

import {mobileConstructorPages} from '../../../page-objects';
import {authViaAqua} from  '../../../utils/auth';

describe('schedule.smoke', () => {
    before(async () => {
        await authViaAqua();
    });

    it('should be able to add simple schedule', async () => {
        allureReporter.addTestId('testId-12');

        await mobileConstructorPages.create.open('/settings/data-sources');
    });
});
