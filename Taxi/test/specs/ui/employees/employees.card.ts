import employee from '../../../fixtures/employees/employee.json';
import {
    wfmPages,
} from '../../../page-objects';
import {authViaAqua} from  '../../../utils/auth';

const allureReporter = require('@wdio/allure-reporter').default;
const {employees: {card}} = wfmPages;

describe('employee.card', () => {
    before(async () => {
        await authViaAqua();
        await wfmPages.menu.open('/employees');
        await wfmPages.employees.page.openEmployeeCard();
    });

    it('can check employee common info', async () => {
        allureReporter.addTestId('wfm-68');
        expect(await card.getFullNameEqual()).toEqual(employee.nameTitle);
        expect(await card.isLoginExist(employee.login)).toBe(true);
        expect(await card.isSupervisorExist(employee.supervisor)).toBe(true);
        expect(await card.isMentorExist(employee.mentor)).toBe(true);
        expect(await card.isStateExist(employee.state)).toBe(true);
        expect(await card.isDepartmentExist(employee.department)).toBe(true);
        expect(await card.isScheduleExist(employee.schedule)).toBe(true);
        expect(await card.isSkillExist(employee.skill)).toBe(true);
        expect(await card.isEmploymentDateExist(employee.employmentData)).toBe(true);
        expect(await card.isTimezoneExist(employee.timezone)).toBe(true);
    });
    it('can add employee tags', async () => {
        allureReporter.addTestId('wfm-68');
        await card.clickOperatorTagsEdit();
        await card.clickOperatorTags();
        await card.setOperatorTags(employee.tag);
        await card.clickOperatorTagsSave();
        expect (await card.isOperatorTagsExist(employee.tag)).toBe(true);
    });
    it('can delete employee tags', async () => {
        allureReporter.addTestId('wfm-68');
        await card.clickOperatorTagsEdit();
        await card.deleteOperatorTags(employee.tag);
        await card.clickOperatorTagsSave();
        expect (await card.isOperatorTagsExist(employee.tag)).toBe(false);
    });
    it('can add employee notes', async () => {
        allureReporter.addTestId('wfm-68');
        await card.clickOperatorNotesEdit();
        await card.setOperatorNotes(employee.note);
        await card.clickOperatorNotesSave();
        expect (await card.isOperatorNotesExist(employee.note)).toBe(true);
    });
    it.skip('can delete employee notes', async () => {
        allureReporter.addTestId('wfm-68');
        await card.clickOperatorNotesEdit();
        await card.clearOperatorNotes();
        await card.clickOperatorNotesSave();
        expect (await card.isOperatorNotesExist(employee.note)).toBe(false);
    });
});
