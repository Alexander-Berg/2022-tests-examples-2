const LegalDocuments = require('../../page/LegalDocuments.js');

describe('Открытие оферты "Оферта по перевозке корпоративных пользователей"', () => {
    it('открыть раздел "Правовые документы"', () => {
        LegalDocuments.goTo();
    });

    it('выбрать "Оферта по перевозке корпоративных пользователей"', () => {
        LegalDocuments.navBar.items.corporate.click();
        expect(LegalDocuments.navBar.items.activeItem).toHaveTextEqual('Оферта по перевозке корпоративных пользователей');
        expect(browser).toHaveUrlContaining('/corporate');
    });

    it('открылось тело выбранного документа', () => {
        LegalDocuments.corporateText.waitForDisplayed({timeout: 30_000});
        expect(LegalDocuments.corporateText).toBeDisplayed();
    });

    it('в теле документа присутствует текст оферты', () => {
        expect(LegalDocuments.corporateText).toHaveElemLengthAbove(0);
    });

    it('в теле документа присутствует ссылка на корпоративную оферту', () => {
        expect(LegalDocuments.corporateLink).toHaveTextEqual('https://yandex.ru/legal/taxi_corporate_offer');
    });
});
