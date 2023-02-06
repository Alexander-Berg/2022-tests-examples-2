import employee from '../../../fixtures/employees/employee.json';
import {
    wfmPages,
} from '../../../page-objects';
import {authViaAqua} from  '../../../utils/auth';
import {getCurrentMonday, getCurrentSunday} from  '../../../utils/getDate';

const allureReporter = require('@wdio/allure-reporter').default;
const {employees: {card}} = wfmPages;

describe('employee.shifts', () => {
    before(async () => {
        await authViaAqua();
        await wfmPages.menu.open('/employees');
        await wfmPages.employees.page.openEmployeeCard();
        await card.clickTabShifts();
    });

    it('can check employee shifts', async () => {
        allureReporter.addTestId('wfm-69');
        expect (await card.isLoadFormExist()).toBe(true);
        expect (await card.isChartExist()).toBe(true);
        expect (await card.isDistributeFormExist()).toBe(true);
    });

    it('can distribute shift', async () => {
        allureReporter.addTestId('wfm-71');
        await card.chooseSkills(employee.skill);
        await card.clickDistributeShiftsBtn();
        await card.clickOkBtn();
        expect (await card.getSuccessNotification()).toEqual(employee.message);
        expect (await card.getNotification(employee.finalMessage)).toBe(true);
    });

    it('can check load shift', async () => {
        allureReporter.addTestId('wfm-69');
        expect (await card.getValueShiftsDateFrom(employee.attribute)).toEqual(getCurrentMonday());
        expect (await card.getValueShiftsDateTo(employee.attribute)).toEqual(getCurrentSunday());
    });

    it('can load shift', async () => {
        allureReporter.addTestId('wfm-70');
        await card.clickShiftsLoadBtn();
        expect (await card.isSkillColumnExist(employee.skill)).toBe(true);
        expect (await card.isShiftExist(employee.shift)).toBe(true);
    });
});
