const SupportMessagesList = require('../../page/SupportMessagesList.js');

const testData = {
    theme: 'Заказать обратный звонок',
    phoneNumber: '+70001259508',
};

describe('Заказ обратного звонка: создать обращение с данными по умолчанию', () => {
    it('Нажать на иконку телефонной трубки в заголовке страницы', () => {
        SupportMessagesList.goTo();
        SupportMessagesList.phoneBtn.waitForDisplayed();
        SupportMessagesList.phoneBtn.click();
        SupportMessagesList.createMessageForm.waitForDisplayed();
    });

    it('Проверить данные формы', () => {
        expect(SupportMessagesList.createMessageThemeFormInputs.theme).toHaveTextContaining(testData.theme);
        expect(SupportMessagesList.selectedPhone).toHaveTextContaining(testData.phoneNumber);
    });

    it('Отправить обращение не заполняя остальные поля', () => {
        SupportMessagesList.sendIssueAndCheckResponse();
        SupportMessagesList.alert.waitForDisplayed();
        expect(SupportMessagesList.alert).toHaveText('Ваше обращение зарегистрировано');
    });

    it('Нажать на данное обращение в списке обращений', () => {
        $('tr td').click();
        $('div[class*="SupportChat_container"]').waitForDisplayed();
    });

    it('Проверить данные обращения', () => {
        expect(SupportMessagesList.supportChat.infoMessage.theme).toHaveTextContaining(testData.theme);
        expect(SupportMessagesList.supportChat.infoMessage.subTheme).toHaveTextContaining(testData.phoneNumber);
    });
});
