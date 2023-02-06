const {type, waitExistSelectorAndReload} = require('../../support/helpers');
const dayjs = require('dayjs');
let currentDate = dayjs();

module.exports = {
    create: '.SmartSubventionsPage__plusButton',
    subventionType: '//input[@name="SUBVENTION_MODEL.rule_type"]/..',
    subventionTypeOnTop: '[aria-label="single_ontop"]',
    zone: '//div[contains(text(), "Тарифная зона")]/following::div[1]//input',
    orderServiceClass: '//div[contains(text(), "Тариф заказа")]/following::div[1]//input',
    total: '[name="SUBVENTION_MODEL.budget.daily"]',
    startTime: '[name="SUBVENTION_MODEL.start.time"]',
    startDate: '[name="SUBVENTION_MODEL.start.date"]',
    endTime: '[name="SUBVENTION_MODEL.end.time"]',
    endDate: '[name="SUBVENTION_MODEL.end.date"]',
    listStartTime: '[name="SUBVENTION_MODEL.rates[0].start"]',
    listEndTime: '[name="SUBVENTION_MODEL.rates[0].end"]',
    listStartDay: '(//button[contains(@class, "SmartSubventionsForm__dateButton")])[1]',
    dayOfWeekStart: '//div[text() = "Понедельник"]',
    dayOfWeekEnd: '//div[text() = "Вторник"]',
    listEndDay: '(//button[contains(@class, "SmartSubventionsForm__dateButton")])[2]',
    bonus: '[name="SUBVENTION_MODEL.rates[0].bonus_amount"]',
    ticket: '[name="SUBVENTION_MODEL.ticketData.ticket"]',
    submit: '//span[text()="Отдать на проверку"]',
    budget: '[name="SUBVENTION_MODEL.budget.subgmv"]',
    acceptButton: '//span[text() = "Подтвердить"]',
    closeButton: '//span[text() = "Закрыть"]',
    notification: '//div[text() = "Draft approved"]',
    errorConflict: '//h2[text() = "Error sending request"]',
    subventionTypeGoal: '[aria-label="goal"]',
    geoHierarchyNode: '.EfficiencyBlocksTreeSelect__control',
    geoHierarchy: '//div[text() = "Узел геоиерархии"]',
    geo: '//div[text() = "boryasvo"]',
    windowSize: '[name="SUBVENTION_MODEL.window"]',
    numberOfRides: '[name="SUBVENTION_MODEL.counters.steps[0].steps[0].nrides"]',
    amountShown: '[name="SUBVENTION_MODEL.counters.steps[0].steps[0].amount"]',
    selectCounter:
        '.SmartSubventionsSingleRideFormFormContentSchedule__intervalInputs .amber-select',
    selectMenuOuter: '//*[@class="Select-menu-outer"]//div[text()="A"]',
    completeGoal: '//span[text()="Завершить цель"]',
    closeDate: '[name="BULK_MODEL.draft.data.closeAt.date"]',
    bulkTicket: '[name="BULK_MODEL.draft.data.ticketData.ticket"]',
    successLabel: '//span[text()="Выполнен успешно"]',
    sidePanelHeaderTitle: '//h2[text() = "Драфт закрытия правил"]',
    async openSub() {
        await browser.url(
            `https://tariff-editor.taxi.tst.yandex-team.ru/smart-subventions/create-draft`
        );
    },
    async fillSubventionsForm() {
        await browser.$(this.zone).setValue('boryasvo');
        await browser.keys('Enter');
        await browser.$(this.orderServiceClass).setValue('Comfort');
        await browser.keys('Enter');
        await browser.$(this.budget).setValue('1');
        await browser.$(this.total).scrollIntoView();
        await browser.$(this.total).setValue('10');
        /*поля заполняются в порядке: дата конца, дата старта, время старта,
           время окончания для того, чтобы дата не подставлялась автоматически*/
        await browser.$(this.endDate).setValue(currentDate.format('DD.MM.YYYY'));
        await browser.keys('Enter');
        await browser.$(this.startDate).setValue(currentDate.format('DD.MM.YYYY'));
        await browser.keys('Enter');
        await browser.$(this.startTime).click();
        await browser.$(this.startTime).clearValue();
        await type(this.startTime, currentDate.add('2', 'minute').format('HH:mm'));
        await browser.keys('Enter');
        await browser.$(this.endTime).click();
        await browser.$(this.endTime).clearValue();
        await type(this.endTime, currentDate.add('3', 'minute').format('HH:mm'));
        await browser.keys('Enter');
        await browser.$(this.listStartDay).click();
        await browser.$(this.dayOfWeekStart).click();
        await type(this.listStartTime, '12:33');
        await browser.$(this.listEndDay).click();
        await browser.$(this.dayOfWeekEnd).click();
        await type(this.listEndTime, '12:33');
        await browser.$(this.bonus).setValue('100');
        await browser.$(this.ticket).setValue('TAXIRATE-91');
        await waitExistSelectorAndReload(15000, this.submit);
        await browser.$(this.submit).click();
        await browser.$(this.acceptButton).click();
        await browser.$(this.notification).isExisting();
        await waitExistSelectorAndReload(21000, this.successLabel);
    }
};
