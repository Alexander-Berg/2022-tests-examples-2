import {Undefinable, findByData, findElement} from '@txi-autotests/ts-utils';

import {setValue} from '../../../utils/setValue';
import {BasePage} from '../base.page';

class ListPage extends BasePage {
    @findByData('employees-filter-fullname')
    public filterByFullName: Undefinable<ReturnType<typeof $>>;

    @findByData('employees-filter-login')
    public filterByLogin: Undefinable<ReturnType<typeof $>>;

    @findByData('employees-filter-supervisors')
    public filterBySupervisors: Undefinable<ReturnType<typeof $>>;

    @findByData('employees-filter-mentor')
    public filterByMentor: Undefinable<ReturnType<typeof $>>;

    @findByData('employees-filter-departments')
    public filterByDepartments: Undefinable<ReturnType<typeof $>>;

    @findElement('[placeholder="Дата найма от"]')
    public filterByDateFrom: Undefinable<ReturnType<typeof $>>;

    @findElement('[placeholder="Дата найма до"]')
    public filterByDateTo: Undefinable<ReturnType<typeof $>>;

    @findByData('employees-filter-tags')
    public filterByTags: Undefinable<ReturnType<typeof $>>;

    @findByData('employees-filter-skills')
    public filterBySkills: Undefinable<ReturnType<typeof $>>;

    @findByData('employees-filter-schedules')
    public filterBySchedules: Undefinable<ReturnType<typeof $>>;

    @findByData('employees-table-fullname-cell')
    public employeeFullName: Undefinable<ReturnType<typeof $>>;

    @findByData('component-header-settings-btn')
    public settingsBtn: Undefinable<ReturnType<typeof $>>;

    async clickSettingsBtn() {
        await this.settingsBtn?.click();
    }

    async getEmployeeFullName(fullName: string) {
        const operatorFullName = await (await this.employeeFullName)?.$('span*=' + fullName);

        await operatorFullName?.waitForDisplayed();
        return operatorFullName;
    }

    async clickEmployeeFullName(fullName: string) {
        const operatorFullName = await this.getEmployeeFullName(fullName);

        await operatorFullName?.click();
    }

    async setFilterByFullName(fullName: string) {
        await setValue(this.filterByFullName, fullName);
    }

    async setFilterByLogin(login: string) {
        await setValue(this.filterByLogin, login);
    }

    async setFilterBySupervisors(supervisor: string) {
        await setValue(this.filterBySupervisors, supervisor);
    }

    async setFilterByMentor(mentor: string) {
        await setValue(this.filterByMentor, mentor);
    }

    async setFilterByDepartments(department: string) {
        await setValue(this.filterByDepartments, department);
    }

    async setFilterByDateFrom(dateFrom: string) {
        await setValue(this.filterByDateFrom, dateFrom);
    }

    async setFilterByDateTo(dateTo: string) {
        await setValue(this.filterByDateTo, dateTo);
    }

    async setFilterByTags(tag: string) {
        await setValue(this.filterByTags, tag);
    }

    async setFilterBySkills(skill: string) {
        await setValue(this.filterBySkills, skill);
    }

    async setFilterBySchedules(schedule: string) {
        await setValue(this.filterBySchedules, schedule);
    }

    async isEmployeeFullNameExist(fullName: string) {
        const operatorFullName = await this.getEmployeeFullName(fullName);

        return operatorFullName?.isExisting();
    }
}

export const listPage = new ListPage();
