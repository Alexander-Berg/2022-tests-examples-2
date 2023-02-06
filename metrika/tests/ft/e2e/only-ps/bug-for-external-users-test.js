'use strict'

const {assert} = require('chai');
const {Passport} = require('../../pageobjects/Passport.js');
const {PromoPage} = require('../../pageobjects/PromoPage');
const {simpleUser: user} = require('../../data/users');
const {goalCreateTestCounter: counter} = require('../../data/counters');

//Константы урлов
const promoUrl = '/promo';
const counterListUrl = '/list?';
const counterSettingUrl = `/settings?id=${counter.id}`;
const simpleCounterUrl = `/dashboard?id=${counter.id}`
const publicCounterUrl = '/dashboard?id=907917';


describe('"Жучок" для внешних пользователей', function () {
    let page;

    beforeEach(function () {
        page = new PromoPage(this.browser);
    });

    describe('Анонимы', function () {
        const pagesForAnonim = [
            {
                description: 'промо страница',
                page: promoUrl
            },
            {
                description: 'публичный счетчика',
                page: publicCounterUrl
            }
        ];

        pagesForAnonim.forEach(function (metrikaPage) {
            it(`"Жучок" скрыт для авторизованных пользователей: ${metrikaPage.description}`, async function () {
                await page.openUrl(metrikaPage.page);

                assert.isFalse(await page.isBugVisible(), 'жучок не доступен');
            });
        });
    });

    describe('Авторизованные пользователи', function () {
        beforeEach(function () {
            return new Passport(this.browser).login(user);
        });

        const pagesForUser = [
            {
                description: 'промо страница',
                page: promoUrl
            },
            {
                description: 'список счетчиков',
                page: counterListUrl
            },
            {
                description: 'настройки счетчика',
                page: counterSettingUrl
            },
            {
                description: 'отчет',
                page: simpleCounterUrl
            },
        ];

        pagesForUser.forEach(function (metrikaPage) {
            it(`"Жучок" скрыт для авторизованных пользователей: ${metrikaPage.description}`, async function () {
                await page.openUrl(metrikaPage.page);

                assert.isFalse(await page.isBugVisible(), 'жучок не доступен');
            });
        })
    });
});
