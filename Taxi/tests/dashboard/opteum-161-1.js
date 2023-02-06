const DashboardPage = require('../../page/DashboardPage');

describe('Сводка: фильтры: кнопки', () => {

    const DATA = {
        filters: [
            'Сегодня',
            'Вчера',
            'Неделя',
            'Месяц',
            'Выберите период',
        ],
        // индекс фильтра по умолчанию из списка выше
        checked: 0,
    };

    const checkedFilter = DATA.filters[DATA.checked];

    let savedGraphs;

    it('Открыть страницу сводки', () => {
        DashboardPage.goTo();
    });

    it('Отображаются корректные фильтры даты', () => {
        expect(DashboardPage.filter.buttons).toHaveTextEqual(DATA.filters);
    });

    it(`По умолчанию отображается фильтр "${checkedFilter}"`, () => {
        expect(DashboardPage.filter.checked).toHaveTextEqual(checkedFilter);
    });

    DATA.filters.forEach((filter, i) => {
        describe(filter, () => {

            it(`Выбрать фильтр "${filter}"`, () => {
                DashboardPage.filter.buttons[i].click();
            });

            // не проверяем первое нажатие — первый фильтр уже выбран по умолчанию
            if (i > 0) {
                it('Графики изменились', () => {
                    expect(DashboardPage.dashboards.paths).not.toHaveElemEqual(savedGraphs);
                });
            }

            // в последней итерации незачем сохранять графики
            if (i !== filter.length - 1) {
                it('Сохранить текущие графики', () => {
                    savedGraphs = DashboardPage.dashboards.paths;
                });
            }
        });
    });

});
