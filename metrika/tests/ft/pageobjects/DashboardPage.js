const Page = require('./Page.js');

const widgetTitle = '.dashboard-item__widgets .widget__title .widget-title__link';
const createWidget = '.dashboard-page__right-controls .dashboard-page__create-dropdown button';
const widgetLibrary = '.dashboard-page__right-controls .dashboard-page__wizard button';
const createWidgetList = '.dashboard-page__add-widget-menu';
const metricWidgetCreteBtn = '.popup2 .dashboard-page__add-widget-menu .menu__item:first-child';
const pieWidgetCreteBtn = '.popup2 .dashboard-page__add-widget-menu .menu__item:nth-child(2)';
const tableWidgetCreteBtn = '.popup2 .dashboard-page__add-widget-menu .menu__item:nth-child(3)';
const lineWidgetCreteBtn = '.popup2 .dashboard-page__add-widget-menu .menu__item:last-child';
const widgetLibraryCreateBtn = '.dashboard-wizard__add-panel .dashboard-wizard__add-button';
const widgetPopup = '.popup .widget__popup-content';
const widgetLibraryPopup = '.popup .dashboard-wizard__popup-content';
const widgetNameInput = '.widget__popup-content .widget__title-input input';
const widgetSettings = '.dashboard-item__widgets .widget .widget__edit';
const widgetSaveBtn = '.widget__popup-content .widget__save .widget__save-button'
const widgetRemoveBtn = '.widget__popup-content .widget__remove .widget__remove-button';
const restoreDefaultDashboard = '.dashboard-page__empty-dashboard .link .link__inner';

const widgetNameLength = 10;

class DashboardPage extends Page {
    async open(counterId) {
        await this.browser.url(`/dashboard?id=${counterId}`);
    }

    async createMetricWidget() {
        const widgetName = this.generateWidgetName();
        await this.browser.waitForVisible(createWidget)
            .click(createWidget)
            .waitForVisible(createWidgetList)
            .click(metricWidgetCreteBtn)
            .waitForVisible(widgetPopup)
            .element(widgetNameInput)
            .setValue(widgetName)
            .click(widgetSaveBtn)
            .pause(1000);
        return widgetName;

    }

    async createPieWidget() {
        const widgetName = this.generateWidgetName();
        await this.browser.waitForVisible(createWidget)
            .click(createWidget)
            .waitForVisible(createWidgetList)
            .click(pieWidgetCreteBtn)
            .waitForVisible(widgetPopup)
            .element(widgetNameInput)
            .setValue(widgetName)
            .click(widgetSaveBtn)
            .pause(1000);
        return widgetName;

    }

    async createTableWidget() {
        const widgetName = this.generateWidgetName();
        await this.browser.waitForVisible(createWidget)
            .click(createWidget)
            .waitForVisible(createWidgetList)
            .click(tableWidgetCreteBtn)
            .waitForVisible(widgetPopup)
            .element(widgetNameInput)
            .setValue(widgetName)
            .click(widgetSaveBtn)
            .pause(1000);
        return widgetName;

    }

    async createLineWidget() {
        const widgetName = this.generateWidgetName();
        await this.browser.waitForVisible(createWidget)
            .click(createWidget)
            .waitForVisible(createWidgetList)
            .click(lineWidgetCreteBtn)
            .waitForVisible(widgetPopup)
            .element(widgetNameInput)
            .setValue(widgetName)
            .click(widgetSaveBtn)
            .pause(1000);
        return widgetName;

    }

    async createWidgetFromLibrary() {
        const widgetName = this.generateWidgetName();
        await this.browser.waitForVisible(createWidget)
            .click(widgetLibrary)
            .waitForVisible(widgetLibraryPopup)
            .waitForVisible(widgetLibraryCreateBtn)
            .scroll(widgetLibraryCreateBtn)
            .click(widgetLibraryCreateBtn)
            .waitForVisible(widgetPopup)
            .element(widgetNameInput)
            .setValue(widgetName)
            .click(widgetSaveBtn)
            .pause(1000);
        return widgetName;
    }

    async deleteAllWidgets() {
        const widgets = await this.countWidgets();
        for (let i = 0; i < widgets; i++) {
            await this.openWidgetSetting();
            await this.deleteWidget();
        }
    }

    async restoreDashboard() {
        await this.browser.click(restoreDefaultDashboard)
            .pause(3000)
            .refresh();
    }

    async openWidgetSetting() {
        await this.browser.click(widgetSettings)
            .waitForVisible(widgetPopup);
    }

    async deleteWidget() {
        await this.browser.click(widgetRemoveBtn)
            .pause(1000);
    }

    async getAllWidgetsName() {
        let result = [];
        let elements = await this.browser.elements(widgetTitle);
        for (let i = 0; i < elements.value.length; i++) {
            let element = await this.browser.elementIdText(elements.value[i].ELEMENT);
            result.push(await element.value);
        }
        return result;
    }

    async countWidgets() {
        const widgets = await this.browser.waitForExist(widgetSettings).elements(widgetSettings);
        return widgets.value.length;
    }

    async isEmpty() {
        return await this.browser.isExisting(restoreDefaultDashboard);
    }

    //Вспомогательные методы
    generateWidgetName() {
        return `Виджет ${this.getRandomString(widgetNameLength)}`;
    }
}

module.exports = {
    DashboardPage,
};
