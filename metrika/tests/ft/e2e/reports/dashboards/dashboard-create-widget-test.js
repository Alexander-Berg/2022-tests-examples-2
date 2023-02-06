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

describe('Создание виджета', function () {
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

    describe('Создание стандартных виджетов', function () {

        it('Создание виджета "Линии"', async function () {
            const widgetName = await page.createLineWidget();
            const allWidgetsName = await page.getAllWidgetsName();

            assert.include(allWidgetsName, widgetName, 'виджет присутствует на дашборде');
        });

        it('Создание виджета "Таблица"', async function () {
            const widgetName = await page.createTableWidget();
            const allWidgetsName = await page.getAllWidgetsName();

            assert.include(allWidgetsName, widgetName, 'виджет присутствует на дашборде');
        });

        it('Создание виджета "Круговая диаграмма"', async function () {
            const widgetName = await page.createPieWidget();
            const allWidgetsName = await page.getAllWidgetsName();

            assert.include(allWidgetsName, widgetName, 'виджет присутствует на дашборде');
        });

        it('Создание виджета "Показатель"', async function () {
            const widgetName = await page.createMetricWidget();
            const allWidgetsName = await page.getAllWidgetsName();

            assert.include(allWidgetsName, widgetName, 'виджет присутствует на дашборде');
        });
    });

    describe('Создание виджета из библиотеки', function () {

        it('Создание виджета из библиотеки виджетов', async function () {
            const widgetName = await page.createWidgetFromLibrary();
            const allWidgetsName = await page.getAllWidgetsName();

            assert.include(allWidgetsName, widgetName, 'виджет присутствует на дашборде');
        });
    });

    afterEach(async function () {
        await settingsPage.open(counterId)
        await settingsPage.deleteCounter(counterId);
    });
});
