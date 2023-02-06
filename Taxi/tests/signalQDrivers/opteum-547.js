const SignalQDriverCard = require('../../page/signalq/SignalQDriverCard');
const SignalQDrivers = require('../../page/signalq/SignalQDrivers');

describe('SignalQ: водители: профиль водителя: редактирование', () => {

    const newData = {
        lastName: 'newlastName',
        firstName: 'newfirstName',
        middleName: 'newmiddleName',
        license: 'NEWLICENSE',
        dateHired: '02.02.2002',
        phone: '+79046073333',
    };

    const oldData = {
        lastName: '',
        firstName: '',
        middleName: '',
        license: '',
        dateHired: '',
        phone: '',
    };

    it('Открыт раздел "Водители SignalQ"', () => {
        SignalQDrivers.goTo();
    });

    it('Нажать на любого водителя в таблице', () => {
        SignalQDrivers.getRow().name.click();
        SignalQDrivers.switchTab();
        SignalQDriverCard.driverFullName.waitForDisplayed();
    });

    it('Сохранить старые данные', () => {
        oldData.lastName = SignalQDriverCard.lastName.getText();
        oldData.firstName = SignalQDriverCard.firstName.getText();
        oldData.middleName = SignalQDriverCard.middleName.getText();
        oldData.license = SignalQDriverCard.license.getText();
        oldData.dateHired = SignalQDriverCard.dateHired.getText();
        oldData.phone = SignalQDriverCard.phone.getText();
    });

    Object.keys(newData).forEach(key => {
        it(`Изменить поле ${key}`, () => {
            SignalQDriverCard[key].click();
            SignalQDriverCard.clearWithBackspace(SignalQDriverCard.focusedInput);
            SignalQDriverCard.focusedInput.addValue(newData[key]);
            browser.keys('Enter');
        });

        it('Поле изменилось', () => {
            expect(SignalQDriverCard[key]).toHaveTextEqual(newData[key]);
        });

        it('Вернуть старые значения', () => {
            SignalQDriverCard[key].click();
            SignalQDriverCard.clearWithBackspace(SignalQDriverCard.focusedInput);
            SignalQDriverCard.focusedInput.addValue(oldData[key]);
            browser.keys('Enter');
        });
    });

});
