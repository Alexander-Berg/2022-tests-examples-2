const RegularCharges = require('../../page/RegularCharges');

describe('Создание периодического списания: Тип Общее', () => {

    const testData = {
        driver: 'Паукаев',
        vehicle: 'А333АА99',
        amount: '10',
        oneDay: '1',
    };

    it('Открыт раздел "Периодические списания"', () => {
        RegularCharges.goTo();
    });

    it('Нажать "+" создания нового списания', () => {
        RegularCharges.addChargesButton.click();
    });

    it('В блоке "За что" в поле "Тип" указать "общее"', () => {
        RegularCharges.addChargesForm.type.click();
        RegularCharges.selectList[0].click();
    });

    it('Заполнить форму списания и нажать "Сохранить"', () => {
        RegularCharges.addChargesByRequiredFields(testData);
    });

    it('Списание создано', () => {
        expect(RegularCharges.getRow(1).driver).toHaveTextIncludes(testData.driver);
        expect(RegularCharges.getRow(1).paymentFor).toHaveTextIncludes(testData.vehicle);
    });

    it('Отменить созданное списание', () => {
        RegularCharges.goTo();
        RegularCharges.deleteChargesFromList();
    });

});
