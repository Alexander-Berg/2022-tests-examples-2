cy.orders = {
    generateExport(stage, from, to) {
        switch (stage) {
            case 'period':
                cy.get('.amber-button_theme_accent > .amber-button__text')
                    .contains('Экспорт')
                    .click();
                cy.xpath('(//span[@class="amber-radio__radio"])[3]').click();
                cy.get('[name="from"]').clear().type(from);
                cy.get('[name="to"]').clear().type(to);
                break;

            case 'current':
                cy.get('.amber-button_theme_accent > .amber-button__text')
                    .contains('Экспорт')
                    .click();
                cy.xpath('(//span[@class="amber-radio__radio"])[1]').click();
                break;

            case 'last':
                cy.get('.amber-button_theme_accent > .amber-button__text')
                    .contains('Экспорт')
                    .click();
                cy.xpath('(//span[@class="amber-radio__radio"])[2]').click();
                break;
        }
        cy.get('.ControlGroup > .amber-button').contains('Сформировать отчёт').click();
        cy.wait('@generateExport').should(xhr => {
            expect(xhr.status).to.equal(200);
        });
    },
    closeExportModal() {
        cy.get('.ModalCloseButton').click();
        cy.get('amber-modal__window-inner').should('not.exist');
    },
    selectService(serviceName) {
        cy.get('.MuiSelect-root', {timeout: 10000}).click();
        cy.get('.MuiButtonBase-root').contains(serviceName).click();
    }
};
