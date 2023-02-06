import {clearValue, setValue} from '../../../../utils/setValue';
import {BasePage} from '../../base.page';

class ListPage extends BasePage {
    get addScheduleBtn() { return $('button[data-cy="schedules-list-card-title_add-button"]'); }
    get showArchived() { return $('[data-cy="schedules-list-card-title_show-archive"]'); }
    get searchInput() { return $('[data-cy="schedules-list-card-filters_input"]'); }
    get emptyListPlaceholder() { return $('div.ant-list-empty-text'); }
    get scheduleItemsList() { return $('ul.ant-list-items'); }
    get scheduleItem() { return $('[data-cy="schedules-list-item"]'); }
    get scheduleItems() { return $$('[data-cy="schedules-list-item"]'); }
    get inputFilterOptions() { return $('[data-cy="schedules-list-card-filters_more-filters-button"]'); }
    get clearFilters() { return $('[data-cy="schedules-list-card-filters_clear-filters-button"]'); }
    get badge() { return $('[data-cy="schedules-list-card-title_counter"]'); }

    async clickAddSchedule() {
        await this.addScheduleBtn.click();
    }

    async clickShowArchived() {
        await this.showArchived.click();
    }

    async setSearchInput(s: string) {
        await setValue(this.searchInput, s);
    }

    async scheduleItemWithName(name: string) {
        return this.scheduleItem.$('span=' + name);
    }

    async showArchivedSchedules() {
        if (! await this.isShowArchivedOn()) {
            await this.clickShowArchived();
        }
    }

    async isScheduleWithNameExist(name: string) {
        await this.setSearchInput(name);
        try {
            const el = await this.scheduleItemWithName(name);

            await el.waitForDisplayed();
            return true;
        } catch (error) {
            return false;
        }
    }

    async isShowArchivedOn() {
        return await this.showArchived.getAttribute('aria-checked') === 'true';
    }

    async clickOnScheduleWithName(name: string) {
        const el = await this.scheduleItemWithName(name);

        await el.click();
    }

    async clearInput(scheduleName: string) {
        await clearValue(scheduleName);
    }
}

export const listPage = new ListPage();
