import Page from './Page';

class LimitsPage extends Page {
    clickAddNewLimitBtn() {
        cy.xpath(`(//button[@type='button'])[2]`, {timeout: 15000}).click();
        return this;
    }

    enterTitle(title) {
        cy.get('[placeholder="Название лимита"]').clear().type(title);
        return this;
    }

    chooseService(service) {
        cy.get('input[name="service"]').click().xpath(`//span[text()='${service}']`).click();
        return this;
    }

    getCostValue(service) {
        return cy.get(`input[name="${service}.limits.orders_cost.value"]`);
    }

    getOrdersAmount(service) {
        return cy.get(`input[name="${service}.limits.orders_amount.value"]`);
    }

    chooseRestrictions(service, restrictions) {
        cy.get(
            `input[name="${service}.customFormState.restrictions.${restrictions}.isActive"`
        ).click();
        return this;
    }

    fillRestrictionsDateTime(service, restrictions, value) {
        return cy
            .get(`input[name="${service}.customFormState.restrictions.${restrictions}"`)
            .click()
            .clear()
            .type(value);
    }

    fillRestrictionsDaysType(service, restrictions, daysType) {
        return cy
            .get(`input[name="${service}.customFormState.restrictions.${restrictions}"`)
            .click()
            .next()
            .xpath(`//span[text()='${daysType}']`)
            .click();
    }

    fillRestrictionDisctrict(service, restrictions, district) {
        return cy
            .get(`input[name="${service}.geo_restrictions.${restrictions}"`)
            .click()
            .type(district)
            .next()
            .xpath(`//span[text()='${district}']`)
            .click();
    }

    fillRestrictionsInterval(from, to) {
        cy.xpath('//*[text()="Период"]/..//input').click();
        cy.xpath('(//*[@role="tooltip"]//input)[1]').click().type(from);
        cy.xpath('(//*[@role="tooltip"]//input)[2]').click().type(to);
        // мисклик для закрытия тултипа с выбором даты
        cy.get('[id="application"]').click();
    }

    fixtureAllLimits() {
        cy.intercept('GET', '/api/2.0/limits?offset=0&limit=30&sorting_direction=1&skip=0', {
            fixture: 'responses/limits/limits.json'
        });
        return this;
    }

    fixtureViewLimit(limitId, serviceName) {
        cy.intercept('GET', `/api/2.0/limits/${limitId}`, {
            fixture: `responses/limits/limits${serviceName}.json`
        });

        cy.intercept('DELETE', `/api/2.0/limits/${limitId}`, {
            body: {}
        }).as('removeLimits');
    }

    responseAfterSaveLimits() {
        cy.intercept('POST', '/api/2.0/limits', {
            _id: '123456789'
        }).as('saveLimits');
        return this;
    }

    responseAfterChangeLimits() {
        cy.intercept('PUT', '/api/2.0/limits/*', {}).as('saveChangeLimits');
        return this;
    }

    fixtureTariffs() {
        cy.intercept('GET', `/api/1.0/class`, {
            fixture: `responses/limits/tariffs.json`
        });
        return this;
    }

    clickDeleteLimitBtn() {
        cy.xpath(`//button[@type='submit']/../../div//*[@type="button"]`, {timeout: 15000})
            .eq(1)
            .click();
    }

    removeTariffClass(tariff) {
        cy.xpath(`//span[text()='${tariff}']/following-sibling::*[name()="svg"]`).click();
        return this;
    }

    unselectTariffClass(tariff) {
        cy.get('[role="presentation"]').find('li').contains(tariff).click();
        return this;
    }

    getExistingLimit(limitName) {
        return cy.xpath(`//div[text()='${limitName}']`, {timeout: 10000});
    }
}

export default LimitsPage;
