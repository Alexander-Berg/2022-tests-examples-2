const LegalDocuments = require('../../page/LegalDocuments.js');

const DATA = {
    name: 'Общие условия',
    path: '/general',
    pdf: 'https://s3.mdst.yandex.net/dynamic-documents/5f4e15859519e9b7a8eda215.pdf',
};

describe(`Открытие оферты "${DATA.name}"`, () => {

    it('Открыть раздел "Правовые документы"', () => {
        LegalDocuments.goTo();
    });

    it(`Выбрать "${DATA.name}"`, () => {
        LegalDocuments.navBar.items.general.click();
        expect(LegalDocuments.navBar.items.activeItem).toHaveTextEqual(DATA.name);
    });

    it(`Открылась страница "${DATA.path}"`, () => {
        expect(browser).toHaveUrlContaining(DATA.path);
    });

    it('Открылся корректный PDF-документ', () => {
        expect(LegalDocuments.pdf.content).toHaveAttributeEqual('data', DATA.pdf);
    });

});
