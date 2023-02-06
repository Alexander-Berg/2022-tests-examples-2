const DriverCard = require('../../page/driverCard/DriverCard');
const PaymentRules = require('../../page/transferRequests/PaymentRules');
const {nanoid} = require('nanoid');

const testData = {
    name: `autotest-opteum-482-${nanoid(10)}`,
    transferFee: '0',
    minFee: '1',
    minRequestAmount: '1',
    maxRequestAmount: '1',
    maxWithdrawalAmount: '1',
    minBalance: '9999999',
    checkboxUseByDefault: 'true',
};

describe('Правила выплат: создание правила - использовать правило по умолчанию', () => {
    it('Открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('Нажать кнопку создания нового правила', () => {
        PaymentRules.btnAdd.click();
    });

    it('открылась форма создания правила', () => {
        PaymentRules.createSideMenu.block.waitForDisplayed();
    });

    it('в форме присутствует чекбокс "Использовать по умолчанию"', () => {
        expect(PaymentRules.createSideMenu.inputs.checkboxUseByDefault).toBePresent();
    });

    it('Заполнить форму "Новое правило выплат"', () => {
        PaymentRules.fillSideMenuInputs(testData);
    });

    it('Нажать "Сохранить и добавить водителей"', () => {
        PaymentRules.createSideMenu.btnSave.click();
    });

    it('Перейти в форму создания водителя', () => {
        PaymentRules.open('/drivers/create/driver');
        DriverCard.waitingLoadThisPage(15_000);
    });

    it('в селекторе выбора правила моментальных выплат по умолчанию выбрано правило из шага 1', () => {
        expect(DriverCard.createDriverForm.instantPayouts).toHaveTextEqual(testData.name);
    });
});
