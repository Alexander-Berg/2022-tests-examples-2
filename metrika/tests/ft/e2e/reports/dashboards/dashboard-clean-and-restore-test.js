'use strict'

const {assert} = require('chai');
const {simpleUser: user} = require('../../../data/users');
const {Passport} = require('../../../pageobjects/Passport.js');
const {DashboardPage} = require('../../../pageobjects/DashboardPage');
const {CreateCounterPage} = require('../../../pageobjects/CreateCounterPage');
const {EditCounterPage} = require('../../../pageobjects/EditCounterPage');

beforeEach(function () {
    return new Passport(this.browser).login(user);
});

describe('Восстановление дашборда', function () {
    let page;
    let settingsPage;
    let counterId;

    beforeEach(async function () {
        const createPage = new CreateCounterPage(this.browser);
        await createPage.open();
        counterId = await createPage.createCounter();
        settingsPage = await new EditCounterPage(this.browser);

        page = await new DashboardPage(this.browser);
        await page.open(counterId);
    });

    it('Удаление всех виджетов с дашборда', async function () {
        await page.deleteAllWidgets();
        const isEmpty = await page.isEmpty();
        assert.isTrue(isEmpty, 'все виджеты удалены')
    });

    it('Восстановление стандартного набора виджетов', async function () {
        await page.deleteAllWidgets();
        await page.restoreDashboard();
        const widgets = await page.countWidgets();
        assert.equal(widgets, 10, 'виджеты восстановлены');

    });

    afterEach(async function () {
        await settingsPage.open(counterId)
        await settingsPage.deleteCounter(counterId);
    });
});
