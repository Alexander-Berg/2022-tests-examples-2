const ScoringPage = require('../../page/ScoringPage');

describe('Скоринг: водитель без купленной истории: таблица', () => {

    const DATA = {
        table: {
            title: 'В других таксопарках',
            columns: [
                'Машина',
                'Компания',
                'Даты',
                'Фотоконтроль',
                'Баланс',
                'Долг по аренде',
            ],
            car: 'BMW7er\nТ***ВМ98\nSea bream 25 февр. 2022 г. – н. в.',
        },
    };

    it('Открыть страницу скоринга водителей', () => {
        ScoringPage.goTo('?license=7716235662');
    });

    it(`Отображается заголовок таблицы "${DATA.table.title}"`, () => {
        expect(ScoringPage.parks.title).toHaveElemVisible();
    });

    it('Отображаются корректные колонки таблицы', () => {
        expect(ScoringPage.parks.table.columns).toHaveTextEqual(DATA.table.columns);
    });

    it('В таблице отображается корректная машина', () => {
        expect(ScoringPage.parks.table.rows).toHaveTextIncludes(DATA.table.car);
    });

});
