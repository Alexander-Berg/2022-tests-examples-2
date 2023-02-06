import {Undefinable, findByData, findElement} from '@txi-autotests/ts-utils';

import {clearValue, addValue, setValue} from '../../../utils/setValue';
import {sleep} from '../../../utils/sleep';
import {BasePage} from '../base.page';

class CardPage extends BasePage {
    @findByData('components_employee-card-card_header_title')
    public operatorFullName: Undefinable<ReturnType<typeof $>>;

    @findElement('#rc-tabs-1-tab-chart')
    public tabShifts: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-chart-filter')
    public shiftsLoadForm: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-chart-view')
    public shiftsChart: Undefinable<ReturnType<typeof $>>;

    @findByData('shifts-planning-employee-card-shifts-tab-setup-shifts-skills-picker')
    public skillsShifts: Undefinable<ReturnType<typeof $>>;

    @findByData('shifts-planning-employee-card-shifts-tab-setup-shifts-auto')
    public distributeShiftsBtn: Undefinable<ReturnType<typeof $>>;

    @findElement('[class="ant-btn ant-btn-primary ant-btn-sm"]')
    public okBtn: Undefinable<ReturnType<typeof $>>;

    @findElement('#rc-tabs-1-tab-schedules')
    public tabSchedules: Undefinable<ReturnType<typeof $>>;

    @findElement('.ant-card-grid sc-eWfVMQ jzpiWm ant-card-grid-hoverable')
    public addScheduleBtn: Undefinable<ReturnType<typeof $>>;

    @findByData('component-apply-schedule-form-skills-picker')
    public selectSkill: Undefinable<ReturnType<typeof $>>;

    @findByData('component-apply-schedule-form-schedule-picker')
    public selectSchedule: Undefinable<ReturnType<typeof $>>;

    @findByData('component-apply-schedule-form-save')
    public saveScheduleBtn: Undefinable<ReturnType<typeof $>>;

    @findElement('#schedule_offset')
    public selectOffset: Undefinable<ReturnType<typeof $>>;

    @findElement('#rc-tabs-1-tab-absences')
    public tabAbsences: Undefinable<ReturnType<typeof $>>;

    @findElement('#rc-tabs-1-tab-violations')
    public tabDiscipline: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_login')
    public operatorLogin: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_supervisor')
    public operatorSupervisor: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_mentor')
    public operatorMentor: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_state')
    public operatorState: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_department')
    public operatorDepartment: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_active-schedule')
    public operatorSchedule: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_employment-date')
    public operatorEmploymentData: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_timezone')
    public operatorTimezone: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_tags_read-mode')
    public operatorTags: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_tags_edit-mode')
    public operatorTagsActive: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_comment_read-mode')
    public operatorNotes: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_comment_edit-mode')
    public operatorNotesActive: Undefinable<ReturnType<typeof $>>;

    @findByData('components_employee-card-card_common-info_skills')
    public operatorSkills: Undefinable<ReturnType<typeof $>>;

    @findElement('[class="ant-notification ant-notification-topRight"]')
    public topRightNotification: Undefinable<ReturnType<typeof $>>;

    @findElement('[class="ant-message"]')
    public topNotification: Undefinable<ReturnType<typeof $>>;

    async clickTabShifts() {
        const tabShifts = await this.tabShifts;

        await tabShifts?.click();
    }

    async clickDistributeShiftsBtn() {
        const distributeBtn = await this.distributeShiftsBtn;

        await distributeBtn?.click();
    }

    async clickOkBtn() {
        const ok = await this.okBtn;

        await ok?.click();
    }

    async clickSkillsShifts() {
        const skill = await this.skillsShifts;

        await skill?.click();
    }

    async inputSkill() {
        return await (await this.skillsShifts)?.$('input');
    }

    async chooseSkills(skill: string) {
        const inputSkill = await this.inputSkill();

        await this.clickSkillsShifts();

        await setValue(inputSkill, skill);

        await browser.keys('Enter');
    }

    async getSuccessNotification()  {
        const successNotification = await (await this.topRightNotification)?.$('div.ant-notification-notice-message');

        await successNotification?.waitForDisplayed();

        return successNotification?.getText();
    }

    async getNotification(message: string)  {
        const successNotification = await (await this.topNotification)?.$('span*='+message);

        await successNotification?.waitForDisplayed();

        return successNotification?.isExisting();
    }

    async clickTabSchedules() {
        await this.tabSchedules?.click();
    }

