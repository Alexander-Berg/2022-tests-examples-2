const ScoringPage = require('../../page/ScoringPage');

describe('Отображение истории автомобиля', () => {

    const DATA = [
        {
            license: 5_555_555_555,
            title: 'История BMW X6 Y009YY99\n'
                 + 'за последние 5 дней',
            table: 'Компания Водитель Последний заказ\n'
                 + 'Другой парк Другой водитель 26 июля 2021 г.',
        },
        {
            license: 4_587_757_576,
            title: 'История BMW 7er P743PM77',
            text: 'На этом автомобиле не выполнялись заказы последние 5 дней',
        },
        {
            license: 'ААВВ000003',
            title: 'История Audi A2 Y004YY78',
            text: 'Подтвердите СТС для получения информации',
        },
        {
            license: 4_507_333_333,
            title: 'История BMW 7er A133AA77\n'
                 + 'за последние 5 дней',
            table: 'Компания Водитель Последний заказ\n'
                 + 'Ваш парк Другой водитель 12 августа 2021 г.',
        },
        {
            license: 3_424_323_423,
            title: 'История BMW 7er M453MM43\n'
                 + 'за последние 5 дней',
            table: 'Компания Водитель Последний заказ\n'
                 + 'Ваш парк Ваш водитель 6 августа 2021 г.',
        },
    ];

    DATA.forEach(elem => {

        describe(`ВУ: ${elem.license}`, () => {

            it('Открыть страницу скоринга водителя', () => {
                ScoringPage.goTo(`?license=${elem.license}`);
            });

            it('Отобразился корректный заголовок истории', () => {
                expect(ScoringPage.report.titles).toHaveTextArrayIncludes(elem.title);
            });

            if (elem.table) {

                it('Отобразилась корректная таблица истории', () => {
                    expect(ScoringPage.report.history).toHaveTextEqual(elem.table);
                });

            } else if (elem.text) {

                it('Отобразился корректный текст вместо таблицы истории', () => {
                    expect(ScoringPage.report.text).toHaveTextEqual(elem.text);
                });

            }

        });

    });

});
