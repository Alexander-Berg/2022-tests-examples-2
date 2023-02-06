import simple_schedule from '../../../fixtures/schedule/simple_schedule.json';
import {
    wfmPages,
} from '../../../page-objects';
import {authViaAqua} from  '../../../utils/auth';
import {makeNameForSimpleSchedule} from  '../../../utils/schedule';


const allureReporter = require('@wdio/allure-reporter').default;

describe('schedule.smoke', () => {
    before(async () => {
        await authViaAqua();
    });

    it('should be able to add simple schedule', async () => {
        allureReporter.addTestId('wfm-59');
        await wfmPages.menu.open('/schedules');
        const scheduleName = makeNameForSimpleSchedule(
            simple_schedule.working_days,
            simple_schedule.days_off,
            simple_schedule.start_time,
            simple_schedule.duration_mins,
        );

        await wfmPages.catalogs.schedules.page.checkExistAndRemoveScheduleWithName(scheduleName);

        await wfmPages.catalogs.schedules.page.createSimpleSchedule(
            simple_schedule.start_time,
            simple_schedule.duration_mins,
            simple_schedule.performance_hrs,
            simple_schedule.working_days,
            simple_schedule.days_off,
        );

        expect(await wfmPages.catalogs.schedules.card.copyScheduleBtn).toBeDisplayed();
        expect(await wfmPages.catalogs.schedules.card.removeScheduleBtn).toBeDisplayed();
        expect(await wfmPages.catalogs.schedules.list.isScheduleWithNameExist(scheduleName)).toBe(true);

        await wfmPages.catalogs.schedules.page.removeScheduleWithName(scheduleName);
    });
});
