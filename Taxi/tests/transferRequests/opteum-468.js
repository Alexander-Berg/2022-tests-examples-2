const PaymentRules = require('../../page/transferRequests/PaymentRules.js');

describe('Переход в раздел "Заявки на перевод средств" из "Правила выплат"', () => {
    it('открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('Нажать на стрелку "Назад" в левом верхнем углу страницы', () => {
        PaymentRules.btnBack.waitForDisplayed();
        PaymentRules.btnBack.click();
    });

    it('открылся раздел "Правила выплат"', () => {
        expect(browser).toHaveUrlContaining('/instant-payouts?');
    });
});
