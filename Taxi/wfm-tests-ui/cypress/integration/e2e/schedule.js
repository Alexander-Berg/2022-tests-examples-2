// import profileData from './data/planning.json';

describe('Графики', () => {
    const wfmUser = 'autotest-profile';

    before(() => {});
    beforeEach(() => {
        cy.yandexLogin(wfmUser);
        // cy.visit('/schedules');
    });

    it('Загрузка страницы и проверка интерфейса', () => {
        cy.visit('/schedules');
    });
});
