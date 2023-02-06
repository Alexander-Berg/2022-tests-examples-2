import employee from '../../../fixtures/employees/employee.json';
import {
    wfmPages,
} from '../../../page-objects';
import {authViaAqua} from  '../../../utils/auth';

const allureReporter = require('@wdio/allure-reporter').default;
const {employees: {card, list}} = wfmPages;

describe('employees.smoke', () => {
    before(async () => {
        await authViaAqua();
    });

    it('can check employee', async () => {
        allureReporter.addTestId('wfm-19');
        await wfmPages.menu.open('/employees');
        await list.setFilterByFullName(employee.fullName);
        expect(await list.isEmployeeFullNameExist(employee.fullName)).toBe(true);
        await list.clickEmployeeFullName(employee.fullName);
        expect(await card.getFullNameEqual()).toEqual(employee.nameTitle);
    });
});
