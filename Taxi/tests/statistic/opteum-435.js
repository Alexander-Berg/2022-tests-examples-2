const Statistic = require('../../page/signalq/Statistic');

describe('SignalQ. Статистика. Фильтрация по группе (негатив)', () => {
    const group = 'empty';

    it('Открыт раздел "Статистика"', () => {
        Statistic.goToWithDate();
    });

    it('В селекторе группы выбрать группу без данных', () => {
        Statistic.groupFilter.click();
        Statistic.groupFilterInput.addValue(group);
        browser.keys('Enter');
    });

    it('нет никаких данных', () => {
        expect(Statistic.critEventsSummary).toHaveTextEqual('0');
        expect(Statistic.critEventsSummaryPercent).toHaveTextEqual('–');
        expect(Statistic.notCritEvents).toHaveTextEqual('0');
        expect(Statistic.notCritEventsPercent).toHaveTextEqual('–');
        expect(Statistic.critEventsNoData).toHaveTextEqual('Нет данных');
        expect(Statistic.camerasOnline).not.toExist();
        expect(Statistic.cameraMalfunctionsNoData).toHaveTextEqual('Нет данных');
        expect(Statistic.graphEventsCounter).toHaveTextEqual('0 событий');
        expect(Statistic.ratingPlaceholder).toExist();
    });

});
