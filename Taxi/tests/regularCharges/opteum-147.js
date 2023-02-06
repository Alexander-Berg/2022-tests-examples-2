const RegularCharges = require('../../page/RegularCharges');

describe('Создание периодического списания: СМЗ', () => {

    const testData = {
        driver: 'Безмятежный Образ',
        vehicle: 'Т555МТ444',
        amount: '10',
        oneDay: '1',
    };

    it('Открыт раздел "Периодические списания"', () => {
        RegularCharges.goTo();
    });

    it('Нажать "+" создания нового списания', () => {
        RegularCharges.addChargesButton.click();
    });

    it('Заполнить форму списания, указав СМЗ водителя и нажать "Сохранить"', () => {
        RegularCharges.addChargesByRequiredFields(testData);
    });

    it('Списание создано', () => {
        expect(RegularCharges.getRow(1).driver).toHaveTextIncludes(testData.driver);
    });

    it('Отменить созданное списание', () => {
        RegularCharges.deleteChargesFromList();
    });

});
