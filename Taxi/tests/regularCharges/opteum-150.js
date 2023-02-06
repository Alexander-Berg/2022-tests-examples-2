const RegularCharges = require('../../page/RegularCharges');

describe('Создание периодического списания: Тип Устройство', () => {

    const testData = {
        driver: 'Белотицкий',
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

    it('В блоке "За что" в поле "Тип" указать "Устройство"', () => {
        RegularCharges.addChargesForm.type.click();
        RegularCharges.selectList[3].click();
    });

    it('Заполнить форму списания и нажать "Сохранить"', () => {
        RegularCharges.addChargesByRequiredFields(testData);
    });

    it('Списание создано', () => {
        expect(RegularCharges.getRow(1).driver).toHaveTextIncludes(testData.driver);
        expect(RegularCharges.getRow(1).paymentFor).toHaveTextEqual('Устройство');
    });

    it('Отменить созданное списание', () => {
        RegularCharges.deleteChargesFromList();
    });

});
