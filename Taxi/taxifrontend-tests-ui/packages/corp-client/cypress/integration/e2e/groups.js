describe('Группы', () => {
    const corpUser = 'autotestcorp-departments';
    const groupDefault = Date.now() + 'default_group_name';
    const GROUPS_DATA = {
        group_department: 'group_department',
        default_dep_id: '85e4c40b0da148588cddc5d32ab9c9b2',
        all_tariff_count: 13,
        tariff_change: 11,
        taxi_limit: 222,
        eats_limit: 333
    };
    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('staff/');
        cy.intercept('/api/1.0/group/*').as('deleteGroup');
    });

    // Реализация выпадающей кнопки редактировать, будет сделана в таске https://st.yandex-team.ru/QAWEBTAXI-37

    it('corptaxi-397: Добавление новой группы с лимитами на сервисы', () => {
        cy.get('.ControlGroup ', {timeout: 10000}).contains('Группа').click();
        cy.get('[name="name"]').type(groupDefault);
        cy.get('#react-select-2--value > .Select-input > input').click();
        cy.get('.Select-menu-outer').contains(GROUPS_DATA.group_department).click();
        cy.get('.Select-placeholder').contains(GROUPS_DATA.all_tariff_count).click();
        cy.get('.Select-menu-outer').click('top');
        cy.get('.Select-menu-outer').click().last();
        cy.get('.ServicesConfig > :nth-child(1) > :nth-child(1) > :nth-child(1)').click();
        cy.get('.Limit__click-catcher').first().type(GROUPS_DATA.taxi_limit);
        cy.get('.Limit__click-catcher').next().type(GROUPS_DATA.eats_limit);
        cy.get('.ControlGroup').contains('Сохранить').click();

        // Проверяем данные
        cy.corpOpen('staff/');
        cy.get(`[href="/staff/departments/${GROUPS_DATA.default_dep_id}"]`, {
            timeout: 10000
        }).should('exist');
        cy.xpath(`//*[text()="${GROUPS_DATA.group_department}"]`).click();
        cy.xpath(`//div[text()='${groupDefault}']`, {timeout: 10000}).click();
        cy.xpath(`(//span[@class='MuiIconButton-label'])[2]`).click();
        cy.get('[name="name"]').should('have.value', groupDefault);
        cy.get('.Select-value .Select-value-label')
            .contains(GROUPS_DATA.group_department)
            .should('exist');
        cy.get('.Select-placeholder').contains(GROUPS_DATA.tariff_change).should('exist');

        cy.xpath(`(//input[@class='amber-input__control'])[3]`)
            .click()
            .should('have.value', GROUPS_DATA.taxi_limit);
        cy.xpath(`((//label[text()='Лимит'])[2]/following::input)[1]`)
            .click()
            .should('have.value', GROUPS_DATA.eats_limit);

        // Удаление группы
        cy.get('.amber-section_roundBorders_bottom', {timeout: 10000}).contains('Удалить').click();
        cy.get('.amber-section_roundBorders_all', {timeout: 10000}).contains('Удалить').click();

        cy.wait('@deleteGroup').its('response.statusCode').should('eq', 200);
        cy.xpath(`//div[text()='${groupDefault}']`, {timeout: 10000}).should('not.exist');
    });

    it('corptaxi-956: Добавление новой группы без лимитов на сервисы', () => {
        cy.get('.ControlGroup ', {timeout: 10000}).contains('Группа').click();
        cy.get('[name="name"]').type(groupDefault + '_no_limit');
        cy.get('#react-select-2--value > .Select-input > input').click();
        cy.get('.Select-menu-outer').contains(GROUPS_DATA.group_department).click();
        cy.get('.Select-placeholder').contains(GROUPS_DATA.all_tariff_count).click();
        cy.get('.Select-menu-outer').click('top');
        cy.get('.Select-menu-outer').click().last();
        cy.get('.ServicesConfig > :nth-child(1) > :nth-child(1) > :nth-child(1)').click();
        cy.get('.ControlGroup').contains('Сохранить').click();

        // Проверяем данные
        cy.corpOpen('staff/');
        cy.xpath(`//*[text()="${GROUPS_DATA.group_department}"]`, {timeout: 10000}).click();
        cy.xpath(`//div[text()='${groupDefault}_no_limit']`, {
            timeout: 10000
        }).click();
        cy.xpath(`(//span[@class='MuiIconButton-label'])[2]`).click();
        cy.get('[name="name"]').should('have.value', groupDefault + '_no_limit');
        cy.get('.Select-value .Select-value-label')
            .contains(GROUPS_DATA.group_department)
            .should('exist');
        cy.get('.Select-placeholder').contains(GROUPS_DATA.tariff_change).should('exist');
        cy.xpath(`(//input[@class='amber-input__control'])[3]`).should('be.disabled');
        cy.xpath(`((//label[text()='Лимит'])[2]/following::input)[1]`).should('be.disabled');

        // Удаление группы
        cy.get('.amber-section_roundBorders_bottom', {timeout: 10000}).contains('Удалить').click();
        cy.get('.amber-section_roundBorders_all', {timeout: 10000}).contains('Удалить').click();

        cy.wait('@deleteGroup').its('response.statusCode').should('eq', 200);
        cy.xpath(`//div[text()='${groupDefault}']`, {timeout: 10000}).should('not.exist');
    });

    it('corptaxi-957: Редактирование группы', () => {
        const groupRename = Date.now() + 'group_rename';
        cy.addGroup(corpUser, GROUPS_DATA.default_dep_id, groupRename).then(renameGroupId => {
            cy.corpOpen('/staff');
            cy.get(`[href="/staff/departments/${GROUPS_DATA.default_dep_id}"]`, {
                timeout: 10000
            }).should('exist');
            cy.get('.MuiGrid-grid-xs-true').contains(GROUPS_DATA.group_department).click();
            cy.xpath(`//div[text()='${groupRename}']`, {timeout: 10000}).click();
            cy.get(
                `[href="/staff/departments/${GROUPS_DATA.default_dep_id}/groups/${renameGroupId}"] > div > div > button:last-child `
            ).click();
            cy.get('[name="name"]')
                .clear()
                .type(groupRename + '_accept');
            cy.get('#react-select-2--value > .Select-input > input').click();
            cy.get('.Select-menu-outer').contains(GROUPS_DATA.group_department).click();
            cy.get('.Select-placeholder').contains(GROUPS_DATA.all_tariff_count).click();
            cy.get('.Select-menu-outer').click('top');
            cy.get('.Select-menu-outer').click().last();
            cy.get('.ServicesConfig > :nth-child(1) > :nth-child(1) > :nth-child(1)').click();
            cy.get('.Limit__click-catcher').first().type(GROUPS_DATA.taxi_limit);
            cy.get('.Limit__click-catcher').next().type(GROUPS_DATA.eats_limit);
            cy.get('.ControlGroup').contains('Сохранить').click();

            // Проверяем данные
            cy.corpOpen('staff/');
            cy.get(`[href="/staff/departments/${GROUPS_DATA.default_dep_id}"]`, {
                timeout: 10000
            }).should('exist');
            cy.get('.MuiGrid-grid-xs-true').contains(GROUPS_DATA.group_department).click();
            cy.xpath(`//div[text()='${groupRename}_accept']`, {
                timeout: 10000
            }).click();
            cy.xpath(`(//span[@class='MuiIconButton-label'])[2]`).click();
            cy.get('[name="name"]').should('have.value', groupRename + '_accept');
            cy.get('.Select-value .Select-value-label')
                .contains(GROUPS_DATA.group_department)
                .should('exist');
            cy.get('.Select-placeholder').contains(GROUPS_DATA.tariff_change).should('exist');

            cy.xpath(`(//input[@class='amber-input__control'])[3]`)
                .click()
                .should('have.value', GROUPS_DATA.taxi_limit);
            cy.xpath(`((//label[text()='Лимит'])[2]/following::input)[1]`)
                .click()
                .should('have.value', GROUPS_DATA.eats_limit);

            // Удаление группы
            cy.get('.amber-section_roundBorders_bottom', {timeout: 10000})
                .contains('Удалить')
                .click();
            cy.get('.amber-section_roundBorders_all', {timeout: 10000}).contains('Удалить').click();

            cy.wait('@deleteGroup').its('response.statusCode').should('eq', 200);
            cy.get(
                `[href="/staff/departments/${GROUPS_DATA.default_dep_id}/groups/${renameGroupId}"] > div `,
                {
                    timeout: 10000
                }
            ).should('not.exist');
        });
    });
});
