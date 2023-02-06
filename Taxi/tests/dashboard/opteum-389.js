const DashboardPage = require('../../page/DashboardPage');
const timeouts = require('../../../../utils/consts/timeouts');

describe('Сводка: логирование: ссылки', () => {

    const DATA = {
        links: [
            ['action', 'certification_quality_link_clicked'],
            ['action', 'certification_summary_park_link_clicked'],
            ['action', 'certification_summary_drivers_link_clicked'],
        ],
    };

    const metricsPostData = [];

    it('Открыть страницу сводки', () => {
        DashboardPage.goTo();
    });

    it('Запустить перехват запросов метрики', () => {
        DashboardPage.saveMetricsToArray(metricsPostData);
    });

    DATA.links.forEach((mc, i) => {
        describe(mc.join('='), () => {

            it('Нажать на ссылку в дашборде сертификации', () => {
                DashboardPage.certificationDash.links[i].click();
            });

            it('Запросы метрики перехватились', () => {
                browser.pause(timeouts.intercept);
                expect(metricsPostData.length).toBeGreaterThan(0);
            });

            it('Запрос содержит корректный параметр', () => {
                expect(metricsPostData.pop()).toHaveProperty(...mc);
            });

        });
    });
});
