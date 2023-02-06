const LegalDocuments = require('../../page/LegalDocuments.js');

describe('Открытие и подписание оферты "Оферта по логистическим заказам"', () => {
    it('открыть раздел "Правовые документы"', () => {
        LegalDocuments.goTo();
    });

    it('выбрать "Оферта по логистическим заказам"', () => {
        LegalDocuments.navBar.items.logistic.click();
    });

    it('Открылась страница отправки формы согласия и принятия оферты', () => {
        const link = LegalDocuments.navBar.items.logisticLink.getAttribute('href');
        browser.pause(250);
        browser.switchWindow(link);
    });

    it('На странице присутствует информация "Оферта по логистическим заказам Если вы заполняли форму ранее, то отправлять заявку повторно не требуется."', () => {
        expect(LegalDocuments.logisticsOffer.header).toBeDisplayed();
        expect(LegalDocuments.logisticsOffer.header).toHaveTextEqual('Оферта по логистическим заказам');
        expect(LegalDocuments.logisticsOffer.info).toBeDisplayed();
        expect(LegalDocuments.logisticsOffer.info).toHaveTextEqual('Если вы заполняли форму ранее, то отправлять заявку повторно не требуется.');
    });

    it('На странице есть пустой чекбокс со ссылкой на оферту', () => {
        expect(LegalDocuments.logisticsOffer.checkbox).toBeDisplayed();
        expect(LegalDocuments.logisticsOffer.checkbox).toHaveValue('');
        expect(LegalDocuments.logisticsOffer.checkboxLink).toBeDisplayed();
        expect(LegalDocuments.logisticsOffer.checkboxLink).toHaveAttributeEqual('href', 'https://yandex.ru/legal/logistics_corporate_offer');
        expect(LegalDocuments.logisticsOffer.checkboxText).toBeDisplayed();
        expect(LegalDocuments.logisticsOffer.checkboxText).toHaveTextContaining('Я ознакомился, согласен и полностью принимаю условия ');
    });

    it('На странице есть неактивная кнопка "Отправить"', () => {
        expect(LegalDocuments.logisticsOffer.button).toBeDisplayed();
        expect(LegalDocuments.logisticsOffer.button).toBeDisabled();
    });

    it('отметить чекбокс', () => {
        LegalDocuments.logisticsOffer.checkboxClickable.click();
    });

    it('кнопка "Отправить" стала активной', () => {
        expect(LegalDocuments.logisticsOffer.button).not.toBeDisabled();
    });

    it('нажать на кнопку "Отправить"', () => {
        LegalDocuments.logisticsOffer.button.click();
    });

    it('форма исчезла', () => {
        expect(LegalDocuments.logisticsOffer.header).not.toBeDisplayed();
    });

    it('открылось окно с сообщением: "Спасибо, ваша заявка принята."', () => {
        expect(LegalDocuments.logisticsOffer.issueApplyText).toBeDisplayed();
        expect(LegalDocuments.logisticsOffer.issueApplyText).toHaveTextEqual('Спасибо, ваша заявка принята.');
    });
});
