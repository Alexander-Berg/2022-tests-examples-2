import {BasePage} from '../../base.page';

import {cardPage} from './card.page';
import {listPage} from './list.page';



class WholePage extends BasePage {
    async createSimpleSchedule(startTime: string, duration: number, perfHrs: number, workDays: number, weekend: number) {
        await listPage.clickAddSchedule();
        await cardPage.createSimpleSchedule(
            startTime,
            duration,
            perfHrs,
            workDays,
            weekend,
        );
    }
    async removeScheduleWithName(scheduleName: string) {
        await listPage.clickOnScheduleWithName(scheduleName);
        await cardPage.removeSchedule();
    }

    async checkExistAndRemoveScheduleWithName(scheduleName: string) {
        await listPage.showArchivedSchedules();
        if (await listPage.isScheduleWithNameExist(scheduleName)) {
            await this.removeScheduleWithName(scheduleName);
            await listPage.clearInput(scheduleName);
        }
    }
}

export const wholePage = new WholePage();
