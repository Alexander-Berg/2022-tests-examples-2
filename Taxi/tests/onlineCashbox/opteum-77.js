const OnlineCashbox = require('../../page/OnlineCashbox');
const {assert} = require('chai');

describe('Онлайн-кассы: Удаление записи', () => {
    let newCashboxId,
        newCashboxPosition;

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
        browser.pause(200);
    });

    it('Найти новую кассу', () => {
        newCashboxPosition = OnlineCashbox.getNewCashboxPosition(allId);
    });

    it('Навестись на кассу', () => {
        OnlineCashbox.getRow(newCashboxPosition).id.moveTo();
        OnlineCashbox.deleteButton.waitForDisplayed();
    });

    it('Нажать кнопку удалить', () => {
        OnlineCashbox.deleteButton.click();
        browser.pause(200);

        for (let i = 0; i < OnlineCashbox.getAllRows.id.length; i++) {
            assert.notEqual(OnlineCashbox.getAllRows.id[i].getText(), newCashboxId);
        }
    });
});
