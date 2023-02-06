import { passportLogin } from 'utils/passport-login';
import { takeScreenshot } from 'utils/take-screenshot';

beforeEach(passportLogin);

describe('Графики', function() {
    ;[
        '/stat/traffic?group=minute&period=2015-12-01%3A2015-12-01&accuracy=1&id=8535712&ulogin=shop-kika&lang=ru',
        '/stat/traffic?group=dekaminute&period=2015-12-01%3A2015-12-01&accuracy=1&id=8535712&ulogin=shop-kika&lang=ru',
        '/stat/traffic?group=hour&period=2015-12-01%3A2015-12-01&accuracy=1&id=8535712&ulogin=shop-kika&lang=ru',
        '/stat/traffic?group=day&period=2015-12-01%3A2015-12-31&accuracy=1&id=8535712&ulogin=shop-kika&lang=ru',
        '/stat/traffic?group=week&period=2015-12-01%3A2015-12-31&accuracy=1&id=8535712&ulogin=shop-kika&lang=ru',
        '/stat/traffic?group=month&period=2015-12-01%3A2016-01-31&accuracy=1&id=8535712&ulogin=shop-kika&lang=ru',
    ].forEach((url, index) => {
        it(`График посещаемости ${index}`, async function() {
            await takeScreenshot.bind(this)(
                url,
                '.chart__chart',
                `traffic-chart-${index}`,
            );
        });
    });

    it('Пай', async function() {
        await takeScreenshot.bind(this)(
            '/stat/sources?period=2015-12-01%3A2015-12-31&chart_type=pie&accuracy=1&ulogin=shop-kika&id=8535712&lang=ru',
            '.chart__chart',
            'pie-chart',
        );
    });

    it('Линии', async function() {
        await takeScreenshot.bind(this)(
            '/stat/titles?period=2015-12-01%3A2015-12-31&chart_type=line-chart&ulogin=shop-kika&id=8535712&lang=ru',
            '.chart__chart',
            'line-chart',
        );
    });

    it('Области', async function() {
        await takeScreenshot.bind(this)(
            '/stat/browsers?period=2015-12-01%3A2015-12-31&chart_type=stacked-chart&region=tr&accuracy=1&ulogin=shop-kika&id=8535712&lang=ru',
            '.chart__chart',
            'stacked-chart',
        );
    });

    it('Колонки', async function() {
        await takeScreenshot.bind(this)(
            '/stat/hourly?period=2015-12-01%3A2015-12-31&chart_type=bar-chart&accuracy=1&ulogin=shop-kika&id=8535712&lang=ru',
            '.chart__chart',
            'bar-chart',
        );
    });

    ;[
        '/stat/geo?period=2015-12-01%3A2015-12-31&accuracy=1&ulogin=shop-kika&id=8535712&lang=ru',
        '/stat/geo?period=2015-12-01%3A2015-12-31&region=ru&accuracy=1&ulogin=shop-kika&id=8535712&lang=ru',
        '/stat/geo?period=2015-12-01%3A2015-12-31&region=ua&accuracy=1&ulogin=shop-kika&id=8535712&lang=ru',
        '/stat/geo?period=2015-12-01%3A2015-12-31&region=by&accuracy=1&ulogin=shop-kika&id=8535712&lang=ru ',
        '/stat/geo?period=2015-12-01%3A2015-12-31&region=tr&accuracy=1&ulogin=shop-kika&id=8535712&lang=ru',
    ].forEach((url, index) => {
        it(`Карта ${index}`, async function() {
            await takeScreenshot.bind(this)(
                url,
                '.chart__mapdiv',
                `geo-chart-${index}`,
            );
        });
    });

    ;[
        '/stat/expenses?goal=89084383&metric=ym%3Aev%3Agoal%3Cgoal_id%3Eexpense%3Ccurrency%3EROI&sort=-ym%3Aev%3Agoal%3Cgoal_id%3Eexpense%3Ccurrency%3EROI&period=2020-02-01%3A2020-02-29&accuracy=1&id=59207371',
        '/stat/expenses?goal=89084383&metric=ym%3Aev%3Agoal%3Cgoal_id%3Eexpense%3Ccurrency%3EROI&sort=-ym%3Aev%3Agoal%3Cgoal_id%3Eexpense%3Ccurrency%3EROI&group=day&chart_type=bar-chart&period=2020-02-01%3A2020-02-02&accuracy=1&id=59207371',
    ].forEach((url, index) => {
        it(`Отрицательный график ${index}`, async function() {
            await this.browser.url(url);
            await this.browser.localStorage('POST', {key: 'onboarding-expenses.hidden', value: '1'});
            await this.browser.localStorage('POST', {key: 'viewed_roi_report', value: '1'});

            await takeScreenshot.bind(this)(
                url,
                '.chart__chart',
                `negative-chart-${index}`,
            );
        });
    });
});
