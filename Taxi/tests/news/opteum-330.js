const NewsPage = require('../../page/NewsPage');

describe('Открытие новой новости (подсвечена)', () => {

    const DATA = {
        path: '/api/v1/feeds/list/by-id',
        status: 'read',
    };

    let request;

    it('Открыть страницу новостей', () => {
        NewsPage.goTo();
    });

    it('Отображаются отметки непросмотренных новости', () => {
        expect(NewsPage.list.marks).toHaveElemLengthAbove(0);
    });

    it('Включить перехват запросов', () => {
        browser.setupInterceptor();
    });

    it('Открыть последнюю новость', () => {
        NewsPage.list.items.pop().click();
    });

    it(`Отправился запрос "${DATA.path}"`, () => {
        const requests = browser.getRequests();

        request = requests.find(({url}) => url.includes(DATA.path));
        expect(request).toBeTruthy();
    });

    // в тесте пока не можем генерить свежие новости, чтобы проверять отметки
    // но можем проверить, что в ручке присутствует статус, по которой рисуется эта отметка
    it(`В запросе есть статус новости "${DATA.status}"`, () => {
        expect(request.response?.body?.feeds?.pop()?.last_status?.status).toEqual('read');
    });

});
