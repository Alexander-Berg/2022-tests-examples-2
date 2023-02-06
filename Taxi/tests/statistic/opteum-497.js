const Statistic = require('../../page/signalq/Statistic');

describe('SignalQ: статистика: фильтр событий: счётчик (декремент)', () => {

    it('Открыт раздел "Статистика"', () => {
        Statistic.goTo();
    });

    it('Предусловие', () => {
        Statistic.eventsFilterButton.click();

        Statistic.eventsFilterDropdownList.forEach(el => {
            el.click();
        });
    });

    it('Нажать каждое событие по очереди, счётчик в красном кружке уменьшается, на против нажатых пунктов пропадает галочка', () => {
        const count = Statistic.eventsFilterButton.getAttribute('data-count');

        Statistic.eventsFilterDropdownList.forEach((el, i) => {
            el.click();
            expect(Statistic.eventsFilterDropdownStatusList[i]).not.toHaveAttrContaining('class', 'CheckboxDropdown_checked__3QR1a');

            const currentCount = count - (i + 1);

            if (currentCount > 0) {
                expect(Statistic.eventsFilterButton).toHaveAttributeEqual('data-count', currentCount.toString());
            } else {
                expect(Statistic.eventsFilterButton).not.toHaveAttribute('data-count');
            }
        });
    });

});
