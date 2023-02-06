import {BasePageLocators} from '../../pageobjects/LocatorsPage'

describe('Тесты API woody', () => {
    it('LT-196-41 Получение токена авторизации', () => {
        cy.request({
            method: 'POST',
            url: 'http://localhost:8069/web/login',
            body: {
              username: 'User1',
              password: BasePageLocators.PASS,
            },
        }).then((response) => {
        cy.log(response.body);
        expect(response.status).equal(200)
        let token = response.headers['set-cookie'][0].split(';')[0].slice(11);
        cy.log(token)
        });
    })

    it.skip('LT-196-42 Получение информации о закупочном листе', () => {
        cy.request({
            method: 'GET',
            url: 'https://woody-il.lavka.tst.yandex.net/api/v1/vendor.assortment',
            body: {"auth":token,
            "store_id": "33e45753daa84a298edc4f1789f9ba24000200010000", 
            "contractor_id": "376000137",
            "cursor": null,
            "namespace": "vendor.assortment"},
        }).then((response) => {
        cy.log(response.body);
        expect(response.status).equal(200)
        });
    })
})


        