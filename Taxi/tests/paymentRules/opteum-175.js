const PaymentRules = require('../../page/transferRequests/PaymentRules');

const testData = {
    name: `autotest-opteum-175-${Math.floor(Math.random() * 9_999_999_999)}`,
    transferFee: '0',
    minFee: '1',
    minRequestAmount: '1',
    maxRequestAmount: '1',
    maxWithdrawalAmount: '1',
    minBalance: '9999999',
    checkboxUseByDefault: 'false',
};

describe('Правила выплат: Новое правило', () => {
    it('Открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('Нажать кнопку создания нового правила', () => {
        PaymentRules.btnAdd.click();
    });

    it('Заполнить форму "Новое правило выплат"', () => {
        PaymentRules.createSideMenu.block.waitForDisplayed();
        PaymentRules.fillSideMenuInputs(testData);
    });

    it('Нажать "Сохранить и добавить водителей"', () => {
        PaymentRules.createSideMenu.btnSave.click();
    });

    it('появился тост "Успешно сохранено"', () => {
        expect(PaymentRules.alert).toHaveTextEqual('Успешно сохранено');
    });

    it('открылась форма добавления водителей', () => {
        expect(PaymentRules.createSideMenu.headerText).toHaveTextEqual(testData.name);
    });

    it('правило добавилось в список правил', () => {
        expect(PaymentRules.getColumn(1)[0]).toHaveTextEqual(testData.name);
    });

    it('правило включено', () => {
        expect(PaymentRules.getCheckboxesColumn()[0]).toHaveAttribute('checked');
    });
});
