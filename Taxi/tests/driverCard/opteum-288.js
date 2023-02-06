const DetailsTab = require('../../page/driverCard/DetailsTab');
const DriverCard = require('../../page/driverCard/DriverCard');
const DriversPage = require('../../page/DriversPage');
const moment = require('moment');
const SupportMessagesList = require('../../page/SupportMessagesList');
const {randomNumBetween} = require('../../../../utils/number.js');

const driverLicense = '77783232';

const formData = {
    theme: 'Вопросы о водителе',
    subTheme1: 'Платный найм',
    driverHiringName: '',
    driverLicense: '77783232',
    hiringDate: '',
    hiringDriverType: 'commercial',
    issueMessage: '',
};

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
        DriverCard.waitingLoadThisPage(10_000);
    });

    it(`Заполнить поле "Серия и номер ВУ" одним из ВУ платного найма: ${driverLicense}`, () => {
        DriversPage.type(DetailsTab.detailsBlock.driverLicense, driverLicense);
        DetailsTab.detailsBlock.paidToUs.tooltip.waitForDisplayed();
    });

    it('Заполнить обязательные поля случайными валидными данныим', () => {
        formData.driverHiringName = fillRequiredFields();
        formData.driverHiringName += ` ${formData.driverHiringName}`;
    });

    it('нажать на кнопку "Сохранить"', () => {
        DriverCard.saveButton.click();
        DetailsTab.paidToUsModalWindow.window.waitForDisplayed();
    });

    it('нажать на кнопку "Нет"', () => {
        DetailsTab.paidToUsModalWindow.btnNo.waitForDisplayed();
        DetailsTab.paidToUsModalWindow.btnNo.click();
        DetailsTab.paidToUsAlert.window.waitForDisplayed();
    });

    it('Нажать на кнопку "Написать"', () => {
        DetailsTab.paidToUsAlert.btnWrite.click();
        DetailsTab.paidToUsAlert.window.waitForDisplayed({reverse: true});
        SupportMessagesList.createMessageForm.waitForDisplayed();
    });

    it('Проверить данные сайд-меню', () => {
        formData.hiringDate = moment().format('YYYY-MM-DD');
        expect(SupportMessagesList.createMessageThemeFormInputs.theme).toHaveTextContaining(formData.theme);
        expect(SupportMessagesList.createMessageThemeFormInputs.subTheme1).toHaveTextContaining(formData.subTheme1);
        expect(SupportMessagesList.createMessageThemeFormInputs.driverLicense).toHaveValue(formData.driverLicense);
        expect(SupportMessagesList.createMessageThemeFormInputs.driverHiringName).toHaveValue(formData.driverHiringName);
        expect(SupportMessagesList.createMessageThemeFormInputs.hiringDate).toHaveValue(formData.hiringDate);
        expect(SupportMessagesList.createMessageThemeFormInputs.hiringDriverType).toHaveValue(formData.hiringDriverType);
        expect(SupportMessagesList.createMessageThemeFormInputs.issueMessage).toHaveTextContaining(formData.issueMessage);
    });

    it('Заполнить поля "Текст обращения" и "Файлы" случайными данными', () => {
        formData.issueMessage = 'test message';
        SupportMessagesList.createMessageThemeFormInputs.issueMessage.setValue(formData.issueMessage);
        SupportMessagesList.uploadImage();
        browser.pause(3000);
    });

    it('Нажать на кнопку "Отправить"', () => {
        SupportMessagesList.confirmIssueButton.click();
        const tost = $('span*=Ваше обращение зарегистрировано');
        expect(tost).toBeDisplayed();
    });

    it('открыть раздел "Мои обращения"', () => {
        SupportMessagesList.goTo();
    });

    it('Выбрать своё обращение в списке обращений', () => {
        const issue = $('td=Платный найм');
        issue.click();
        SupportMessagesList.supportChatBlock.waitForDisplayed();
    });

    it('Проверить данные обращения', () => {
        expect(SupportMessagesList.supportChatHeaders.status).toHaveText('В работе');
        expect(SupportMessagesList.supportChatHeaders.id).toBeDisplayed();
        expect(SupportMessagesList.supportChat.infoMessage.theme).toHaveTextContaining(formData.theme);
        expect(SupportMessagesList.supportChat.infoMessage.subTheme).toHaveTextContaining(formData.subTheme1);
        expect(SupportMessagesList.supportChat.infoMessage.driverLicense).toHaveTextContaining(formData.driverLicense);
        expect(SupportMessagesList.supportChat.infoMessage.driverHiringName).toHaveTextContaining(formData.driverHiringName);
        expect(SupportMessagesList.supportChat.infoMessage.hiringDate).toHaveTextContaining(formData.hiringDate);
        expect(SupportMessagesList.supportChat.infoMessage.hiringDriverType).toHaveTextContaining(formData.hiringDriverType);
        expect(SupportMessagesList.supportChat.imageMessage.img).toBeDisplayed();
        expect(SupportMessagesList.supportChat.imageMessage.text).toHaveTextContaining(formData.issueMessage);
    });
});
