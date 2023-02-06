'use strict'

const { assert } = require('chai');
const { parse } = require('url');
const { PromoPage } = require('../pageobjects/PromoPage');
const { demoCounter: demoCounter } = require('../data/counters');

describe('Старая промо-страница', function() {
    let page;

    beforeEach(async function() {
        page = new PromoPage(this.browser);
    });

    it('Открывается промка для неавторизованного пользователя', async function() {
        await page.openMainUrl();
        const currentUrl = await page.getUrl();

        assert.equal(parse(currentUrl).pathname, '/promo', 'url совпадает с ожидаемым');
    });

    it('Демо-счетчик доступен для неавторизованного пользователя', async function() {
        await page.open();
        await page.openDemoCounter();
        const currentUrl = await page.getUrl();

        assert.equal(parse(currentUrl).path, `/dashboard?id=${demoCounter.id}`, 'url совпадает с ожидаемым');
    });

    it('Открывается страница авторизации при переходе на список счетчиков для неавторизованного пользователя', async function() {
        const encodedUri = encodeURIComponent(`${hermione.ctx.baseUrl}/list`);

        await page.open();
        await page.clickStartUsing();

        const currentUrl = await page.getUrl();

        assert.equal(
            currentUrl,
            `https://passport.yandex.ru/auth?origin=metrica&retpath=${encodedUri}`,
            'url совпадает с ожидаемым'
        );
    });
});
