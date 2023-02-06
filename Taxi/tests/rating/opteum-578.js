const moment = require('moment');
const Rating = require('../../page/Rating');

moment.locale('ru');

describe('Рейтинг: переключение на текущий месяц', () => {

    const DATA = {
        todayButton: 'Сегодня',
        months: {
            current: Rating.defaultDate.text,
            today: moment().format(Rating.defaultDate.mask),
        },
    };

    let currentMonthText;

    it('Открыть раздел рейтинга', () => {
        Rating.goToWithRating();
    });

    it('Открылся корректный месяц', () => {
        currentMonthText = Rating.filters.month.title.getText();
        expect(Rating.filters.month.title).toHaveTextEqual(DATA.months.current);
    });

    it('Отображается кнопка выбора текущего месяца', () => {
        expect(Rating.filters.month.buttons.today).toHaveTextEqual(DATA.todayButton);
    });

    it('Нажать на кнопку выбора текущего месяца', () => {
        Rating.filters.month.buttons.today.click();
    });

    it('Текст месяца сменился', () => {
        expect(Rating.filters.month.title).not.toHaveTextEqual('');
        expect(Rating.filters.month.title).not.toHaveTextEqual(currentMonthText);
    });

    it('Текст месяца корректный', () => {
        expect(Rating.filters.month.title).toHaveTextEqual(DATA.months.today);
    });

});
