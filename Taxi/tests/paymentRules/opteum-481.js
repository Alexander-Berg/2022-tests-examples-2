const DriverCard = require('../../page/driverCard/DriverCard');
const PaymentRules = require('../../page/transferRequests/PaymentRules');

const testData = {
    checkboxUseByDefault: 'true',
};

let ruleName;

describe('Правила выплат: редактирование правила - использовать правило по умолчанию', () => {
    it('Открыть раздел "Правила выплат"', () => {
        PaymentRules.goTo();
    });

    it('Навести курсор на запись правила', () => {
        ruleName = PaymentRules.getColumn(1)[0].getText();
        PaymentRules.getRow(1).moveTo();
    });

    it('в строке с правилом отображаются две кнопки действия с правилом: добавление водителя и редактирование правила', () => {
        expect(PaymentRules.editButtons[0]).toBeDisplayed();
        expect(PaymentRules.driversButtons[0]).toBeDisplayed();
    });

    it('Нажать кнопку редактирования правила', () => {
        PaymentRules.editButtons[0].click();
    });

    it('открылась форма редактирования правила', () => {
        PaymentRules.createSideMenu.block.waitForDisplayed();
    });

    it('в форме присутствует чекбокс "Использовать по умолчанию"', () => {
        expect(PaymentRules.createSideMenu.inputs.checkboxUseByDefault).toBePresent();
    });

    it('Включить чекбокс "Использовать по умолчанию"', () => {
        PaymentRules.fillSideMenuInputs(testData);
    });

    it('Нажать на кнопку "Сохранить"', () => {
        PaymentRules.createSideMenu.btnSave.click();
    });

    it('Перейти в форму создания водителя', () => {
        PaymentRules.open('/drivers/create/driver');
        DriverCard.waitingLoadThisPage(15_000);
    });

    it('в селекторе выбора правила моментальных выплат по умолчанию выбрано правило из шага 1', () => {
        expect(DriverCard.createDriverForm.instantPayouts).toHaveTextEqual(ruleName);
    });
});
