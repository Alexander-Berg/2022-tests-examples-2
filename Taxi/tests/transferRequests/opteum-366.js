const TransferRequests = require('../../page/transferRequests/TransferRequests.js');

describe('Переход в раздел "Правила выплат"', () => {
    it('открыть раздел "Заявки на перевод средств"', () => {
        TransferRequests.goTo();
    });

    it('Нажать на ссылку "Правила выплат"', () => {
        TransferRequests.instantPayoutsRulesLink.waitForDisplayed();
        TransferRequests.instantPayoutsRulesLink.click();
    });

    it('открылся раздел "Правила выплат"', () => {
        expect(browser).toHaveUrlContaining('/instant-payouts/rules');
    });
});
