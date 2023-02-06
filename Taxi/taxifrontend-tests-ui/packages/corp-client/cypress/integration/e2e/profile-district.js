import profileData from './data/profile-district.json';

describe('Ваши районы', () => {
    const corpUser = 'autotestcorp-profile';
    const districtRename = 'Rename' + Date.now();
    const districtDelete = 'Delete' + Date.now();

    before(() => {
        cy.removeAllDisctrict(corpUser);
        cy.addDistrict(corpUser, districtRename, profileData.center, profileData.radius);
        cy.addDistrict(corpUser, districtDelete, profileData.center, profileData.radius);
    });

    beforeEach(() => {
        cy.yandexLogin(corpUser);
        cy.prepareLocalStorage();
        cy.corpOpen('/profile/geo/');
    });

    it('corptaxi-535: Указать доступные районы существующему сотруднику. Вкладка Сотрудники', () => {
        cy.intercept(
            'GET',
            '/api/1.0/client/a5d0fd0ba16340089924ab6a63f8ff4f/user/ed4d9401e24649ab829ea19d828d68fb',
            {
                fixture: 'responses/user/user-without-district.json'
            }
        );
        cy.intercept('GET', '/api/1.0/client/*/geo_restrictions*', {
            fixture: 'responses/client/geo-restrictions.json'
        });

        cy.intercept('PUT', '/api/1.0/client/*/user/*', {}).as('saveUser');

        cy.visit('/staff#user/edit/ed4d9401e24649ab829ea19d828d68fb');
        cy.xpath('//*[text()="Сервисы"]').click();
        cy.xpath('//*[text()="Указать доступные районы поездок"]').click();
        cy.xpath('//*[text()="Откуда"]/../..').click();
        cy.xpath('//*[text()="Домашний"]').click();
        cy.xpath('//*[text()="Куда"]/../..').click();
        cy.xpath('//*[text()="Работочка"]').click();
        cy.xpath('//*[text()="Сохранить"]/..').click();

        cy.wait('@saveUser')
            .its('request.body')
            .then(body => {
                expect(body.role.geo_restrictions[0].source).eq('fe9bca0f230b4fc0b0e42e9f5638bbd3');
                expect(body.role.geo_restrictions[0].destination).eq(
                    '68bafc5a88a04ef18f3ed26a1ccb1a4c'
                );
            });
    });

    it('corptaxi-564: Добавление района. Раздел Ваши районы. Вкладка профиль', () => {
        cy.corpOpen('profile/geo/');
        cy.get('.amber-col > .amber-button > .amber-button__text').click();
        cy.get('[name="name"]').type(profileData.district);
        cy.get('[placeholder="Адрес"]').type(profileData.adress);
        cy.wait(2000);
        cy.get('.SuggestOption_selected > .SuggestOption__name')
            .contains(profileData.adress)
            .click();
        cy.wait(2000);
        cy.get('[name="radius"]').clear().type(profileData.radius);
        cy.wait(2000);
        cy.get('.ControlGroup > .amber-button_theme_accent').contains('Сохранить').click();

        cy.xpath(`//div[text()='${profileData.district}']`)
            .next('.FloatingActions')
            .then($el => {
                cy.wrap($el).invoke('show');
                cy.wrap($el).find('.amber-icon_edit').click();
            });
        cy.get('[name="name"]').should('have.value', profileData.district);
        cy.get('[name="radius"]').should('have.value', profileData.radius);
        cy.get('[placeholder="Адрес"]').should('have.value', profileData.adress);
        cy.get('.ControlGroup > .amber-button_theme_fill').contains('Отмена').click();
    });

    it('corptaxi-565: Редактирование района. Раздел Ваши районы. Вкладка профиль', () => {
        cy.xpath(`//div[text()='${districtRename}']`)
            .next('.FloatingActions')
            .then($el => {
                cy.wrap($el).invoke('show');
                cy.wrap($el).find('.amber-icon_edit').click();
            });
        cy.get('[name="name"]').clear().type(profileData.district_rn);
        cy.get('[placeholder="Адрес"]').clear().type(profileData.adress_rn);
        cy.wait(2000);
        cy.get('.SuggestOption > .SuggestOption__name').contains(profileData.adress_rn).click();
        cy.wait(2000);
        cy.get('[name="radius"]').clear().type(profileData.radius_rn);
        cy.wait(2000);
        cy.get('.ControlGroup > .amber-button_theme_accent').contains('Сохранить').click();

        cy.xpath(`//div[text()='${profileData.district_rn}']`)
            .next('.FloatingActions')
            .then($el => {
                cy.wrap($el).invoke('show');
                cy.wrap($el).find('.amber-icon_edit').click();
            });
        cy.get('[name="name"]').should('have.value', profileData.district_rn);
        cy.get('[name="radius"]').should('have.value', profileData.radius_rn);
        cy.get('[placeholder="Адрес"]').should('have.value', profileData.adress_rn);
    });

    it('corptaxi-1046: Удаление района. Раздел Ваши районы. Вкладка профиль', () => {
        cy.xpath(`//div[text()='${districtDelete}']`)
            .next('.FloatingActions')
            .then($el => {
                cy.wrap($el).invoke('show');
                cy.wrap($el).find('.amber-icon_edit').click();
            });
        cy.get(':nth-child(2) > .amber-button > .amber-button__text').contains('Удалить').click();
        cy.wait(2000);
        cy.get('.ControlGroup > .amber-button_theme_accent').contains('Удалить').click();
        cy.xpath(`//div[text()='${districtDelete}']`).should('not.exist');
    });
});
