const Agent = require('../../page/Agent.js');

describe('Агент: Показать скрытое поле', () => {

    it('Открыть главную', () => {
        Agent.goTo();
    });

    it('Нажать на засекреченное поле у первого водителя', () => {
        Agent.getRow().phone.click();
    });

    it('Вместо звёздочек появился телефон', () => {
        expect(Agent.getRow().phone).not.toHaveText('﹡﹡﹡﹡﹡');
    });
});
