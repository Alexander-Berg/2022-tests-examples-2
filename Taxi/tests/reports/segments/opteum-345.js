const AutoCard = require('../../../page/AutoCard');
const ReportsSegments = require('../../../page/ReportsSegments');

describe('Переход к списку водителей из "Сегменты водителей"', () => {

    const DATA = {
        link: 'Все водители',
    };

    it('Открыть страницу сегментов водителей', () => {
        ReportsSegments.goTo();
    });

    it(`Отображается ссылка "${DATA.link}"`, () => {
        expect(ReportsSegments.header.links.drivers).toHaveTextEqual(DATA.link);
    });

    it(`Нажать на ссылку "${DATA.link}"`, () => {
        ReportsSegments.header.links.drivers.click();
    });

    it('Переключиться на открывшийся таб водителей', () => {
        ReportsSegments.switchTab();
    });

    it('Открылась страница всех водителей', () => {
        expect(browser).toHaveUrlContaining(`${AutoCard.baseUrl}/drivers`);
    });

});
