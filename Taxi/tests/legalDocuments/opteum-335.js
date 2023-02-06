const LegalDocuments = require('../../page/LegalDocuments.js');

const DATA = {
    name: 'Маркетинговые условия',
    path: '/marketing',
    pdf: 'https://s3.mdst.yandex.net/dynamic-documents/5ca24245-01c0-493f-b304-730930da6491.pdf',
};

describe(`Открытие оферты "${DATA.name}"`, () => {

    it('Открыть раздел "Правовые документы"', () => {
        LegalDocuments.goTo();
    });

    it(`Выбрать "${DATA.name}"`, () => {
        LegalDocuments.navBar.items.marketingConditions.click();
        expect(LegalDocuments.navBar.items.activeItem).toHaveTextEqual(DATA.name);
    });

    it(`Открылась страница "${DATA.path}"`, () => {
        expect(browser).toHaveUrlContaining(DATA.path);
    });

    it('Открылся корректный PDF-документ', () => {
        expect(LegalDocuments.pdf.content).toHaveAttributeEqual('data', DATA.pdf);
    });

});
