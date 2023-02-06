const NewsPage = require('../../page/NewsPage');

describe('Открытие просмотренной новости', () => {

    const DATA = {
        header: 'Новости',
    };

    it('Открыть страницу новостей', () => {
        NewsPage.goTo();
    });

    it('Отображается заголовок блока', () => {
        expect(NewsPage.list.header).toHaveTextEqual(DATA.header);
    });

    it('Отображается список новостей', () => {
        expect(NewsPage.list.items).toHaveElemLengthAbove(0);
    });

    it('У новостей корректный текст', () => {
        expect(NewsPage.list.items).toHaveTextOk();
    });

    it('Отображаются отметки непросмотренных новости', () => {
        expect(NewsPage.list.marks).toHaveElemLengthAbove(0);
    });

    it('Открыть первую новость', () => {
        NewsPage.list.items[0].click();
    });

    it('Отображается корректный текст новости', () => {
        expect(NewsPage.body).toHaveTextOk();
    });

});
