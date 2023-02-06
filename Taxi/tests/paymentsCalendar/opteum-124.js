const RegularCharges = require('../../page/RegularCharges');

const testData = {
    driver: 'Крюков',
    vehicle: 'А333АА99',
    amount: '10',
    oneDay: '1',
};

describe('Добавление нового списания с выходным', () => {
    it('Открыть страницу Календарь списаний', () => {
        RegularCharges.goTo();
    });

    it('Открыть форму нового списания и заполнить данными', () => {
        RegularCharges.firstChargeInList.waitForDisplayed();
        RegularCharges.addChargesButton.click();
        RegularCharges.onScheduleAlgorithm.click();
    });

    it('Заполнить форму нового списания данными', () => {
        RegularCharges.clearWithBackspace(RegularCharges.workingDaysInput);
        RegularCharges.workingDaysInput.setValue(testData.oneDay);

        RegularCharges.clearWithBackspace(RegularCharges.weekendInput);
        RegularCharges.weekendInput.setValue(testData.oneDay);

        RegularCharges.addChargesByRequiredFields(testData);
    });

    it('Открыть созданное списание', () => {
        RegularCharges.goTo();
        RegularCharges.firstChargeInList.waitForDisplayed();
        RegularCharges.firstChargeInList.click();
    });

    it('Проверить данные в созданном списании', () => {
        RegularCharges.addChargesFormDivs.driver.waitForDisplayed();

        expect(RegularCharges.addChargesFormDivs.driver).toHaveTextIncludes(testData.driver);
        expect(RegularCharges.addChargesFormDivs.vehicle).toHaveTextIncludes(testData.vehicle);

        expect(RegularCharges.addChargesFormDivs.amount).toHaveAttributeStartsWith('value', testData.amount);
        expect(RegularCharges.workingDaysInput).toHaveAttributeEqual('value', testData.oneDay);
        expect(RegularCharges.weekendInput).toHaveAttributeEqual('value', testData.oneDay);
    });

    it('Удалить списание', () => {
        RegularCharges.goTo();
        RegularCharges.deleteChargesFromList();
    });
});
