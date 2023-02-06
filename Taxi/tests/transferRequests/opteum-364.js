const TransferRequests = require('../../page/transferRequests/TransferRequests.js');

describe('Переход в раздел графиков по моментальным выплатам', () => {
    it('открыть раздел "Заявки на перевод средств"', () => {
        TransferRequests.goTo();
    });

    it('Навести курсор на кнопку открытия раздела графиков', () => {
        TransferRequests.chartsBtn.moveTo();
    });

    it('появился ховер "Графики по моментальным выплатам"', () => {
        expect(TransferRequests.chartsBtnPopup).toBeDisplayed();
        expect(TransferRequests.chartsBtnPopup).toHaveTextEqual('Графики по моментальным выплатам');
    });

    it('Нажать на кнопку открытия раздела графиков', () => {
        TransferRequests.chartsBtn.click();
    });

    it('открылся раздел графиков по моментальным выплатам', () => {
        expect(browser).toHaveUrlContaining('/stats/instant-payouts');
    });
});
