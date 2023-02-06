const RegularCharges = require('../../page/RegularCharges');

describe('Создание периодического списания: Алгоритмы по активности', () => {

    const testData = {
        driver: 'Ефременков',
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

    it('В блоке "Алгоритм" выбрать "по активности"', () => {
        RegularCharges.addChargesForm.algorithm.byActivity.click();
    });

    it('Заполнить форму списания и нажать "Сохранить"', () => {
        RegularCharges.addChargesByRequiredFields(testData);
    });

    it('Списание создано', () => {
        expect(RegularCharges.getRow(1).driver).toHaveTextIncludes(testData.driver);
        expect(RegularCharges.getRow(1).paymentFor).toHaveTextIncludes(testData.vehicle);
    });

    it('В карточке списания выбран соответствующий алгоритм', () => {
        RegularCharges.getRow(1).id.click();
        expect(RegularCharges.addChargesForm.algorithm.byActivity).toHaveAttributeIncludes('class', 'RadioButton-Radio_checked');
    });

    it('Отменить созданное списание', () => {
        RegularCharges.goTo();
        RegularCharges.deleteChargesFromList();
    });

});
