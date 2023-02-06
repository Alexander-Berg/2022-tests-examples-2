import profileData from './data/profile-roles.json';

describe('Подразделения', () => {
    context('Простые проверки формы подразделения', () => {
        const corpUser = 'autotestcorp-departments';
        const departmentName = 'departmentName';
        const departmentId = 'd5cc9e709f4946b38156248b5829eda7';

        beforeEach(() => {
            cy.yandexLogin(corpUser);
            cy.prepareLocalStorage();
            cy.corpOpen('/staff');
            cy.server();
            cy.route('/api/1.0/client/*/department?limit=1000').as('departments');
            cy.route({
                url: '/api/1.0/client/*/department/*',
                method: 'DELETE'
            }).as('departmentDelete');
            cy.intercept('/api/1.0/client/*/department').as('department');
        });

        it('corptaxi-938: Открытие формы создания подразделения из сайдбара', () => {
            cy.get('.MuiIconButton-label > svg', {timeout: 10000}).click();
            cy.get('.MuiList-root > [tabindex="-1"]').contains('Добавить подразделение').click();
            cy.get('.DepartmentForm').should('exist');
        });

        it('corptaxi-940: Открытие формы создания подразделения из шапки', () => {
            cy.get('.ControlGroup', {timeout: 10000}).contains('Подразделение').click();
            cy.get('.DepartmentForm').should('exist');
        });

        it('corptaxi-942: Форма создания подразделения из подразделения', () => {
            cy.visit(`/staff/departments/${departmentId}#department/add`);
            cy.get('.DepartmentForm .Select-value-label').should('contain', departmentName);
        });

        it('corptaxi-536: Добавление подразделения. Вкладка Сотрудники (и удаление)', () => {
            const departmentName = 'create and delete dep' + Date.now();

            cy.get('.ControlGroup', {timeout: 10000}).contains('Подразделение').click();
            cy.get('[name="department.name"]').type(departmentName);
            cy.xpath('//*[text()="Без лимита"]').click();
            cy.xpath('//*[text()="Лимит"]/../..//input[@type="text"]').type('50000');
            cy.get('[type="submit"]').click();

            // Удаление подразделения
            cy.wait('@department').then(res => {
                cy.xpath(`//*[contains(text(), '${departmentName}')]`).should('exist');

                const departmentDelId = res.response.body._id;

                cy.get(`[href="/staff/departments/${departmentDelId}"] > div`, {timeout: 10000}).as(
                    'departmentItem'
                );
                cy.get('@departmentItem').nhover();
                cy.get(
                    `[href="/staff/departments/${departmentDelId}"] > div > div > button:last-child`
                ).click();
                cy.get('.EditorModalFooterSection__remove', {timeout: 10000}).click();
                cy.get('.ConfirmModalFooter__ok').click();
                cy.wait('@departmentDelete');

                cy.xpath(`//div[contains(text(),'${departmentName}')]`, {timeout: 10000}).should(
                    'not.exist'
                );
            });
        });
    });


    context('Создание подразделений с ответственными', () => {
        function waitCreateRole() {
            cy.log('Нужно подождать сохранение роли на бэке');
            cy.wait(3000);
            cy.corpOpen('/profile/managers/');
            cy.wait('@depSearch');
        }

        const corpUser = 'autotestcorp-departments';
        let depResponsible;
        const depResponsibleSub = Date.now() + 'parent-department';
        const depResponsibleParent = Date.now() + 'sub-department';

        before(() => {
            cy.removeAllRoles(corpUser);
            cy.addDepartment(corpUser, depResponsibleParent);
        });

        beforeEach(() => {
            cy.yandexLogin(corpUser);
            cy.prepareLocalStorage();
            cy.intercept('/api/1.0/client/*/department_manager/search').as('depSearch');
        });

        it('corptaxi-433: Создание подразделения с ответственным', () => {
            cy.removeAllRoles(corpUser).then(() => {
                depResponsible = Date.now() + 'responsible-department';
                cy.corpOpen('/staff');
                cy.get('.ControlGroup', {timeout: 10000}).contains('Подразделение').click();
                cy.get('[name="department.name"]').type(depResponsible);
                cy.get('.amber-section > .amber-button').contains('Выдать роль').click();
                cy.get('[name="managers.0.fullname"]').type(profileData.full_name_man);
                cy.get('[name="managers.0.yandex_login"]').type(profileData.yandex_login_man);
                cy.get('[name="managers.0.email"]').type(profileData.email_man);
                cy.get('[name="managers.0.phone"]').clear().type(profileData.phone_man);
                cy.get('#react-select-3--value > .Select-input > input').click();
                cy.get('.Select-menu-outer').contains(profileData.role_man).click();
                cy.get('[type="submit"]').click();
                cy.xpath(`//*[contains(text(), '${depResponsible}')]`).should('exist');

                waitCreateRole();

                cy.xpath(
                    `//*[@class='TableRow TableRow amber-row']//div[contains(text(),'${profileData.full_name_man}')]`
                ).click();
                cy.get('.Select-value', {timeout: 10000}).contains(depResponsible).should('exist');
                cy.get('[name="fullname"]').should('have.value', profileData.full_name_man);
                cy.get('[name="yandex_login"]').should('have.value', profileData.yandex_login_man);
                cy.get('[name="email"]').should('have.value', profileData.email_man);
                cy.get('[name="phone"]').should('have.value', profileData.phone_man);

                // Удаление роли
                cy.removeAllRoles(corpUser);

                // Удаление департамента
                cy.corpOpen('staff/');
                cy.xpath(`//*[contains(text(), '${depResponsible}')]`, {
                    timeout: 10000
                }).click();
                cy.xpath(`(//span[@class='MuiIconButton-label'])[3]`)
                    .click()
                    .get('.amber-button', {timeout: 10000})
                    .contains('Удалить')
                    .click()
                    .get('.amber-section_roundBorders_all', {timeout: 10000})
                    .contains('Удалить')
                    .click();
            });
        });

        it('corptaxi-946: Две роли. Форма роли. Добавление подразделения', () => {
            cy.removeAllRoles(corpUser).then(() => {
                depResponsible = Date.now() + 'responsible-department';
                cy.corpOpen('/staff');
                cy.get('.ControlGroup', {timeout: 10000}).contains('Подразделение').click();
                cy.get('[name="department.name"]').type(depResponsible);
                cy.get('.amber-section > .amber-button').contains('Выдать роль').click();
                cy.get(':nth-child(4) > .amber-button').contains('Роль').click();
                cy.get('[name="managers.0.fullname"]').type(profileData.full_name_api);
                cy.get('[name="managers.0.yandex_login"]').type(profileData.yandex_login_api);
                cy.get('[name="managers.0.email"]').type(profileData.email_api);
                cy.get('[name="managers.0.phone"]').clear().type(profileData.phone_api);
                cy.get('#react-select-3--value > .Select-input > input').click();
                cy.get('.Select-menu-outer').contains(profileData.role_man).click();

                cy.get('[name="managers.1.fullname"]').type(profileData.full_name_sec);
                cy.get('[name="managers.1.yandex_login"]').type(profileData.yandex_login_sec);
                cy.get('[name="managers.1.email"]').type(profileData.email_sec);
                cy.get('[name="managers.1.phone"]').clear().type(profileData.phone_sec);
                cy.get('#react-select-4--value > .Select-input > input').click();
                cy.get('.Select-menu-outer').contains(profileData.role_sec).click();
                cy.get('[type="submit"]').click();

                cy.xpath(`//*[contains(text(), '${depResponsible}')]`).should('exist');

                waitCreateRole();

                cy.xpath(
                    `//*[@class='TableRow TableRow amber-row']//div[contains(text(),'${profileData.full_name_api}')]`
                ).click();
                cy.get('.Select-value', {timeout: 10000}).contains(depResponsible).should('exist');
                cy.get('[name="fullname"]').should('have.value', profileData.full_name_api);
                cy.get('[name="yandex_login"]').should('have.value', profileData.yandex_login_api);
                cy.get('[name="email"]').should('have.value', profileData.email_api);
                cy.get('[name="phone"]').should('have.value', profileData.phone_api_list);
                cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
                cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');

                cy.xpath(
                    `//*[@class='TableRow TableRow amber-row']//div[contains(text(),'${profileData.full_name_sec}')]`
                ).click();
                cy.get('.Select-value', {timeout: 10000}).contains(depResponsible).should('exist');
                cy.get('[name="fullname"]').should('have.value', profileData.full_name_sec);
                cy.get('[name="yandex_login"]').should('have.value', profileData.yandex_login_sec);
                cy.get('[name="email"]').should('have.value', profileData.email_sec);
                cy.get('[name="phone"]').should('have.value', profileData.phone_sec);
                cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
                cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');

                // Удаление департамента
                cy.removeAllRoles(corpUser);
                cy.corpOpen('staff/');

                cy.xpath(`//*[contains(text(), '${depResponsible}')]`, {
                    timeout: 10000
                }).click();
                cy.xpath(`(//span[@class='MuiIconButton-label'])[3]`)
                    .click()
                    .get('.amber-button', {timeout: 10000})
                    .contains('Удалить')
                    .click()
                    .get('.amber-section_roundBorders_all', {timeout: 10000})
                    .contains('Удалить')
                    .click();
            });
        });

        // https://st.yandex-team.ru/QAWEBTAXI-249
        it.skip('corptaxi-948: Создание дочернего подразделения с ролью', () => {
            cy.removeAllRoles(corpUser).then(() => {
                cy.corpOpen('/staff');

                cy.get('.ControlGroup ').contains('Подразделение').click();
                cy.get('[name="department.name"]').type(depResponsibleSub);
                cy.get('#react-select-2--value > .Select-input > input').click();
                cy.get('#react-select-2--value > .Select-input > input').type(depResponsibleParent);
                cy.get('.Select-menu-outer').contains(depResponsibleParent).click();
                cy.get('.amber-section > .amber-button').contains('Выдать роль').click();
                cy.get('[name="managers.0.fullname"]').type(profileData.full_name_api_rn);
                cy.get('[name="managers.0.yandex_login"]').type(profileData.yandex_login_api_rn);
                cy.get('[name="managers.0.email"]').type(profileData.email_api_rn);
                cy.get('[name="managers.0.phone"]').clear().type(profileData.phone_api_rn);
                cy.get('#react-select-3--value > .Select-input > input').click();
                cy.get('.Select-menu-outer').contains(profileData.role_man).click();
                cy.get('[type="submit"]').click();

                cy.xpath(`//*[contains(text(), '${depResponsibleParent}')]`).should('exist');

                waitCreateRole();

                cy.xpath(
                    `//*[@class='TableRow TableRow amber-row']//div[contains(text(),'${profileData.full_name_api_rn}')]`,
                    {timeout: 10000}
                ).click();

                cy.get('.Select-value', {timeout: 10000}).contains(depResponsibleSub);
                cy.get('#react-select-2--value > .Select-input').click();
                cy.get('.Select-menu-outer > .Select-menu > .Select-option ')
                    .contains(depResponsibleParent)
                    .should('exist');
                cy.get('[name="fullname"]', {timeout: 10000}).should(
                    'have.value',
                    profileData.full_name_api_rn
                );
                cy.get('[name="yandex_login"]').should('have.value', profileData.yandex_login_api_rn);
                cy.get('[name="email"]').should('have.value', profileData.email_api_rn);
                cy.get('[name="phone"]').should('have.value', profileData.phone_api_rn);
                cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
                cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');

                // Удаление роли
                cy.removeAllRoles(corpUser);

                // Удаление департамента
                cy.corpOpen('staff/');
                cy.xpath(`//*[contains(text(), '${depResponsibleParent}')]`, {
                    timeout: 10000
                }).click();
                cy.xpath(`(//span[@class='MuiIconButton-label'])[3]`)
                    .click()
                    .get('.amber-button', {timeout: 10000})
                    .contains('Удалить')
                    .click()
                    .get('.amber-section_roundBorders_all', {timeout: 10000})
                    .contains('Удалить')
                    .click()
                    .get('.amber-section_roundBorders_all', {timeout: 10000})
                    .contains('Удалить')
                    .should('not.exist');
            });
        });
    });
});
