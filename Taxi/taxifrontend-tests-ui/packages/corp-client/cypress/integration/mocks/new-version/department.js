import deptData from '../../../fixtures/responses/department/all-departments.json';

describe('Подразделения (Новый функционал)', () => {
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

        cy.intercept('POST', '/api/1.0/search/departments', {
            fixture: 'responses/department/all-departments.json'
        }).as('allDepartments');

        cy.get('[title="Добавить подразделение"]').as('addDepartments');
    });

    it('corptaxi-951: Открытие формы создания подразделения', () => {
        cy.get('@addDepartments').click();
        cy.get('.DepartmentForm').should('exist');
    });

    // https://st.yandex-team.ru/QAWEBTAXI-250
    it.skip('corptaxi-952: Открытие формы создания подразделения в подгруппе', () => {
        cy.xpath(`//*[contains(text(), '${deptData.departments[3].name}')]`).click();

        clickSettings(deptData.departments[0].name, 'Добавить подгруппу');

        cy.xpath(
            `//*[@class="Select-value-label"][text()='${deptData.departments[0].name}']`
        ).should('exist');
    });

    it('corptaxi-431: Пустое поле Лимит. Форма Добавление подразделения', () => {
        const departmentName = 'manual department';

        cy.intercept('POST', '/api/1.0/client/*/department', {
            _id: '123456789'
        }).as('saveDepartments');

        cy.get('@addDepartments').click();
        cy.get('[name="department.name"]').type(departmentName);
        cy.get('[type="submit"]').click();

        cy.wait('@saveDepartments')
            .its('request.body')
            .then(xhr => {
                expect(xhr).to.deep.equal({
                    counters: {users: 0},
                    name: departmentName,
                    parent_id: null
                });
            });

        cy.xpath(`//*[contains(text(), '${departmentName}')]`).should('exist');
    });

    it('corptaxi-953: Создание подгруппы с выбором подразделения (с лимитом)', () => {
        const departmentName = 'manual department';
        const limit = '11';

        cy.intercept('POST', '/api/1.0/client/*/department', {
            _id: '123456789'
        }).as('saveDepartments');

        cy.get('@addDepartments').click();
        cy.get('[name="department.name"]').type(departmentName);
        cy.get('.Select-input').click();
        cy.get('.Select-menu-outer').contains(deptData.departments[3].name).click();
        cy.get('.Limit').type(limit);
        cy.get('[type="submit"]').click();

        cy.wait('@saveDepartments')
            .its('request.body')
            .then(xhr => {
                expect(xhr).to.deep.equal({
                    counters: {users: 0},
                    limit: {budget: 11},
                    name: departmentName,
                    parent_id: deptData.departments[3]._id
                });
            });
        cy.xpath(`//*[contains(text(), '${deptData.departments[3].name}')]`).click();
        cy.xpath(`//*[contains(text(), '${departmentName}')]`).should('exist');
    });

    it('corptaxi-949: Удаление подразделения', () => {
        const clientId = '2a0e22ef61894364bfe4c951f6f7c2a0';

        cy.intercept(
            'DELETE',
            `/api/1.0/client/${clientId}/department/${deptData.departments[1]._id}`,
            {
                body: {}
            }
        ).as('deleteDepartments');

        clickSettings(deptData.departments[1].name, 'Редактировать');

        cy.get('.EditorModalFooterSection__remove').click();
        cy.get('span')
            .contains(`Точно хотите удалить департамент «${deptData.departments[1].name}»?`)
            .should('exist');
        cy.get('button').contains('Удалить').click();

        cy.wait('@deleteDepartments', {timeout: 10000})
            .its('request.url')
            .then(xhr => {
                expect(xhr).contains(
                    `/api/1.0/client/${clientId}/department/${deptData.departments[1]._id}`
                );
            });

        cy.xpath(`//div[contains(text(),'${deptData.departments[1].name}')]`).should('not.exist');
    });

    it('corptaxi-954: Изменение центра затрат для подразделения. Вкладка Сотрудники', () => {
        const clientId = '2a0e22ef61894364bfe4c951f6f7c2a0';
        const cost_centers_id = '4ab0886e197f4a73802e03bcc9e1ff7d';

        cy.intercept('POST', `/api/1.0/client/${clientId}/department_users/update_cost_centers`, {
            body: {}
        }).as('saveCostCenter');

        clickSettings(deptData.departments[1].name, 'Редактировать');

        cy.get('[tabindex="1"]').contains('Центры затрат').click();
        cy.get('.Select-control').click();
        cy.get('.Select-menu-outer').contains('Основной центр затрат').click();
        cy.get('.amber-button').click();

        cy.wait('@saveCostCenter')
            .its('request.body')
            .then(xhr => {
                expect(xhr).to.deep.equal({
                    cost_centers_id: cost_centers_id,
                    department_id: deptData.departments[1]._id
                });
            });
    });
});
