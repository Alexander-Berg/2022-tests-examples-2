describe('Позитивные сценарии заказа такси c дополнительными проверками функционала формы', () => {
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
        cy.intercept('GET', '/api/1.0/zoneinfo?*', {
            fixture: 'responses/zoneinfo/index.json'
        }).as('zoneinfo');
        cy.intercept('GET', '/api/2.0/users*', {
            fixture: 'responses/client/users'
        }).as('users');
        cy.intercept('GET', '/api/1.0/client/02ecd60194a24d51ada6ecae87ef1ab7/cost_centers', {
            fixture: 'responses/client/cost-centres.json'
        }).as('costCentres');
        cy.corpOpen('/order');
    });

    it('corptaxi-1009: Заказ такси. Заполнение точки А из подсказки', () => {
        window.localStorage.setItem(
            `02ecd60194a24d51ada6ecae87ef1ab7.geoHistory.source`,
            '{"city":"Москва","country":"Россия","description":"Москва, Россия","exact":true,"full_text":"Россия, Москва, Садовническая улица, 82с3","house":"82с3","object_type":"другое","oid":"1623521189","point":[37.64101838896652,55.73586460441729],"short_text":"Садовническая улица, 82с3","short_text_from":"Садовническая улица, 82с3","short_text_to":"Садовническая улица, 82с3","street":"Садовническая улица","type":"address"}'
        );
        cy.intercept('POST', '/api/1.0/client/*/order*', {
            fixture: 'responses/order/200'
        }).as('order');
        cy.get('.OrderForm__submit').should('exist').should('be.disabled');
        cy.get('.OrderFormUser input').should('exist').focus().type('+7 (909) 678 56 45');
        cy.xpath('//*[text()="Dasha"]').click();
        cy.get('.OrderRoute__sample > .amber-link').contains('Садовническая улица, 82с3').click();
        cy.get('input[placeholder="Откуда"].amber-input__control')
            .invoke('attr', 'value')
            .should('contain', 'Садовническая улица, 82с3');
        cy.get('.OrderForm__submit').should('exist').should('not.be.disabled').click();
        cy.location('pathname').should('eq', '/order/82fb7d49656a3c51a4ae244b3a8d3c80');
    });

    context('Проверка отправленных данных в ручке заказа', () => {
        beforeEach(() => {
            cy.intercept('POST', '/api/1.0/client/*/order', {
                statusCode: 200
            }).as('newOrder');
        });

        const formData = {
            class: 'business',
            cost_center_values: 'Центр затрат',
            childchair_other: 1
        };

        it('corptaxi-1010: Заказ такси. Центр затрат', () => {
            cy.get('.OrderForm__submit').should('exist').should('be.disabled');
            cy.get('.OrderFormUser input').should('exist').focus().type('+79096785645');
            cy.wait('@users');
            cy.get('.SuggestOption').should('exist').contains('+7 (909) 678 56 45').click();
            cy.get('.FormSource').find('input').focus().type('Москва БЦ Аврора');
            cy.get('.SuggestOption_selected').contains('Аврора').click();
            cy.xpath('(//input[@placeholder="Центр затрат"])').type('Центр затрат');
            cy.get('.OrderForm__submit', {timeout: 10000})
                .should('exist')
                .should('not.be.disabled')
                .click();
            cy.wait('@newOrder')
                .its('request.body')
                .then(body => {
                    expect(body.cost_center_values[0].value).eq(formData.cost_center_values);
                });
        });

        it('corptaxi-1011: Заказ такси с недефолтным тарифом', () => {
            cy.get('.OrderForm__submit').should('exist').should('be.disabled');
            cy.get('.OrderFormUser input').should('exist').focus().type('+79096785645');
            cy.wait('@users');
            cy.get('.SuggestOption').should('exist').contains('+7 (909) 678 56 45').click();
            cy.get('.FormSource').find('input').focus().type('Москва БЦ Аврора');
            cy.get('.SuggestOption_selected').contains('Аврора').click();
            cy.get('div.Select-value').contains('Эконом').click();
            cy.get('div.is-open').contains('Комфорт').click();
            cy.get('.OrderForm__submit').should('exist').should('not.be.disabled').click();
            cy.wait('@newOrder')
                .its('request.body')
                .then(body => {
                    expect(body.class).eq(formData.class);
                });
        });
    });
});
