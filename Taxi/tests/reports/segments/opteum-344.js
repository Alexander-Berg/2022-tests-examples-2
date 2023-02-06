const AutoCard = require('../../../page/AutoCard');
const ReportsSegments = require('../../../page/ReportsSegments');

describe('Открытие карточки авто из сегментов водителей', () => {

    let sign;

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it('Сохранить позывной первого водителя из списка', () => {
        sign = ReportsSegments.getCells({tr: 1, td: 2}).getText();
    });

    it('Нажать на позывной', () => {
        ReportsSegments.getCells({tr: 1, td: 2}).click();
    });

    it('Открылась страница авто', () => {
        expect(browser).toHaveUrlContaining(`${AutoCard.baseUrl}/vehicles`);
    });

    it('В карточке авто отображается корректный позывной', () => {
        expect(AutoCard.parametersBlock.sign).toHaveAttributeEqual('value', sign);
    });

});
