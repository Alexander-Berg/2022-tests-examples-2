const RegularCharges = require('../../page/RegularCharges');

describe('Создание периодического списания: Негатив', () => {
    const requiredField = 'Это поле необходимо заполнить';
    const amountHint = 'Сумма не может быть меньше 5';

    it('Открыт раздел "Периодические списания"', () => {
        RegularCharges.goTo();
    });

    it('Нажать "+" создания нового списания', () => {
        RegularCharges.addChargesButton.click();
    });

    it('Нажать кнопку "Сохранить"', () => {
        RegularCharges.addChargesForm.saveButton.click();
    });

    it('Отобразились Хинты', () => {
        expect(RegularCharges.addChargesForm.selectHint[0]).toHaveTextEqual(requiredField);
        expect(RegularCharges.addChargesForm.selectHint[1]).toHaveTextEqual(requiredField);
        expect(RegularCharges.addChargesForm.inputHint[0]).toHaveTextEqual(amountHint);
    });

    it('Очистить поле "сумма"', () => {
        RegularCharges.clearWithBackspace(RegularCharges.addChargesForm.amount);
    });

    it('Нажать кнопку "Сохранить"', () => {
        RegularCharges.addChargesForm.saveButton.click();
    });

    it('У поля "сумма" появился хинт "Это поле необходимо заполнить"', () => {
        expect(RegularCharges.addChargesForm.inputHint[0]).toHaveTextEqual(requiredField);
    });
});
