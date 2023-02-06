import repeatOrder from '../../fixtures/responses/order/repeat-order.json';

describe('Позитивные сценарии заказа такси', () => {
    function makeOrder(phone, suggestUserName, from) {
        cy.get('.OrderForm__submit', {timeout: 10000}).should('exist').should('be.disabled');
        cy.get('.OrderFormUser input').should('exist').focus().type(phone);
        cy.wait('@users');
        cy.xpath(`//*[text()="${suggestUserName}"]`).click();
        cy.get('.FormSource').find('input').focus().type(from);
        cy.get('.SuggestOption_selected').contains(from).click();
        cy.get('.OrderForm__submit').should('exist').should('not.be.disabled').click();
    }

    beforeEach(() => {
        cy.intercept('POST', '/api/1.0/estimate', {
            fixture: 'responses/estimate/index.json'
        }).as('estimate');
        cy.intercept('POST', '/api/1.0/client/*/order/*/processing', {
            fixture: 'responses/order/processing/200'
        }).as('processing');
        cy.intercept('GET', '/api/1.0/zoneinfo?*', {
            fixture: 'responses/zoneinfo/index.json'
        }).as('zoneinfo');
    });

    it('corptaxi-1005: Повтор заказа такси', () => {
        cy.yandexLogin('autotestcorp');
        cy.prepareLocalStorage();
        cy.intercept('GET', '/api/1.0/client/*/order/d8fbba6ef5d5cee3a0a01ee6286c9593', {
            fixture: 'responses/order/repeat-order'
        }).as('repeat-order');
        cy.intercept('POST', '/api/1.0/client/*/order', {
            statusCode: 200
        }).as('newOrder');
        cy.visit('/order?previousOrderID=d8fbba6ef5d5cee3a0a01ee6286c9593');
        cy.wait('@estimate');

        cy.get('.OrderForm__submit', {timeout: 10000})
            .should('exist')
            .should('not.be.disabled')
            .click();
        cy.wait('@newOrder')
            .its('request.body')
            .then(body => {
                expect(body.class).eq(repeatOrder.class);
                expect(body.destination.fullname).eq(repeatOrder.destination.fullname);
                expect(body.source.fullname).eq(repeatOrder.source.fullname);
                expect(body.phone).eq(repeatOrder.corp_user.phone);
            });
        cy.get('.Notification').contains('Заказ создан').should('exist');
    });

    context('', () => {
        beforeEach(() => {
            cy.yandexLogin('autotestcorp');
            cy.prepareLocalStorage();
            cy.corpOpen('/order');
            cy.intercept('POST', '/client-api/3.0/geosearch', {
                fixture: 'responses/geosearch/geosearch'
            }).as('geosearch');
            cy.intercept('POST', '/api/1.0/client/*/order*', {
                fixture: 'responses/order/200'
            }).as('order');
        });

        it('corptaxi-1004: Заказ по номеру телефона существующего сотрудника (без точки Б)', () => {
            cy.intercept('GET', '/api/2.0/users*', {
                fixture: 'responses/client/users'
            }).as('users');
            makeOrder('+7 (909) 678 56 45', 'Dasha', 'Аврора');
            cy.location('pathname').should('eq', '/order/82fb7d49656a3c51a4ae244b3a8d3c80');
            cy.get('.Notification').contains('Заказ создан').should('exist');
        });

        it('corptaxi-1003: Заказ по номеру телефона нового сотрудника (без точки Б)', () => {
            cy.intercept('GET', '/api/2.0/users*', {
                body: {
                    items: [],
                    amount: 0,
                    skip: 0,
                    limit: 20,
                    sorting_field: 'due_date',
                    sorting_direction: 1,
                    search: '+79096785645'
                }
            }).as('users');
            makeOrder('+7 (909) 678 56 45', 'Новый телефон', 'Аврора');
            cy.location('pathname').should('eq', '/order/82fb7d49656a3c51a4ae244b3a8d3c80');
            cy.get('.Notification').contains('Заказ создан').should('exist');
        });

        it('corptaxi-1008: Получается сделать заказ с промежуточными точками (без точки Б)', () => {
            cy.intercept('GET', '/api/2.0/users*', {
                fixture: 'responses/client/users'
            }).as('users');
            cy.get('.OrderForm__submit', {timeout: 10000}).should('exist').should('be.disabled');
            cy.get('.OrderFormUser input').should('exist').focus().type('+79096785645');
            cy.wait('@users');
            cy.get('.SuggestOption').should('exist').contains('+7 (909) 678 56 45').click();
            cy.get('.FormSource').find('input').focus().type('Москва БЦ Аврора');
            cy.get('.SuggestOption_selected').contains('Аврора').click();
            cy.get('[placeholder="Куда"]').should($res => {
                expect($res).to.have.length(1);
            });
            cy.get('.OrderRoute__add').click();
            cy.get('[placeholder="Куда"]').should($res => {
                expect($res).to.have.length(2);
            });
            cy.xpath('(//input[@placeholder="Куда"])[1]').type('Красная Роза');
            cy.get('.SuggestOption__name').contains('Красная роза').click();
            cy.get('.OrderForm__submit').should('exist').should('not.be.disabled').click();
            cy.location('pathname').should('eq', '/order/82fb7d49656a3c51a4ae244b3a8d3c80');
            cy.get('.Notification').contains('Заказ создан').should('exist');
        });

        it('corptaxi-1002: Заказ с точками А и Б', () => {
            cy.intercept('GET', '/api/2.0/users*', {
                fixture: 'responses/client/users'
            }).as('users');
            cy.get('.OrderForm__submit', {timeout: 10000}).should('exist').should('be.disabled');
            cy.get('.OrderFormUser input').should('exist').focus().type('+79096785645');
            cy.wait('@users');
            cy.get('.SuggestOption').should('exist').contains('+7 (909) 678 56 45').click();
            cy.get('.FormSource').find('input').focus().type('Москва БЦ Аврора');
            cy.get('.SuggestOption_selected').contains('Аврора').click();
            cy.xpath('(//input[@placeholder="Куда"])').type('Красная Роза');
            cy.get('.SuggestOption__name').contains('Красная роза').click();
            cy.get('.OrderForm__submit').should('exist').should('not.be.disabled').click();
            cy.location('pathname').should('eq', '/order/82fb7d49656a3c51a4ae244b3a8d3c80');
            cy.get('.Notification').contains('Заказ создан').should('exist');
        });
    });

    context('Заказы под менеджером', () => {
        beforeEach(() => {
            cy.yandexLogin('autotestcorp-manager');
            cy.prepareLocalStorage();
            cy.corpOpen('/order');
            cy.intercept('POST', '/client-api/3.0/geosearch', {
                fixture: 'responses/geosearch/geosearch'
            }).as('geosearch');
            cy.intercept('POST', '/api/1.0/client/*/order*', {
                fixture: 'responses/order/200'
            }).as('order');
        });

        it('corptaxi-1007: Заказ на сотрудника из другого департамента с аккаунта менеджера', () => {
            cy.intercept('GET', '/api/2.0/users*?limit=*&search=*&department_id=*', {
                body: {
                    items: [],
                    amount: 0,
                    skip: 0,
                    limit: 20,
                    sorting_field: 'due_date',
                    sorting_direction: 1,
                    search: '+79096785645'
                }
            }).as('users');
            cy.intercept('GET', '/api/1.0/client/*/user/*', {
                statusCode: 403,
                body: {
                    message: 'Access denied'
                }
            }).as('afterOrder');
            makeOrder('+7 (909) 678 56 45', 'Новый телефон', 'Аврора');
            cy.wait('@afterOrder');
            cy.location('pathname').should('eq', '/order');
            cy.get('.Notification').contains('Заказ создан').should('exist');
        });
    });
});