    async clickTabAbsences() {
        await this.tabAbsences?.click();
    }

    async clickTabDiscipline() {
        await this.tabDiscipline?.click();
    }

    async clickAddScheduleBtn() {
        await this.addScheduleBtn?.click();
    }

    async clickSaveScheduleBtn() {
        await this.saveScheduleBtn?.click();
    }

    async setSelectSkill(skill: string) {
        await setValue(this.selectSkill, skill);
    }

    async setSelectSchedule(schedule: string) {
        await setValue(this.selectSchedule, schedule);
    }

    async setSelectOffset(offset: string) {
        await setValue(this.selectOffset, offset);
    }

    async getFullNameEqual() {
        const operatorFullName = await this.operatorFullName;

        await operatorFullName?.waitForDisplayed();

        return operatorFullName?.getText();
    }

    async isLoginExist(login: string) {
        const operatorLogin = await (await this.operatorLogin)?.$('span*=' + login);

        await operatorLogin?.waitForDisplayed();

        return operatorLogin?.isExisting();
    }

    async isSupervisorExist(supervisor: string) {
        const operatorSupervisor = await (await this.operatorSupervisor)?.$('span*=' + supervisor);

        await operatorSupervisor?.waitForDisplayed();

        return operatorSupervisor?.isExisting();
    }

    async isMentorExist(mentor: string) {
        const operatorMentor = await (await this.operatorMentor)?.$('span*=' + mentor);

        await operatorMentor?.waitForDisplayed();

        return operatorMentor?.isExisting();
    }

    async isStateExist(state: string) {
        const operatorState = await (await this.operatorState)?.$('span*=' + state);

        await operatorState?.waitForDisplayed();

        return operatorState?.isExisting();
    }

    async isDepartmentExist(department: string) {
        const operatorDepartment = await (await this.operatorDepartment)?.$('span*=' + department);

        await operatorDepartment?.waitForDisplayed();

        return operatorDepartment?.isExisting();
    }

    async isScheduleExist(schedule: string) {
        const operatorSchedule = await (await this.operatorSchedule)?.$('span*=' + schedule);

        await operatorSchedule?.waitForDisplayed();

        return operatorSchedule?.isExisting();
    }

    async isSkillExist(skill: string) {
        const operatorSkill = await (await this.operatorSkills)?.$('span*=' + skill);

        await operatorSkill?.waitForDisplayed();

        return operatorSkill?.isExisting();
    }

    async isEmploymentDateExist(employmentData: string) {
        const operatorEmploymentData = await (await this.operatorEmploymentData)?.$('span*=' + employmentData);

        await operatorEmploymentData?.waitForDisplayed();

        return operatorEmploymentData?.isExisting();
    }

    async isTimezoneExist(timezone: string) {
        const operatorTimezone = await (await this.operatorTimezone)?.$('span*=' + timezone);

        await operatorTimezone?.waitForDisplayed();

        return operatorTimezone?.isExisting();
    }

    async clickOperatorTagsEdit() {
        const operatorTagsEdit = await (await this.operatorTags)?.$('svg');

        await operatorTagsEdit?.click();
    }

    async inputOperatorTags() {
        return await (await this.operatorTagsActive)?.$('input');
    }

    async clickOperatorTags() {
        const operatorTagsEdit = await this.inputOperatorTags();

        await operatorTagsEdit?.click();
    }

    async setOperatorTags(tag: string) {
        const inputOperatorTags = await this.inputOperatorTags();

        await addValue(inputOperatorTags, tag);

        await browser.keys('Enter');
    }

    async operatorTagsSave(){
        return await (await this.operatorTagsActive)?.$('svg[data-icon="check"]');
    }

    async clickOperatorTagsSave(){
        const operatorTagsSave = await this.operatorTagsSave();

        await operatorTagsSave?.click();

        await sleep(10000); // убрать после обновления бекенда
    }

    async clickOperatorNotesEdit() {
        const operatorNotesEdit = await (await this.operatorNotes)?.$('svg');

        await operatorNotesEdit?.click();
    }

    async isOperatorTagsExist(tag: string) {
        await browser.refresh(); // возможно, тоже можно будет убрать после обновления бекенда

        const operatorTags = await (await this.operatorTags)?.$('span*=' + tag);

        return operatorTags?.isExisting();
    }

    async deleteOperatorTags(tag: string) {
        const operatorTagsDelete = await (await this.operatorTagsActive)?.$('span*=' + tag).$('svg[data-icon="close"]');

        await operatorTagsDelete?.click();
    }

