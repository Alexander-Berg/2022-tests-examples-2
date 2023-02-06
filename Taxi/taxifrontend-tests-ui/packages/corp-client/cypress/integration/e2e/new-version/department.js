describe('Подразделения (Новые лимиты)', () => {
    const corpUser = 'autotestcorp-newVersion';

    function clickSettings(name, settings) {
        cy.xpath(`//*[contains(text(), '${name}')]`).should('exist');
        cy.xpath(`//div/*[contains(text(), '${name}')]//following-sibling::div/div`).click();
        cy.xpath(`//div/*[contains(text(), '${settings}')]`).click();
    }

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('v2/staff');
        cy.intercept('DELETE', '/api/1.0/client/*/department/*').as('departmentDelete');
        cy.intercept('/api/1.0/client/*/department').as('department');
        cy.intercept('/api/1.0/client/*/department/*').as('departmentRename');
    });

    it('corptaxi-887: Добавление нового подразделения. Вкладка Сотрудники (Без лимита)', () => {
        const departmentName = 'department' + Date.now();

        cy.get('[title="Добавить подразделение"]').click();
        cy.get('[name="department.name"]').type(departmentName);
        cy.get('[type="submit"]').click();

        // Проверяем подразделение
        cy.wait('@department');

        clickSettings(departmentName, 'Редактировать');

        cy.get('[name="department.name"]').should('have.value', departmentName);
        cy.xpath(`(//label[text()='Лимит']/following::input)[1]`).should('be.disabled');

        // Удаление подразделения
        cy.get('.EditorModalFooterSection__remove', {timeout: 10000}).click();
        cy.get('span')
            .contains(`Точно хотите удалить департамент «${departmentName}»?`)
            .should('exist');
        cy.get('button').contains('Удалить').click();
        cy.wait('@departmentDelete');
        cy.xpath(`//div[contains(text(),'${departmentName}')]`, {timeout: 10000}).should(
            'not.exist'
        );
    });

    it('corptaxi-950: Создание/редактирование/удаление подгруппы (С лимитом)', () => {
        const departmentName = 'nameSubGroup' + Date.now();
        const departmentSubGroup = 'depSubGroup';
        const limit = '11';

        clickSettings(departmentSubGroup, 'Добавить подгруппу');

        cy.get('[name="department.name"]').type(departmentName);
        cy.get('.Limit').type(limit);
        cy.get('[type="submit"]').click();

        //Редактирование подгруппы
        cy.wait('@department');
        cy.xpath(`(//div[text()='${departmentSubGroup}'][1])`).click();

        clickSettings(departmentName, 'Редактировать');

        cy.get('[name="department.name"]')
            .clear()
            .type(departmentName + '-rn');
        cy.get('.Limit')
            .click()
            .type(limit + '2');

        // Проверяем расположение подгруппы
        cy.xpath(`//*[@class="Select-value-label"][text()='${departmentSubGroup}']`).should(
            'exist'
        );
        cy.get('[type="submit"]').click();

        // Проверка изменений
        cy.wait('@departmentRename');

        clickSettings(departmentName + '-rn', 'Редактировать');

        cy.get('[name="department.name"]').should('have.value', departmentName + '-rn');
        cy.xpath(`((//label[text()='Лимит'])/following::input)[1]`).should(
            'have.value',
            limit + '2'
        );

        // Удаляем подгруппу
        cy.get('.EditorModalFooterSection__remove', {timeout: 10000}).click();
        cy.get('span')
            .contains(`Точно хотите удалить департамент «${departmentName + '-rn'}»?`)
            .should('exist');
        cy.get('button').contains('Удалить').click();
        cy.wait('@departmentDelete');
        cy.xpath(`//div[contains(text(),'${departmentName + '-rn'}')]`, {timeout: 10000}).should(
            'not.exist'
        );
    });
});
