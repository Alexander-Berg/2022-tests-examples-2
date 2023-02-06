const SupportMessagesList = require('../../page/SupportMessagesList.js');

const testData = {
    theme: 'Заказать обратный звонок',
    phoneNumber: '+70001259508',
    issueMessage: 'test message',
};

describe('Заказ обратного звонка: заполнение всей формы', () => {
    it('Нажать "+" в заголовке страницы', () => {
        SupportMessagesList.goTo();
        SupportMessagesList.addButton.waitForDisplayed();
        SupportMessagesList.addButton.click();
        SupportMessagesList.createMessageForm.waitForDisplayed();
    });

    it('Выбрать "Доступ: Всем"', () => {
        SupportMessagesList.accessRadioBtn.all.click();
    });

    it('Выбрать "Тема: Заказать обратный звонок"', () => {
        SupportMessagesList.createMessageThemeFormInputs.theme.click();
        SupportMessagesList.selectDropdownItem(testData.theme);
    });

    it('Заполнить все поля и прикрепить файл', () => {
        SupportMessagesList.createMessageThemeFormInputs.issueMessage.setValue(testData.issueMessage);
        SupportMessagesList.uploadImage();
        browser.pause(3000);
    });

    it('Нажать "Отправить"', () => {
        SupportMessagesList.sendIssueAndCheckResponse();
        SupportMessagesList.alert.waitForDisplayed();
        expect(SupportMessagesList.alert).toHaveText('Ваше обращение зарегистрировано');
    });

    it('Нажать на данное обращение в списке обращений', () => {
        $('tr td').click();
        $('div[class*="SupportChat_container"]').waitForDisplayed();
    });

    it('Проверить данные обращения', () => {
        expect(SupportMessagesList.supportChat.infoMessage.theme).toHaveTextIncludes(testData.theme);
        expect(SupportMessagesList.supportChat.infoMessage.subTheme).toHaveTextIncludes(testData.phoneNumber);
        expect(SupportMessagesList.supportChat.imageMessage.img).toBeDisplayed();
        expect(SupportMessagesList.supportChat.imageMessage.text).toHaveTextIncludes(testData.issueMessage);
    });
});
