'use strict'

const { assert } = require('chai');
const { parse } = require('url');
const { Passport } = require('../../pageobjects/Passport.js');
const { CounterListPage } = require('../../pageobjects/CounterListPage');
const { simpleUser: user } = require('../../data/users');

beforeEach(function() {
    return new Passport(this.browser).login(user);
});

describe('Список счетчиков', function() {
    let page;

    beforeEach(async function() {
        page = new CounterListPage(this.browser);
    });

    it('Редирект на список счетчиков для авторизованного пользователя', async function() {
        await page.openMainUrl();

        const currentUrl = await page.getUrl();

        assert.equal(parse(currentUrl).pathname, '/list', 'url совпадает с ожидаемым');
    });

    it('Кнопка добавления счетчика работает', async function() {
        await page.open();
        await page.openAddCounter();

        const currentUrl = await page.getUrl();

        assert.equal(parse(currentUrl).pathname, '/add', 'url совпадает с ожидаемым');
    });
});
