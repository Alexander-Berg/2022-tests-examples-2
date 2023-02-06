describe('Редактирование сотрудника', () => {
    beforeEach(() => {
        cy.yandexLogin('autotestcorp-profile');
        cy.prepareLocalStorage();
        cy.server();
        cy.visit('/');
    });
    context('У сотрудника отправлена ссылка на привязку', () => {
        it('corptaxi-1063: Привязка к драйву. Статус и кнопка "перепривязать"', () => {
            cy.visit('/users/e0c8ea7d44dc42fdbccb1fcde63be4c6?back=%2Fstaff');
            cy.get('.amber-button__icon').click();
            cy.get('.amber-tab').contains('Сервисы').click();
            cy.get('.amber-modal_scrollable').scrollTo('bottom');
            cy.get('.amber-button').contains('Привязать повторно').should('exist');
            cy.get('.amber-row_paddingTop-xs_m').contains('ссылка отправлена').should('exist');
        });
    });
    context('Сотрудник не был привязан к Драйву', () => {
        it('corptaxi-1064: Привязка к драйву. Сотрудник не привязан к драйву', () => {
            cy.visit('/users/51bfe61e13a2475085d9d042c76264d5?back=%2Fstaff');
            cy.get('.amber-button__icon').click();
            cy.get('.amber-tab').contains('Сервисы').click();
            cy.get('.amber-modal_scrollable').scrollTo('bottom');
            cy.get('.amber-row_paddingTop-xs_m').contains('не привязан').should('exist');
            cy.get('.amber-button').contains('Привязать').should('exist');
        });
    });
});