    async inputOperatorNotes() {
        return await (await this.operatorNotesActive)?.$('textarea');
    }

    async setOperatorNotes(note: string) {
        const inputOperatorNotes = await this.inputOperatorNotes();

        await setValue(inputOperatorNotes, note);
    }

    async operatorNotesSave() {
        return await (await this.operatorNotesActive)?.$('svg');
    }

    async clickOperatorNotesSave() {
        const operatorNotesSave = await this.operatorNotesSave();

        await operatorNotesSave?.click();
    }

    async isOperatorNotesExist(note: string) {
        const operatorNotes = await (await this.operatorNotes)?.$('p*=' + note);

        await operatorNotes?.waitForDisplayed();

        return operatorNotes?.isExisting();
    }

    async clearOperatorNotes() {
        const inputOperatorNotes = await this.inputOperatorNotes();

        await clearValue(inputOperatorNotes);
    }

    async shiftsLoadBtn() {
        return await (await this.shiftsLoadForm)?.$('[class="ant-btn ant-btn-primary"]');
    }

    async clickShiftsLoadBtn() {
        const shiftsLoadBtn = await this.shiftsLoadBtn();

        await shiftsLoadBtn?.click();
    }

    async clickShiftsDateFrom() {
        const shiftsDateFrom = await this.shiftsDateFrom();

        await shiftsDateFrom?.click();
    }

    async clickShiftsDateTo() {
        const shiftsDateTo = await this.shiftsDateTo();

        await shiftsDateTo?.click();
    }

    async shiftsDateFrom() {
        return await (await this.shiftsLoadForm)?.$('[placeholder="Начало (дата)"]');
    }

    async isShiftsDateFromExist() {
        const shiftsDateFrom = await this.shiftsDateFrom();

        await shiftsDateFrom?.waitForDisplayed();

        return shiftsDateFrom?.isExisting();
    }

    async shiftsDateTo() {
        return await (await this.shiftsLoadForm)?.$('[placeholder="Конец (дата)"]');
    }

    async isShiftsDateToExist() {
        const shiftsDateTo = await this.shiftsDateTo();

        await shiftsDateTo?.waitForDisplayed();

        return shiftsDateTo?.isExisting();
    }

    async getValueShiftsDateFrom(value: string) {
        const shiftsDateFrom = await this.shiftsDateFrom();

        await shiftsDateFrom?.waitForDisplayed();

        return shiftsDateFrom?.getAttribute(value);
    }

    async getValueShiftsDateTo(value: string) {
        const shiftsDateTo = await this.shiftsDateTo();

        await shiftsDateTo?.waitForDisplayed();

        return shiftsDateTo?.getAttribute(value);
    }

    async isShiftsLoadBtnExist() {
        const shiftsLoadBtn = await this.shiftsLoadBtn();

        await shiftsLoadBtn?.waitForDisplayed();

        return shiftsLoadBtn?.isExisting();
    }

    async isSkillsShiftsExist() {
        const skillList = await this.skillsShifts;

        await skillList?.waitForDisplayed();

        return skillList?.isExisting();
    }

    async isDistributeShiftsBtnExist() {
        const distributeBtn = await this.distributeShiftsBtn;

        await distributeBtn?.waitForDisplayed();

        return distributeBtn?.isExisting();
    }

    async isLoadFormExist() {
        const dateFrom = await this.isShiftsDateFromExist();
        const dateTo = await this.isShiftsDateToExist();
        const button = await this.isShiftsLoadBtnExist();

        if(dateFrom && dateTo && button) {
            return true;
        } else {
            return false;
        }
    }

    async isChartExist() {
        const chart = await this.shiftsChart;

        await chart?.waitForDisplayed();

        return chart?.isExisting();
    }

    async isDistributeFormExist() {
        const skills = await this.isSkillsShiftsExist();
        const button = await this.isDistributeShiftsBtnExist();

        if(skills && button) {
            return true;
        } else {
            return false;
        }
    }

    async isSkillColumnExist(skill: string) {
        const skillColumn = await (await this.shiftsChart)?.$('[class="skill-column"]='+ skill);

        await skillColumn?.waitForDisplayed();

        return skillColumn?.isExisting();
    }

    async isShiftExist(schedule: string) {
        const shift = await (await this.shiftsChart)?.$('[class="item shift-item-primary"]='+ schedule);

        await shift?.waitForDisplayed();

        return shift?.isExisting();
    }
}

export const cardPage = new CardPage();
