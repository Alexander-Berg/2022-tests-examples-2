const RegularCharges = require('../../page/RegularCharges');
const {assert} = require('chai');

let firstChargeNumber;

describe('Прекратить списание', () => {
    it('Открыть страницу Периодические списания', () => {
        RegularCharges.goTo();
    });

    it('Открыть первое в списке списание и прекратить его', () => {
        RegularCharges.firstChargeInList.waitForDisplayed();
        firstChargeNumber = RegularCharges.firstChargeInList.getText();
        RegularCharges.deleteChargesFromList();
    });

    it('Проверить номер первого списания в списке после', () => {
        browser.pause(3000);
        assert.notEqual(RegularCharges.firstChargeInList.getText(), firstChargeNumber);
    });
});
