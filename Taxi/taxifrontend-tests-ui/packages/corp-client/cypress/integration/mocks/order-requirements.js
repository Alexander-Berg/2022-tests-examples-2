describe('Проверка модалки требований при заказе', () => {
    const formData = {
        animaltransport: true,
        childchair_other: 1,
        luggage_count: 1
    };

    beforeEach(() => {
        cy.yandexLogin('autotestcorp');
        cy.prepareLocalStorage();
        cy.intercept('POST', '/client-api/3.0/geosearch', {
            fixture: 'responses/geosearch/geosearch'
        }).as('geosearch');
        cy.intercept('POST', '/api/1.0/estimate', {
            fixture: 'responses/estimate/index.json'
        }).as('estimate');
        cy.intercept('POST', '/api/1.0/client/*/order/*/processing', {
            fixture: 'responses/order/processing/200'
        }).as('processing');
        //заменить зонинфо
        cy.intercept('GET', '/api/1.0/zoneinfo?*', {
            fixture: 'responses/zoneinfo/index.json'
        }).as('zoneinfo');
        cy.intercept('GET', 'api/2.0/users*', {
            fixture: 'responses/client/users'
        }).as('users');
        cy.intercept('GET', '/api/1.0/client/02ecd60194a24d51ada6ecae87ef1ab7/cost_centers', {
            fixture: 'responses/client/cost-centres.json'
        }).as('costCentres');
        cy.corpOpen('/order');
    });

    it('corptaxi-1012: Заказ такси с доп требованиями', () => {
        cy.intercept('POST', '/api/1.0/client/*/order', {
            statusCode: 200
        }).as('newOrder');
        cy.get('.OrderForm__submit', {timeout: 10000}).should('exist').should('be.disabled');
        cy.get('.OrderFormUser input').should('exist').focus().type('+79096785645');
        cy.wait('@users');
        cy.get('.SuggestOption').should('exist').contains('+7 (909) 678 56 45').click();
        cy.get('.FormSource').find('input').focus().type('Аврора');
        cy.get('.SuggestOption').contains('Аврора').click();
        cy.get('.Select-placeholder_with-value').should('not.exist');
        cy.get('.Select-control')
            .contains('Требования')
            .should('not.have.class', 'Select-placeholder_with-value')
            .click();
        cy.get('div.amber-modal__window').should('be.visible');
        cy.get('.RequirementItem').contains('Перевозка домашнего животного').click();
        cy.get('.Quantity__value').should('have.text', '0');
        cy.get('.Quantity__action_active').click();
        cy.get('.Quantity__value').should('have.text', '1');
        cy.get('.Select-placeholder').contains('Детское кресло').click();
        cy.get('.is-open').contains('Бустер').click();
        cy.get('.amber-button__text').contains('Закрыть').click();
        cy.get('.Select-placeholder_with-value').should('exist');
        //проверить что в ручке уходят требования
        cy.get('.OrderForm__submit').should('exist').should('not.be.disabled').click();
        cy.wait('@newOrder')
            .its('request.body')
            .then(body => {
                expect(body.requirements.animaltransport).eq(formData.animaltransport);
                expect(body.requirements.childchair_other).eq(formData.childchair_other);
                expect(body.requirements.luggage_count[0]).eq(formData.luggage_count);
            });
        cy.get('.Notification').contains('Заказ создан').should('exist');
    });
});
