context('Карточка сотрудника', () => {
    beforeEach(() => {
        cy.server();
        cy.yandexLogin('autotestcorp');
        cy.route(
            '/api/1.0/client/*/user/*/order?skip=*',
            'fixture:responses/user/order/list'
        )
        cy.visit('/users/023634d03e764236ac2954d28dbef4ae');
    });

    it('corptaxi-970: Список поездок сотрудника', () => {
        cy.get('.UserOrders')
            .should('exist')
            .find('> .RowGroup')
            .its('length')
            .should('be.greaterThan', 0);
    });
});
