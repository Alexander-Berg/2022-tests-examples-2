const RegularCharges = require('../../page/RegularCharges');

describe('Создание периодического списания: Тип Прочее', () => {

    const testData = {
        driver: 'Чичайкин',
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

    it('В блоке "За что" в поле "Тип" указать "Прочее"', () => {
        RegularCharges.addChargesForm.type.click();
        RegularCharges.selectList[4].click();
    });

    it('Заполнить форму списания и нажать "Сохранить"', () => {
        RegularCharges.addChargesByRequiredFields(testData);
    });

    it('Списание создано', () => {
        expect(RegularCharges.getRow(1).driver).toHaveTextIncludes(testData.driver);
        expect(RegularCharges.getRow(1).paymentFor).toHaveTextEqual('Прочее');
    });

    it('Отменить созданное списание', () => {
        RegularCharges.deleteChargesFromList();
    });

});
