import departments from '../../fixtures/responses/group/all-resp/departments.json';
import groupRenameDelete from '../../fixtures/responses/group/all-resp/general-group-rn-del.json';
import defaultGroups from '../../fixtures/responses/group/all-resp/group-default-name.json';

describe('Группы', () => {
    const corpUser = 'autotestcorp-profile';

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('staff/');

        cy.intercept('POST', '/api/1.0/search/departments', {
            fixture: 'responses/group/all-resp/departments.json'
        }).as('allDepartments');

        cy.intercept('GET', '/api/1.0/group?department_id=null&limit=10000', {
            fixture: 'responses/group/all-resp/general-group.json'
        });

        cy.intercept('GET', '/api/1.0/group/*', {
            fixture: 'responses/group/all-resp/no-rights.json'
        }).as('noRights');

        cy.intercept(
            'GET',
            `/api/1.0/group?department_id=${departments.departments[1]._id}&limit=10000`,
            {
                fixture: 'responses/group/all-resp/group-default-name.json'
            }
        ).as('grDefaultName');

        cy.intercept(
            'GET',
            '/api/1.0/client/*/user?include_roles=*&department_id=*&skip=0&limit=50',
            {
                fixture: 'responses/group/all-resp/sorting.json'
            }
        );

        cy.intercept(
            'GET',
            `/api/1.0/client/*/user?department_id=${departments.departments[1]._id}&skip=0&limit=50&include_subdepartments=1`,
            {
                fixture: 'responses/group/all-resp/sorting.json'
            }
        );

        cy.intercept('GET', `/api/1.0/group/${defaultGroups.items[0]._id}`, {
            fixture: 'responses/group/all-resp/group-default.json'
        }).as('choiceGroupLimits');

        cy.intercept('GET', `/api/1.0/group/${defaultGroups.items[1]._id}`, {
            fixture: 'responses/group/all-resp/group-default.json'
        }).as('choiceGroup');

        cy.intercept(
            'GET',
            `/api/1.0/group?department_id=${departments.departments[0]._id}&limit=10000`,
            {
                fixture: 'responses/group/all-resp/general-group-rn-del.json'
            }
        ).as('grRenameDelete');
    });

    // Реализация выпадающей кнопки редактировать, будет сделана в таске https://st.yandex-team.ru/QAWEBTAXI-37
    it('corptaxi-397: Добавление новой группы с лимитами на сервисы', () => {
        cy.intercept('POST', '/api/1.0/group', {
            _id: '123456789'
        }).as('saveGroups');

        cy.get('.ControlGroup ', {timeout: 10000}).contains('Группа').click();
        cy.get('[name="name"]').type(defaultGroups.items[0].name);
        cy.get('#react-select-2--value > .Select-input > input').click();
        cy.get('.Select-menu-outer').contains(departments.departments[1].name).click();
        cy.get('.Select-placeholder').contains('13').click();
        cy.get('.Select-menu-outer').click('top');
        cy.get('.Select-menu-outer').click().last();
        cy.get('.ServicesConfig > :nth-child(1) > :nth-child(1) > :nth-child(1)').click();
        cy.get('.Limit__click-catcher').first().type(defaultGroups.items[0].services.taxi.limit);
        cy.get('.Limit__click-catcher')
            .next()
            .type(defaultGroups.items[0].services.eats2.limits.monthly.amount);
        cy.get('.ControlGroup').contains('Сохранить').click();

        // Проверяем  что отправили
        cy.wait('@saveGroups')
            .its('request.body')
            .then(xhr => {
                expect(xhr.name).to.equal('default_name');
                expect(xhr.department_id).to.equal('4d4ac441292b467c807be2d6064d3128');
                expect(xhr.services.eats2.is_active).to.be.true;
                expect(xhr.services.eats2.limits.monthly.amount).to.equal('333');
                expect(xhr.services.eats2.limits.monthly.no_specific_limit).to.be.false;
                expect(xhr.services.taxi.limit).to.equal(222);
                expect(xhr.services.taxi.no_specific_limit).to.be.false;
                expect(xhr.services.taxi.restrictions).is.empty;
                expect(xhr.services.taxi.geo_restrictions).is.empty;
                expect(xhr.services.taxi.classes).to.include.members([
                    'premium_van',
                    'maybach',
                    'cargo',
                    'child_tariff',
                    'express',
                    'business',
                    'comfortplus',
                    'courier',
                    'minivan',
                    'universal',
                    'econom'
                ]);
                expect(xhr.services.taxi.limits_mode).to.equal('and');
                expect(xhr.services.taxi.period).to.equal('month');
                expect(xhr.services.taxi.orders.no_specific_limit).is.true;
            });

        // Проверяем отображение
        cy.get(`[href="/staff/departments/${departments.departments[1]._id}"]`, {
            timeout: 10000
        }).should('exist');
        cy.xpath(`//*[text()="${departments.departments[1].name}"]`).click();
        cy.xpath(`//div[text()='${defaultGroups.items[0].name}']`, {timeout: 10000}).click();
        cy.xpath(`(//span[@class='MuiIconButton-label'])[2]`).click();

        cy.wait('@noRights');
        cy.wait('@choiceGroupLimits');

        cy.get('[name="name"]').should('have.value', defaultGroups.items[0].name);
        cy.get('.Select-value .Select-value-label')
            .contains(departments.departments[1].name)
            .should('exist');
        cy.get('.Select-placeholder').contains('10').should('exist');

        cy.xpath(`((//label[text()='Лимит'])[1]/following::input)[1]`)
            .click()
            .should('have.value', defaultGroups.items[0].services.taxi.limit);
        cy.xpath(`((//label[text()='Лимит'])[2]/following::input)[1]`)
            .click()
            .should('have.value', defaultGroups.items[0].services.eats2.limits.monthly.amount);
        cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
    });

    it('corptaxi-956: Добавление новой группы без лимитов на сервисы', () => {
        cy.intercept('POST', '/api/1.0/group', {
            _id: '123456789'
        }).as('saveGroups');

        cy.get('.ControlGroup ', {timeout: 10000}).contains('Группа').click();
        cy.get('[name="name"]').type(defaultGroups.items[0].name + '_no_limit');
        cy.get('#react-select-2--value > .Select-input > input').click();
        cy.get('.Select-menu-outer').contains(departments.departments[1].name).click();
        cy.get('.Select-placeholder').contains('13').click();
        cy.get('.Select-menu-outer').click('top');
        cy.get('.Select-menu-outer').click().last();
        cy.get('.ServicesConfig > :nth-child(1) > :nth-child(1) > :nth-child(1)').click();
        cy.get('.ControlGroup').contains('Сохранить').click();

        //Проверяем  что отправили
        cy.wait('@saveGroups')
            .its('request.body')
            .then(xhr => {
                expect(xhr.name).to.equal('default_name_no_limit');
                expect(xhr.department_id).to.equal('4d4ac441292b467c807be2d6064d3128');
                expect(xhr.services.eats2.is_active).to.be.true;
                expect(xhr.services.eats2.limits.monthly.amount).to.equal('-1');
                expect(xhr.services.eats2.limits.monthly.no_specific_limit).to.be.true;
                expect(xhr.services.taxi.no_specific_limit).to.be.true;
                expect(xhr.services.taxi.restrictions).is.empty;
                expect(xhr.services.taxi.geo_restrictions).is.empty;
                expect(xhr.services.taxi.classes).to.include.members([
                    'premium_van',
                    'maybach',
                    'cargo',
                    'child_tariff',
                    'express',
                    'business',
                    'comfortplus',
                    'courier',
                    'minivan',
                    'universal',
                    'econom'
                ]);
                expect(xhr.services.taxi.limits_mode).to.equal('and');
                expect(xhr.services.taxi.period).to.equal('month');
                expect(xhr.services.taxi.orders.no_specific_limit).is.true;
            });

        // Проверяем отображение
        cy.xpath(`//*[text()="${departments.departments[1].name}"]`).click();
        cy.xpath(`//div[text()='${defaultGroups.items[0].name}_no_limit']`, {
            timeout: 10000
        }).click();
        cy.xpath(`(//span[@class='MuiIconButton-label'])[2]`).click();

        cy.wait('@noRights');
        cy.wait('@choiceGroup');

        cy.get('[name="name"]').should('have.value', defaultGroups.items[0].name + '_no_limit');
        cy.get('.Select-value .Select-value-label')
            .contains(departments.departments[1].name)
            .should('exist');
        cy.get('.Select-placeholder').contains('10').should('exist');
        cy.xpath(`(//input[@class='amber-input__control'])[3]`).should('be.disabled');
        cy.xpath(`(//input[@class='amber-input__control'])[5]`).should('be.disabled');
        cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
    });

    it('corptaxi-957: Редактирование группы', () => {
        cy.intercept('PUT', `/api/1.0/group/${groupRenameDelete.items[1]._id}`, {
            _id: '123456789'
        }).as('saveGroups');

        cy.get(`[href="/staff/departments/${departments.departments[0]._id}"]`, {
            timeout: 10000
        }).should('exist');
        cy.get('.MuiGrid-grid-xs-true').contains(departments.departments[0].name).click();
        cy.xpath(`//div[text()='${groupRenameDelete.items[1].name}']`, {timeout: 10000}).click();
        cy.xpath(`(//span[@class='MuiIconButton-label'])[2]`).click();
        cy.get('[name="name"]')
            .clear()
            .type(groupRenameDelete.items[1].name + '_accept');
        cy.get('#react-select-2--value > .Select-input > input').click();
        cy.get('.Select-menu-outer').contains(departments.departments[0].name).click();
        cy.get('.Select-placeholder').contains('12').click();
        cy.get('.Select-menu-outer').click('top');
        cy.get('.Select-menu-outer').click().last();
        cy.get('.ServicesConfig > :nth-child(1) > :nth-child(1) > :nth-child(1)').click();
        cy.get('.Limit__click-catcher').first().type('555');
        cy.get('.Limit__click-catcher').next().type('444');
        cy.get('.ControlGroup').contains('Сохранить').click();

        //Проверяем  что отправили
        cy.wait('@saveGroups')
            .its('request.body')
            .then(xhr => {
                expect(xhr.name).to.equal('group_rename_accept');
                expect(xhr.department_id).to.equal('ab0b06752fe54ebfadce82fe9ecb5fe6');
                expect(xhr.services.eats2.is_active).to.be.true;
                expect(xhr.services.eats2.limits.monthly.amount).to.equal('444');
                expect(xhr.services.eats2.limits.monthly.no_specific_limit).to.be.false;
                expect(xhr.services.taxi.limit).to.equal(555);
                expect(xhr.services.taxi.no_specific_limit).to.be.false;
                expect(xhr.services.taxi.restrictions).is.empty;
                expect(xhr.services.taxi.geo_restrictions).is.empty;
                expect(xhr.services.taxi.classes).to.include.members([
                    'premium_van',
                    'maybach',
                    'cargo',
                    'child_tariff',
                    'express',
                    'business',
                    'comfortplus',
                    'courier',
                    'minivan',
                    'econom'
                ]);
                expect(xhr.services.taxi.limits_mode).to.equal('and');
                expect(xhr.services.taxi.period).to.equal('month');
                expect(xhr.services.taxi.orders.no_specific_limit).is.true;
            });

        // Проверяем отображение
        cy.get(`[href="/staff/departments/${departments.departments[0]._id}"]`, {
            timeout: 10000
        }).should('exist');
        cy.xpath(`//div[text()='${groupRenameDelete.items[1].name}_accept']`, {
            timeout: 10000
        }).click();
        cy.xpath(`(//span[@class='MuiIconButton-label'])[2]`).click();
        cy.get('[name="name"]').should('have.value', groupRenameDelete.items[1].name + '_accept');
        cy.get('.Select-value .Select-value-label')
            .contains(departments.departments[0].name)
            .should('exist');
        cy.get('.Select-placeholder').contains('10').should('exist');
        cy.xpath(`((//label[text()='Лимит'])[1]/following::input)[1]`)
            .click()
            .should('have.value', '555');
        cy.xpath(`((//label[text()='Лимит'])[2]/following::input)[1]`)
            .click()
            .should('have.value', '444');
        cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
    });

    it('corptaxi-958: Удаление группы', () => {
        cy.intercept('DELETE', `/api/1.0/group/*`, {
            body: {}
        }).as('removeGroup');

        cy.get(`[href="/staff/departments/${departments.departments[0]._id}"]`, {
            timeout: 10000
        }).should('exist');
        cy.get(`.amber-modal-content > .Loader`, {timeout: 10000}).should('not.exist');
        cy.get('.MuiGrid-grid-xs-true').contains(departments.departments[0].name).click();
        cy.xpath(`//div[text()='${groupRenameDelete.items[0].name}']`).click();
        cy.get(
            `[href="/staff/departments/${departments.departments[0]._id}/groups/${groupRenameDelete.items[0]._id}"] > div > div > button:last-child `
        ).click();
        cy.get('.amber-section_roundBorders_bottom', {timeout: 10000}).contains('Удалить').click();
        cy.get('.amber-section_roundBorders_all', {timeout: 10000}).contains('Удалить').click();

        cy.wait('@removeGroup').its('response.statusCode').should('eq', 200);

        cy.get(
            `[href="/staff/departments/${departments.departments[0]._id}/groups/${groupRenameDelete.items[0]._id}"] > div `,
            {
                timeout: 10000
            }
        ).should('not.exist');
    });

    it('corptaxi-959: Открытие формы создания группы из сайдбара', () => {
        cy.get('.MuiIconButton-label > svg', {timeout: 10000}).click();
        cy.get('.MuiList-root > [tabindex="0"]').contains('Добавить группу').click();
        cy.get('.amber-modal__window-inner').should('exist');
    });
});
