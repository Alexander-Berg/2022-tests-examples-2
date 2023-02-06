const footerChecks = require('../../shared/footer');
const Vacancies = require('../../page/Vacancies');

describe('Вакансии: выбранная вакансия: подвал', () => {

    it('Открыть страницу первой вакансии из списка всех вакансий', () => {
        Vacancies.goToFirstVacancy();
    });

    footerChecks();
});
