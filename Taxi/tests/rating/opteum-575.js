const moment = require('moment');
const Rating = require('../../page/Rating');

moment.locale('ru');

describe('Рейтинг: просмотр предыдущего месяца', () => {

    const DATA = {
        months: {
            current: Rating.defaultDate.text,
            previous: moment(Rating.defaultDate.text, Rating.defaultDate.mask)
                .add(-1, 'months')
                .format(Rating.defaultDate.mask),
        },
    };

    it('Открыть раздел рейтинга', () => {
        Rating.goToWithRating();
    });

    it('Открылся корректный месяц', () => {
        expect(Rating.filters.month.title).toHaveTextEqual(DATA.months.current);
    });

    it('Отображается селектор выбора предыдущего месяца', () => {
        expect(Rating.filters.month.buttons.arrows.left).toHaveElemVisible();
    });

    it('Нажать на селектор выбора предыдущего месяца', () => {
        Rating.filters.month.buttons.arrows.left.click();
    });

    it('Открылся предыдущий месяц', () => {
        expect(Rating.filters.month.title).toHaveTextEqual(DATA.months.previous);
    });

});
