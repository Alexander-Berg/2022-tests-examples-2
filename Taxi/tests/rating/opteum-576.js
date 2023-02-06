const moment = require('moment');
const Rating = require('../../page/Rating');

moment.locale('ru');

describe('Рейтинг: просмотр следующего месяца', () => {

    const DATA = {
        months: {
            current: Rating.defaultDate.text,
            next: moment(Rating.defaultDate.text, Rating.defaultDate.mask)
                .add(1, 'months')
                .format(Rating.defaultDate.mask),
        },
    };

    it('Открыть раздел рейтинга', () => {
        Rating.goToWithRating();
    });

    it('Открылся корректный месяц', () => {
        expect(Rating.filters.month.title).toHaveTextEqual(DATA.months.current);
    });

    it('Отображается селектор выбора следующего месяца', () => {
        expect(Rating.filters.month.buttons.arrows.right).toHaveElemVisible();
    });

    it('Нажать на селектор выбора следующего месяца', () => {
        Rating.filters.month.buttons.arrows.right.click();
    });

    it('Открылся следующий месяц', () => {
        expect(Rating.filters.month.title).toHaveTextEqual(DATA.months.next);
    });

});
