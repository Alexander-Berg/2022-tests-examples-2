const ScoringPage = require('../../page/ScoringPage');

describe('Скоринг: водитель с купленной историей: таблица', () => {

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
            cars: [
                'BMW7er\nН***НН777\nТакси-вжух 25 февр. 2021 г. – н. в.',
                'AcuraILX\nA***AA555\nПрокуренный Извозчик 5 июн. 2020 г. – н. в.',
                'BMWX6\nУ***УУ99\nSea bream 2 авг. 2019 г. – н. в.',
            ],
        },
    };

    it('Открыть страницу скоринга водителей', () => {
        ScoringPage.goTo('?license=5555555555');
    });

    it(`Отображается заголовок таблицы "${DATA.table.title}"`, () => {
        expect(ScoringPage.parks.title).toHaveElemVisible();
    });

    it('Отображаются корректные колонки таблицы', () => {
        expect(ScoringPage.parks.table.columns).toHaveTextEqual(DATA.table.columns);
    });

    DATA.table.cars.forEach((elem, i) => {
        it(`В таблице на строке "${i + 1}" отображаются корректные машины`, () => {
            expect(ScoringPage.parks.table.rows[i]).toHaveTextIncludes(elem);
        });
    });

});
