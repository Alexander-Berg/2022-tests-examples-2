const OnlineCashbox = require('../../page/OnlineCashbox');
const {assert} = require('chai');

describe('Онлайн-кассы: Выключение', () => {
    let newCashboxPosition;
    const allId = [];

    it('Открыть страницу онлайн-касс', () => {
        OnlineCashbox.goTo();
    });

    it('Сохранить список текущих касс', () => {
        OnlineCashbox.getAllRows.id.forEach(el => {
            allId.push(el.getText());
        });
    });

    it('Создать новую кассу', () => {
        OnlineCashbox.createNewCashbox();
    });

    it('Найти новую кассу', () => {
        newCashboxPosition = OnlineCashbox.getNewCashboxPosition(allId);
    });

    it('Активировать кассу', () => {
        OnlineCashbox.getRow(newCashboxPosition).id.moveTo();
        OnlineCashbox.activateButton.waitForDisplayed();
        OnlineCashbox.activateButton.click();
        OnlineCashbox.getRow(newCashboxPosition).active.waitForDisplayed();
        assert.isTrue(OnlineCashbox.getRow(newCashboxPosition).active.isDisplayed());
    });

    it('Навестись на кассу', () => {
        OnlineCashbox.getRow(newCashboxPosition).id.moveTo();
    });

    it('Выключить кассу', () => {
        OnlineCashbox.deactivateButton.click();
        browser.pause(500);
        assert.isFalse(OnlineCashbox.getRow(newCashboxPosition).active.isDisplayed());
    });

    it('Удалить созданную кассу', () => {
        OnlineCashbox.getRow(newCashboxPosition).id.moveTo();
        OnlineCashbox.deleteButton.waitForDisplayed();
        OnlineCashbox.deleteButton.click();
    });

    it('Активировать другую кассу', () => {
        OnlineCashbox.getRow().id.moveTo();
        OnlineCashbox.activateButton.waitForDisplayed();
        OnlineCashbox.activateButton.click();
    });
});
