import Page from './Page';

class EmployeesPage extends Page {
    clickAddEmployeeBtn() {
        cy.xpath('(//*[@placeholder="Поиск по сотрудникам"]/../../../..//button)[1]').click();
        return this;
    }

    typeName(name) {
        cy.get('[name="fullname"]').clear().type(name);
        return this;
    }

    typePhone(phone) {
        cy.get('[placeholder="+7 (912) 345 67 89"]').type(phone);
        return this;
    }

    typeEmail(email) {
        cy.get('[name="email"]').clear().type(email);
        return this;
    }

    typeID(id) {
        cy.get('[name="nickname"]').type(id);
        return this;
    }

    /**
     * Если не передан цз, то выбирается первый из выпадашки
     */
    selectCostCenter(costCenter) {
        cy.get('input[name="cost_centers_id"]').click();
        if (costCenter) {
            cy.xpath(`//*[text()="${costCenter}"]`).click();
        } else {
            cy.get('[data-option-index="0"').click();
        }
        return this;
    }

    /**
     * Если не передано подразделение, то выбирается первое из выпадашки
     */
    selectDepartment(department) {
        cy.get('input[name="department_id"]').click();
        if (department) {
            cy.xpath(`//*[text()="${department}"]`).click();
        } else {
            cy.get('[data-option-index="0"').click();
        }
        return this;
    }

    fillEmployeeFields(user) {
        this.clickAddEmployeeBtn()
            .typeName(user.name)
            .typePhone(user.phone)
            .typeEmail(user.email)
            .typeID(user.id)
            .selectCostCenter();
        return this;
    }

    openEmployee(name, forceClick = false) {
        cy.xpath(`//*[text()="${name}"]`).click({force: forceClick});
        cy.get('[name="fullname"]').should('be.visible');
        return this;
    }

    clickDeleteBtn() {
        cy.xpath('//*[text()="Сохранить"]/../../..//*[name()="svg"]').click();
        return this;
    }

    clickRestoreBtn() {
        cy.xpath('//form//*[text()="Восстановить"]').click();
        return this;
    }

    searchEmployee(text) {
        cy.get('[name="search"]').type(text);
        return this;
    }

    openOrderHistory() {
        cy.xpath('//*[text()="Посмотреть всю историю"]').click();
    }
}

export default EmployeesPage;
