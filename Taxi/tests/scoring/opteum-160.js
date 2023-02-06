const ScoringPage = require('../../page/ScoringPage');

describe('Скоринг: водитель без купленной истории: поиск', () => {

    const DATA = {
        license: 7_716_235_662,
        driver: {
            name: 'Денис Новиков',
            age: '22 года, дата рождения 01.01.2000',
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
