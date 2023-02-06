import profileData from './data/profile-roles.json';

function waitCreateRole() {
    cy.log('Нужно подождать сохранение роли на бэке');
    cy.wait(3000);
    cy.reload();
    cy.wait('@depSearch');
}

describe('Управление ролями', () => {
    const corpUser = 'autotestcorp-departments';
    const rolesDep = Date.now() + 'roles-department';
    let globalDepId;

    before(() => {
        cy.removeAllRoles(corpUser);
        cy.addDepartment(corpUser, rolesDep).then(depId => {
            globalDepId = depId;
            cy.addRole(
                corpUser,
                globalDepId,
                profileData.email_api_del,
                profileData.full_name_api_del,
                profileData.phone_api_del,
                profileData.role_api_del,
                profileData.yandex_login_api_del
            );
        });
    });

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('profile/managers/');
        cy.intercept('/api/1.0/client/*/department_manager/search').as('depSearch');
    });

    it('corptaxi-548: Выдать Роль. Раздел Управление ролями. Вкладка профиль', () => {
        cy.get('.ControlGroup > .amber-button').contains('Выдать роль').click();
        cy.get('#react-select-2--value > .Select-input > input').click();
        cy.get('.Select-menu-outer').contains(rolesDep).click();
        cy.get('[name="fullname"]').type(profileData.full_name_man);
        cy.get('[name="yandex_login"]').type(profileData.yandex_login_man);
        cy.get('[name="email"]').type(profileData.email_man);
        cy.get('[name="phone"]').clear().type(profileData.phone_man);
        cy.get('#react-select-3--value > .Select-input > input').click();
        cy.get('.Select-menu-outer').contains(profileData.role_man).click();
        cy.get('.ControlGroup > .amber-button_theme_accent').contains('Сохранить').click();
        cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');

        waitCreateRole();

        cy.xpath(
            `//*[@class='TableRow TableRow amber-row']//div[contains(text(),'${profileData.full_name_man}')]`
        ).click();
        cy.get('.Select-value').contains(rolesDep).should('exist');
        cy.get('[name="fullname"]').should('have.value', profileData.full_name_man);
        cy.get('[name="yandex_login"]').should('have.value', profileData.yandex_login_man);
        cy.get('[name="email"]').should('have.value', profileData.email_man);
        cy.get('[name="phone"]').should('have.value', profileData.phone_man);

        //Удаление роли
        cy.get('.amber-button', {timeout: 10000})
            .contains('Удалить')
            .click()
            .get('.amber-section_roundBorders_all', {timeout: 10000})
            .contains('Удалить')
            .click();
    });

    it('corptaxi-555: Поиск по Имени пользователя. Раздел Управление ролями. Вкладка профиль', () => {
        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control').type(
            profileData.full_name_api_del
        );
        cy.get('.TableRow > .amber-col_paddingLeft-xs_m')
            .contains(profileData.full_name_api_del)
            .should('exist');
        cy.get('.TableRow').should($res => {
            expect($res).to.have.length(1);
        });
    });

    it('corptaxi-1047: Поиск по несуществующей роли. Раздел Управление ролями. Вкладка профиль', () => {
        cy.get('.Search > .amber-input > .amber-input__box > .amber-input__control').type(
            'Не существующий'
        );
        cy.get('.TableRow > .BlankSlate__text').contains('Ещё нет выданных ролей').should('exist');
    });

    it('corptaxi-1048: Проверка данных в списке. Раздел Управление ролями. Вкладка профиль', () => {
        cy.get('.TableRow > .amber-col_paddingLeft-xs_m')
            .contains(profileData.full_name_api_del)
            .should('exist');
        cy.get('.TableRow > :nth-child(2)')
            .contains(profileData.yandex_login_api_del)
            .should('exist');
        cy.get('.TableRow > :nth-child(3)')
            .contains(profileData.phone_api_del_list)
            .should('exist');
        cy.get('.TableRow > :nth-child(5)').contains(profileData.email_api_del).should('exist');
    });

    it(
        'corptaxi-1049: Редактировать Роль. Раздел Управление ролями. Вкладка профиль',
        {
            retries: {
                runMode: 0
            }
        },
        () => {
            cy.addRole(
                corpUser,
                globalDepId,
                profileData.email_api,
                profileData.full_name_api,
                profileData.phone_api,
                profileData.role_api,
                profileData.yandex_login_api
            ).then(() => {
                cy.visit('profile/managers/');
                cy.get('.TableRow > .amber-col_paddingLeft-xs_m')
                    .contains(profileData.full_name_api)
                    .click();
                cy.get('#react-select-2--value > .Select-input > input').click();
                cy.get('.Select-menu-outer').contains(rolesDep).click();
                cy.get('[name="fullname"]').clear().type(profileData.full_name_api_rn);
                cy.get('[name="yandex_login"]').clear().type(profileData.yandex_login_api_rn);
                cy.get('[name="email"]').clear().type(profileData.email_api_rn);
                cy.get('[name="phone"]').clear().type(profileData.phone_api_rn);
                cy.get('#react-select-3--value > .Select-input > input').click();
                cy.get('.Select-menu-outer').contains(profileData.role_api_rn).click();
                cy.get('.ControlGroup > .amber-button_theme_accent').contains('Сохранить').click();
                cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');

                waitCreateRole();

                cy.xpath(
                    `//*[@class='TableRow TableRow amber-row']//div[contains(text(),'${profileData.full_name_api_rn}')]`
                ).click();
                cy.get('.Select-value').contains(rolesDep).should('exist');
                cy.get('[name="fullname"]').should('have.value', profileData.full_name_api_rn);
                cy.get('[name="yandex_login"]').should(
                    'have.value',
                    profileData.yandex_login_api_rn
                );
                cy.get('[name="email"]').should('have.value', profileData.email_api_rn);
                cy.get('[name="phone"]').should('have.value', profileData.phone_api_rn);
                cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
                cy.get('.amber-modal__window', {timeout: 10000}).should('not.exist');

                // Удаление роли
                cy.removeAllRoles(corpUser);

                // Удаление департамента
                cy.corpOpen('staff/');
                cy.xpath(`//*[contains(text(), '${rolesDep}')]`, {
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
        }
    );
});
