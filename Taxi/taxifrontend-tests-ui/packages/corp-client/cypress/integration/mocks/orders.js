context('Страница заказа', () => {
    beforeEach(() => {
        cy.yandexLogin('autotestcorp');
    });
    context('Ошибки при работе с сервером', () => {
        it('corptaxi-1044: Список заказов - ошибка ручки', () => {
            cy.server();
            cy.route({
                method: 'GET',
                url: '/api/1.0/client/*/order*',
                status: 500,
                response: {
                    errors: [
                        {
                            text: 'Очень очень длинный текст ошибки, просто совершенно невообразимой длины.'
                        },
                        {
                            text: 'Очень очень длинный текст ошибки, просто совершенно невообразимой длины.'
                        }
                    ]
                }
            });
            cy.visit('/orders');
            cy.get('.Notification_show').should('exist').and('be.visible');
            cy.get('div.amber-alert').should('exist').and('have.class', 'amber-alert_type_error');
            cy.get('.Notification_show .amber-alert__close').should('exist').click();
            cy.get('.Notification_show .amber-alert__close').should('not.exist');
        });
    });
});
