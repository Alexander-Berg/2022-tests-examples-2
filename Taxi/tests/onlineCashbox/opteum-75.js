const OnlineCashbox = require('../../page/OnlineCashbox');
const {assert} = require('chai');

describe('Онлайн-кассы: активация', () => {
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

    it('Навестись на кассу', () => {
        OnlineCashbox.getRow(newCashboxPosition).id.scrollIntoView({block: 'center'});
        OnlineCashbox.getRow(newCashboxPosition).id.moveTo();
        browser.pause(500);
    });

    it('Нажать кнопку активировать', () => {
        OnlineCashbox.activateButton.click();
        OnlineCashbox.getRow(newCashboxPosition).active.waitForDisplayed();
        assert.isTrue(OnlineCashbox.getRow(newCashboxPosition).active.isDisplayed());
    });

    it('Выбрать активной другую запись онлайн-кассы', () => {
        const anotherCashboxPosition = newCashboxPosition === 1
            ? newCashboxPosition + 1
            : newCashboxPosition - 1;

        OnlineCashbox.getRow(anotherCashboxPosition).id.moveTo();
        OnlineCashbox.activateButton.waitForDisplayed();
        OnlineCashbox.activateButton.click();
        OnlineCashbox.getRow(anotherCashboxPosition).active.waitForDisplayed();
        assert.isTrue(OnlineCashbox.getRow(anotherCashboxPosition).active.isDisplayed());
        assert.isFalse(OnlineCashbox.getRow(newCashboxPosition).active.isDisplayed());
    });

    it('Удалить созданную кассу', () => {
        OnlineCashbox.getRow(newCashboxPosition).id.moveTo();
        OnlineCashbox.deleteButton.waitForDisplayed();
        OnlineCashbox.deleteButton.click();
    });
});
