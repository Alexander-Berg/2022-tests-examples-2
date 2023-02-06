import departments from '../../fixtures/responses/role/profile-roles/departments.json';
import addManager from '../../fixtures/requests/roles/add-manager.json';
import changeManagers from '../../fixtures/responses/role/profile-roles/managers-rn-del.json';
import deleteManagers from '../../fixtures/responses/role/profile-roles/get-delete-managers.json';
import changeOnceManager from '../../fixtures/requests/roles/change-manager.json';

describe('Управление ролями', () => {
    const corpUser = 'autotestcorp-profile';
    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('profile/managers/');
    });

    context('Добавление роли и проверка функционала', () => {
        it('corptaxi-1050: Переход в раздел Управление ролями', () => {
            cy.get('a[href="/profile/managers"]').contains('Управление ролями').click();
            cy.get('.ControlGroup > .amber-button', {timeout: 10000})
                .contains('Выдать роль')
                .should('exist');
        });

        it('corptaxi-548: Выдать Роль. Раздел Управление ролями. Вкладка профиль', () => {
            cy.intercept('POST', `/api/1.0/client/*/department_manager`, {
                _id: '123456789'
            }).as('saveRole');

            cy.get('.ControlGroup > .amber-button').contains('Выдать роль').click();
            cy.get('#react-select-2--value > .Select-input > input').click();
            cy.get('.Select-menu-outer').contains(departments.departments[0].name).click();
            cy.get('[name="fullname"]').type(addManager.fullname);
            cy.get('[name="yandex_login"]').type(addManager.yandex_login);
            cy.get('[name="email"]').type(addManager.email);
            cy.get('[name="phone"]').clear().type(addManager.phone);
            cy.get('#react-select-3--value > .Select-input > input').click();
            cy.get('.Select-menu-outer').contains('Менеджер подразделения').click();
            cy.get('.ControlGroup > .amber-button_theme_accent').contains('Сохранить').click();

            //Проверяем  что отправили
            cy.wait('@saveRole')
                .its('request.body')
                .then(xhr => {
                    cy.fixture('./../fixtures/requests/roles/add-manager.json').then(request => {
                        expect(xhr).to.deep.equal(request);
                    });
                });

            cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');
        });

        it('corptaxi-555: Поиск по Имени пользователя. Раздел Управление ролями. Вкладка профиль', () => {
            cy.intercept('POST', '/api/1.0/client/*/department_manager/search', {
                fixture: 'responses/role/profile-roles/search-manager.json'
            });
            cy.intercept('POST', '/api/1.0/search/departments', {
                fixture: 'responses/role/profile-roles/departments.json'
            }).as('searchManager');

            cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control', {
                timeout: 10000
            }).type(changeManagers.department_managers[0].fullname);

            cy.wait('@searchManager');

            cy.get('.TableRow > .amber-col_paddingLeft-xs_m', {timeout: 10000})
                .contains(changeManagers.department_managers[0].fullname)
                .should('exist');
            cy.get('.TableRow').should($res => {
                expect($res).to.have.length(1);
            });
        });

        it('corptaxi-1047: Поиск по несуществующей роли. Раздел Управление ролями. Вкладка профиль', () => {
            cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control').type(
                'Несуществующий'
            );
            cy.get('.TableRow > .BlankSlate__text')
                .contains('Ещё нет выданных ролей')
                .should('exist');
        });
    });

    context('Изменение и удаление роли', () => {
        beforeEach(() => {
            cy.intercept('POST', '/api/1.0/search/departments', {
                fixture: 'responses/role/profile-roles/departments.json'
            });

            cy.intercept('POST', '/api/1.0/client/*/department_manager/search', {
                fixture: 'responses/role/profile-roles/managers-rn-del.json'
            });
        });

        it('corptaxi-549: Удаление Роли. Раздел Управление ролями. Вкладка профиль', () => {
            cy.intercept('GET', `/api/1.0/client/*/department_manager/${deleteManagers._id}`, {
                fixture: 'responses/role/profile-roles/get-delete-managers.json'
            });

            cy.intercept('DELETE', `/api/1.0/client/*/department_manager/${deleteManagers._id}`, {
                body: {}
            }).as('removeManagers');

            cy.xpath(
                `//*[@class='TableRow TableRow amber-row']//div[contains(text(),'${deleteManagers.fullname}')]`,
                {timeout: 10000}
            ).click();
            cy.get('button.EditorModalFooterSection__remove').contains('Удалить').click();
            cy.get('button.amber-button_theme_accent').contains('Удалить').click();

            cy.wait('@removeManagers').its('response.statusCode').should('eq', 200);

            cy.get('a.TableRow > .TableCell').contains(deleteManagers.fullname).should('not.exist');
        });

        it('corptaxi-1048: Проверка данных в списке. Раздел Управление ролями. Вкладка профиль', () => {
            cy.get('.TableRow > .amber-col_paddingLeft-xs_m', {timeout: 10000})
                .contains(changeManagers.department_managers[0].fullname)
                .should('exist');
            cy.get('.TableRow > :nth-child(2)')
                .contains(changeManagers.department_managers[0].yandex_login)
                .should('exist');
            cy.get('.TableRow > :nth-child(3)').contains('+7 (916) 192 99 55').should('exist');
            cy.get('.TableRow > :nth-child(5)')
                .contains(changeManagers.department_managers[0].email)
                .should('exist');
        });

        it('corptaxi-1049: Редактировать Роль. Раздел Управление ролями. Вкладка профиль', () => {
            cy.intercept(
                'GET',
                `/api/1.0/client/*/department_manager/${changeManagers.department_managers[0]._id}`,
                {
                    fixture: 'responses/role/profile-roles/get-change-managers.json'
                }
            );

            cy.intercept(
                'PUT',
                `/api/1.0/client/*/department_manager/${changeManagers.department_managers[0]._id}`,
                {
                    body: {}
                }
            ).as('changeManager');

            cy.get('.TableRow > .amber-col_paddingLeft-xs_m', {timeout: 10000})
                .contains(changeManagers.department_managers[0].fullname)
                .click();
            cy.get('#react-select-2--value > .Select-input > input').click();
            cy.get('.Select-menu-outer').contains(departments.departments[1].name).click();
            cy.get('[name="fullname"]').clear().type(changeOnceManager.fullname);
            cy.get('[name="yandex_login"]').clear().type(changeOnceManager.yandex_login);
            cy.get('[name="email"]').clear().type(changeOnceManager.email);
            cy.get('[name="phone"]').clear().type('+7 (916) 192 11 11');
            cy.get('#react-select-3--value > .Select-input > input').click();
            cy.get('.Select-menu-outer').contains('Секретарь подразделения').click();
            cy.get('.ControlGroup > .amber-button_theme_accent').contains('Сохранить').click();
            cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');

            //Проверяем  что отправили
            cy.wait('@changeManager')
                .its('request.body')
                .then(xhr => {
                    cy.fixture('./../fixtures/requests/roles/change-manager.json').then(request => {
                        expect(xhr).to.deep.equal(request);
                    });
                });

            cy.xpath(
                `//*[@class='TableRow TableRow amber-row']//div[contains(text(),'${changeOnceManager.fullname}')]`,
                {timeout: 10000}
            ).click();
            cy.get('.Select-value', {timeout: 10000})
                .contains(departments.departments[1].name)
                .should('exist');
            cy.get('[name="fullname"]').should('have.value', changeOnceManager.fullname);
            cy.get('[name="yandex_login"]').should('have.value', changeOnceManager.yandex_login);
            cy.get('[name="email"]').should('have.value', changeOnceManager.email);
            cy.get('[name="phone"]').should('have.value', '+7 (916) 192 11 11');
            cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
            cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');
        });
    });
});
