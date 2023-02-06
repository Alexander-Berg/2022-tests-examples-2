module.exports = {
    discountName: '[name="sharedModel.discountName"]',
    discountPercentMoney: '[name="sharedModel.paymentRules.rules[0].moneyValue.value"]',
    discountPercentCashback: '[name="sharedModel.paymentRules.rules[0].cashbackValue.value"]',
    ticket: '[name="sharedModel.metaInfo.ticket"]',
    zone: '//div[contains(text(), "Имя зоны")]/following::div[1]//input',
    zoneCurrent: '//li[@title="br_belarus/br_minsk/minsk"]',
    submit: '//span[text()="Отдать на проверку"]',
    prioritySpecific: '//span[text()="Конкретные совокупности меток"]/../..',
    priorityForAll: '//*[text()="Во всех совокупностях меток, кроме"]',
    prioritized: '//input[@name="sharedModel.activePeriod.updateExistingDiscounts"]/..',
    classOfDiscounts: '//div[contains(text(), "Имя класса")]/following::div[1]//input',
    acceptButton: '//span[text() = "Подтвердить"]',
    successLabel: '//span[text()="Выполнен успешно"]',
    notification: '//div[text() = "Draft approved"]',

    async openTaxiDiscount(type) {
        await browser.url(
            `/ride-discounts/discounts?hierarchyName=${type}&__timestamp=1654509924718&formType=createView&mode=create`
        );
    }
};
