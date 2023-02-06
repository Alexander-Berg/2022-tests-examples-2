const headerChecks = require('../../shared/header');
const Vacancies = require('../../page/Vacancies');

describe('Вакансии: выбранная вакансия: шапка', () => {

    it('Открыть страницу первой вакансии из списка всех вакансий', () => {
        Vacancies.goToFirstVacancy();
    });

    headerChecks();
});
