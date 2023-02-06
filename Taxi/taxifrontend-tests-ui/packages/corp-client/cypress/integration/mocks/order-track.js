describe('Форма трекинга заказа', () => {
    beforeEach(() => {
        cy.yandexLogin('autotestcorp');
        cy.prepareLocalStorage();

        cy.intercept('GET', '/api/1.0/client/*/order/*/?show_cancel_text=true', {
            fixture: 'responses/order/200-fresh-order-cancel-text'
        });
        cy.intercept('GET', '/api/1.0/client/*/order/*', {
            fixture: 'responses/order/200-fresh-order'
        });
        cy.intercept('GET', '/api/1.0/client/*/order/*/progress', {
            fixture: 'responses/order/progress/200-fresh'
        });
    });

    function assertOrderTracking() {
        cy.get('.OrderTrack__content', {timeout: 10000}).as('OrderTrack').should('exist');
    }

    context('Свежий заказ', () => {
        beforeEach(() => {
            cy.visit('/order/fresh-order');
            assertOrderTracking();
        });

        it('corptaxi-1014: Есть свежий заказ: Заказать еще', () => {
            cy.get('@OrderTrack')
                .find('.amber-button')
                .contains('Заказать')
                .should('exist')
                .click();
            cy.url().should('match', /\/order$/);
            cy.get('.OrderForm', {timeout: 10000}).should('be.visible');
        });

        it('corptaxi-1015: Есть свежий заказ: Отмена заказа', () => {
            cy.intercept('POST', '/api/1.0/client/*/order/*/cancel', {
                body: {status: 'ok'}
            });
            cy.get('@OrderTrack')
                .find('.amber-button')
                .contains('Отменить')
                .should('exist')
                .click();
            cy.get('.CancelOrderModal')
                .should('exist')
                .contains('отменить')
                .should('exist')
                .click();
            cy.url().should('match', /\/order$/);
            cy.get('.OrderForm', {timeout: 10000}).should('be.visible');
        });

        it('corptaxi-1016: Есть свежий заказ: Невозможно отменить заказ', () => {
            cy.intercept('POST', '/api/1.0/client/*/order/*/cancel', {
                statusCode: 403,
                body: {}
            });
            cy.get('@OrderTrack').find('.amber-button').contains('Отменить').click();
            cy.get('.CancelOrderModal')
                .should('exist')
                .contains('отменить')
                .should('exist')
                .click();
            cy.get('.CancelOrderModal').find('.amber-alert').should('exist');
        });

        it('corptaxi-1017: Есть свежий заказ: закрыть окошко отмены заказа', () => {
            cy.get('@OrderTrack').find('.amber-button').contains('Отменить').click();
            cy.get('.CancelOrderModal').contains('Закрыть').click();
            cy.get('.CancelOrderModal').should('not.exist');
        });
    });

    it('corptaxi-1018: Есть отмененный заказ: Отображение', () => {
        cy.intercept('GET', '/api/1.0/client/*/order/*', {
            fixture: 'responses/order/200-cancelled'
        });
        cy.visit('/order/canceled-order');
        assertOrderTracking();

        cy.get('@OrderTrack').find('.amber-button').contains('Отменить').should('not.exist');
        cy.get('@OrderTrack').find('.amber-button').contains('Заказать').should('exist').click();
        cy.get('.OrderForm', {timeout: 10000}).should('be.visible');
    });

    it('corptaxi-1019: Заказ не найден', () => {
        cy.intercept('/api/1.0/client/*/order/does-not-exist', {
            statusCode: 404,
            body: {}
        });
        cy.visit('/order/does-not-exist');

        cy.get('.OrderTrackNotFound').should('exist');
    });
});
