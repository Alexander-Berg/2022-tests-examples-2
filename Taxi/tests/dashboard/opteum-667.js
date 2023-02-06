const DashboardPage = require('../../page/DashboardPage');
const timeouts = require('../../../../utils/consts/timeouts');

describe('Сводка: логирование: фильтры', () => {

    const DATA = {
        filters: [
            ['params.value', 'yesterday'],
            ['params.value', 'week'],
            ['params.value', 'month'],
            ['params.value', 'period'],
        ],
        default: ['action', 'date_filter_changed'],
    };

    const metricsPostData = [];

    it('Открыть страницу сводки', () => {
        DashboardPage.goTo();
    });

    it('Запустить перехват запросов метрики', () => {
        DashboardPage.saveMetricsToArray(metricsPostData);
    });

    DATA.filters.forEach((mc, i) => {
        describe(mc.join('='), () => {

            it('Выбрать фильтр периода', () => {
                DashboardPage.filter.buttons[i + 1].click();
            });

            it('Запросы метрики перехватились', () => {
                browser.pause(timeouts.intercept);
                expect(metricsPostData.length).toBeGreaterThan(0);
            });

            it('Запрос содержит корректные параметры', () => {
                const lastElem = metricsPostData.pop();

                expect(lastElem).toHaveProperty(...DATA.default);
                expect(lastElem).toHaveProperty(...mc);
            });

        });
    });
});
