const OnlineCashbox = require('../../page/OnlineCashbox');
const {assert} = require('chai');

describe('Онлайн-кассы: добавление записи', () => {
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
        browser.pause(200);
    });

    it('Отобразился тост об успешном добавлении записи онлайн-кассы', () => {
        assert.equal(OnlineCashbox.alertText.getText(), 'Касса успешно создана');
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
    });
});
