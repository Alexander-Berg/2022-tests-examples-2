const ScoringPage = require('../../page/ScoringPage');

describe('Скоринг: водитель с купленной историей: поиск', () => {

    const DATA = {
        license: 5_555_555_555,
        driver: {
            name: 'Дарья Федосеева',
            age: '23 года, дата рождения 02.02.1999',
        },
    };

    it('Открыть страницу скоринга водителей', () => {
        ScoringPage.goTo();
    });

    it(`Найти водителя с ВУ "${DATA.license}"`, () => {
        ScoringPage.queryFilter(ScoringPage.search, DATA.license);
    });

    it('Отобразилось корректное имя водителя', () => {
        expect(ScoringPage.driver.name).toHaveTextEqual(DATA.driver.name);
    });

    it('Отобразился корректный возраст водителя', () => {
        expect(ScoringPage.driver.age).toHaveTextEqual(DATA.driver.age);
    });

    it('Отобразилась аватарка водителя', () => {
        expect(ScoringPage.driver.avatar).toHaveElemVisible();
    });

});
