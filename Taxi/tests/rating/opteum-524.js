const Rating = require('../../page/Rating');

describe('Рейтинг: заглушка "Нет данных" если города парка нет в агломерации', () => {

    const DATA = {
        notFound: 'Нет данных',
    };

    it('Открыть раздел рейтинга', () => {
        Rating.goTo();
    });

    it('Отобразилась заглушка', () => {
        expect(Rating.reportTable.notFound).toHaveTextEqual(DATA.notFound);
    });

});
