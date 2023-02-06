const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const {randomNumBetween} = require('../../../../utils/number.js');

const driverLicense = '77783232';
const driverName = 'MAN Z.';
const startDate = '03.02.2022';
const alertTitle = 'Водитель не будет сохранён';
const alertText = 'Если у вас остались вопросы, вы можете написать обращение в службу поддержки';

const fillRequiredFields = function() {
    const randomNumber = randomNumBetween(10_000_000_000, 99_999_999_999);
    DriverCard.firstName.setValue(randomNumber);
    DriverCard.lastName.setValue(randomNumber);
    DriverCard.phoneNumber.setValue(randomNumber);

    for (let i = 0; i < 3; i++) {
        $$('.Textinput >button')[i].click();
        browser.keys('Enter');
        browser.pause(1000);
    }

    return randomNumber;
};

describe('Создание платного водителя: модальные окна', () => {
    it('Нажать "+" в заголовке списка водителей', () => {
        DriversPage.goTo();
        DriversPage.addDriverButton.waitForDisplayed();
        DriversPage.addDriverButton.click();
        DriverCard.waitingLoadThisPage(15_000);
    });

    it(`Заполнить поле "Серия и номер ВУ" одним из ВУ платного найма: ${driverLicense}`, () => {
        DetailsTab.detailsBlock.driverLicense.setValue(driverLicense);
        expect(DetailsTab.detailsBlock.paidToUs.tooltip).toBeDisplayed();
    });

    it('Заполнить обязательные поля случайными валидными данныим', () => {
        fillRequiredFields();
    });

    it('нажать на кнопку "Сохранить"', () => {
        DriverCard.saveButton.click();
        expect(DetailsTab.paidToUsModalWindow.window).toBeDisplayed();
        expect(DetailsTab.paidToUsModalWindow.text).toHaveTextIncludes(driverName);
        expect(DetailsTab.paidToUsModalWindow.text).toHaveTextIncludes(startDate);
    });

    it('нажать на кнопку "Нет"', () => {
        DetailsTab.paidToUsModalWindow.btnNo.waitForDisplayed();
        DetailsTab.paidToUsModalWindow.btnNo.click();
        expect(DetailsTab.paidToUsAlert.window).toBeDisplayed();
        expect(DetailsTab.paidToUsAlert.title).toHaveText(alertTitle);
        expect(DetailsTab.paidToUsAlert.text).toHaveText(alertText);
    });

    it('нажать на кнопку "Понятно"', () => {
        DetailsTab.paidToUsAlert.btnUnderstand.click();
        expect(DetailsTab.paidToUsAlert.window).not.toBeDisplayed();
    });
});
