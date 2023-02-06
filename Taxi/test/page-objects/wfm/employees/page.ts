import employee from '../../../fixtures/employees/employee.json';
import {BasePage} from '../base.page';

import {listPage} from './list.page';

class WholePage extends BasePage {
    async openEmployeeCard() {
        await listPage.setFilterByFullName(employee.fullName);
        expect(await listPage.isEmployeeFullNameExist(employee.fullName)).toBe(true);
        await listPage.clickEmployeeFullName(employee.fullName);
    }
}

export const wholePage = new WholePage();
