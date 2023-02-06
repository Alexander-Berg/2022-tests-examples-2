const Statistic = require('../../page/signalq/Statistic');

describe('SignalQ: статистика: фильтр событий: счётчик (инкремент)', () => {

    it('Открыт раздел "Статистика"', () => {
        Statistic.goTo();
    });

    it('Нажать на "фильтр событий" в виджете графика', () => {
        Statistic.eventsFilterButton.click();
    });

    it('Нажать каждое событие по очереди, счётчик в красном кружке увеличивается, напротив нажатых пунктов появляется галочка', () => {
        Statistic.eventsFilterDropdownList.forEach((el, i) => {
            el.click();
            expect(Statistic.eventsFilterDropdownStatusList[i]).toHaveAttrContaining('class', 'CheckboxDropdown_checked__3QR1a');
            expect(Statistic.eventsFilterButton).toHaveAttributeEqual('data-count', (i + 1).toString());
        });
    });

});
