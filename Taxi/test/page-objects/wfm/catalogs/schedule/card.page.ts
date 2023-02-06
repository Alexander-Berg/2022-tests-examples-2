import {setValue} from '../../../../utils/setValue';
import {BasePage} from '../../base.page';


class CardPage extends BasePage {
    get simpleScheduleBtn() { return $('[data-cy="schedules-card-card_picker-complexity_simple-button-create"]'); }
    get complexScheduleBtn() { return $('[data-cy="schedules-card-card_picker-complexity_complexity-button-create"]'); }
    get start() { return $('#start'); }
    get durationMinutes() { return $('#duration_minutes'); }
    get performanceStandard() { return $('#performanceStandard'); }
    get workingDays() { return $('#simplePattern_0_odd'); }
    get weekendDays() { return $('#simplePattern_1_even'); }
    get saveScheduleBtn() { return $('button[data-cy="schedules-form-submit"]'); }
    get copyScheduleBtn() { return $('button[data-cy="schedules-form-copy"]'); }
    get removeScheduleBtn() { return $('button[data-cy="schedules-form-remove"]'); }
    get timeOkBtn() { return $('button[class="ant-btn ant-btn-primary ant-btn-sm"]'); }
    get popoverOk() { return $('div.ant-popover-inner-content').$('span=Да'); }
    get notificationClose() { return $('.ant-notification-close-icon'); }
    get filters_modal() { return $('[data-cy="schedules-list-card-more_modal"]'); }
    get simpleScheduleTitle() { return $('[data-cy="schedules-card-card_picker-complexity_simple-picker-title"]'); }
    get complexScheduleTitle() { return $('[data-cy="schedules-card-card_picker-complexity_complexity-picker-title"]'); }
    get complexScheduleHelp() { return $('[data-cy="schedules-card-card_picker-complexity_complexity-picker-title"]'); }

    async clickSaveSchedule() {
        await this.saveScheduleBtn.click();
    }

    async clickCreateSimpleSchedule() {
        await this.simpleScheduleBtn.click();
    }

    async setDuration(mins: string) {
        await setValue(this.durationMinutes, mins);
    }

    async setPerformanceStandardHrs(hrs: string) {
        await setValue(this.performanceStandard, hrs);
    }

    async setWorkingDays(dayCount: string) {
        await setValue(this.workingDays, dayCount);
    }

    async setWeekendDays(dayCount: string) {
        await setValue(this.weekendDays, dayCount);
    }

    async setStart(startTime: string) {
        await this.start.click();
        await setValue(this.start, startTime);
        await this.timeOkBtn.click();
    }

    async createSimpleSchedule(startTime: string, duration: number, perfHrs: number, workDays: number, weekend: number) {
        await this.clickCreateSimpleSchedule();
        await this.setStart(startTime);
        await this.setDuration(duration.toString());
        await this.setPerformanceStandardHrs(perfHrs.toString());
        await this.setWorkingDays(workDays.toString());
        await this.setWeekendDays(weekend.toString());
        await this.clickSaveSchedule();
    }

    async removeSchedule() {
        await this.removeScheduleBtn.click();
        await this.popoverOk.click();
        await this.removeScheduleBtn.waitForDisplayed({reverse: true});
    }

    async closeNotification() {
        await this.notificationClose.click();
    }
}

export const cardPage = new CardPage();
