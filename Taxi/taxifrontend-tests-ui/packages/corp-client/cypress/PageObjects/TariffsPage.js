import Page from './Page';

class TariffsPage extends Page {
    openTariffsByUrl(url) {
        cy.visit(url);
        // ожидание загрузки страницы
        cy.get('h2').contains('Тарифы для города');
        return this;
    }

    selectCity(city) {
        cy.get('[name="zone"]').click().clear().type(city);
        cy.xpath(`//span[text()="${city}"]`).click();
    }

    selectTariff(tariff) {
        cy.get('[name="tariff"]').click().clear().type(tariff);
        cy.xpath(`//span[text()="${tariff}"]`).click();
        return this;
    }

    selectTransfer(transfer) {
        cy.get('[placeholder="Трансферы"]').click().clear().type(transfer);
        cy.xpath(`//span[text()="${transfer}"]`).click();
        return this;
    }

    expectTariffHeadersShouldBeVisible() {
        cy.get('h6').contains('Посадка').should('be.visible');
        cy.get('h6').contains('Поездка за пределами города').should('be.visible');
        cy.get('h6').contains('Поездка далее по городу').should('be.visible');
        cy.get('h6').contains('Дополнительные опции').should('be.visible');
    }

    expectTransferHeadersShouldBeVisible() {
        cy.xpath('//h6[text()="Трансферы"]/../..//*[text()="Посадка"]').should('be.visible');
        cy.xpath('//h6[text()="Трансферы"]/../..//*[text()="Поездка далее"]').should('be.visible');
    }
}

export default TariffsPage;
