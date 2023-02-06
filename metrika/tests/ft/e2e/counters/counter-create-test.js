'use strict'

const { assert } = require('chai');
const { simpleUser: user } = require('../../data/users');
const { Passport } = require('../../pageobjects/Passport.js');
const { CreateCounterPage } = require('../../pageobjects/CreateCounterPage');
const { EditCounterPage } = require('../../pageobjects/EditCounterPage');

beforeEach(function() {
    return new Passport(this.browser).login(user);
});

describe('Создание счетчика', function() {
    let page;
    let editPage;
    let counterId;

    beforeEach(async function() {
        editPage = new EditCounterPage(this.browser);

        page = new CreateCounterPage(this.browser);
        await page.open();
    });

    it('Код вставки на странице onboarding', async function() {
        counterId = await page.createCounter();
        assert.isTrue(await page.isCodePreviewAllow(), 'код вставки доступен после создания счетчика');
    });

    afterEach(async function() {
        await editPage.deleteCounter(counterId);
    });
});
