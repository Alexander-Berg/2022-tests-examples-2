const Vacancies = require('../../page/Vacancies');

describe('Вакансии: фильтрация: по типу', () => {

    const DATA = {
        tags: {
            // кнопка на dev-go: путь в ссылке на "больше вакансий"
            frontend: 'frontend-developer',
            backend: 'backend-developer',
            mobile: 'mob-app-developer',
            QA: 'tester',
            ML: 'ml-developer',
            data: 'analyst',
        },
        button: {
            text: 'больше вакансий',
            getJobProfessionLink: profession => `https://yandex.ru/jobs/professions/${profession}`
                + '?services=taxi'
                + '&services=eda'
                + '&services=lavka'
                + '&services=dostavka'
                + '&from=devgoyandex',
        },
    };

    it('Открыть страницу вакансий', () => {
        Vacancies.goTo();
    });

    it('Отображаются кнопки фильтрации вакансий', () => {
        Vacancies.filtersBlock.tags[0].scrollIntoView({block: 'center'});
        expect(Vacancies.filtersBlock.tags).toHaveTextEqual(Object.keys(DATA.tags));
    });

    let currentVacancies, defaultVacancies;

    it('Сохранить список вакансий по умолчанию', () => {
        defaultVacancies = Vacancies.vacanciesBlock.name.map(elem => elem.getText());
    });

    Object.entries(DATA.tags).forEach(([tag, profession], i) => {

        it(`Сохранить список "${DATA.tags[i - 1] || 'текущих'}" вакансий`, () => {
            currentVacancies = Vacancies.vacanciesBlock.name.map(elem => elem.getText());
        });

        it(`Выбрать фильтр "${tag}"`, () => {
            Vacancies.filtersBlock.tags[i].click();
        });

        it(`Список вакансий по фильтру "${tag}" изменился`, () => {
            expect(Vacancies.vacanciesBlock.name).not.toHaveTextEqual(currentVacancies);
        });

        it(`У вакансий отображается выбранный тег "${tag}"`, () => {
            expect(Vacancies.vacanciesBlock.tags).toHaveTextArrayIncludes(tag.toLowerCase());
        });

        it(`Отображается кнопка "${DATA.button.text}"`, () => {
            expect(Vacancies.vacanciesBlock.more).toHaveTextEqual(DATA.button.text);
        });

        it(`У кнопки корректная ссылка на профессию ${profession}`, () => {
            expect(Vacancies.vacanciesBlock.more).toHaveAttributeEqual('href', DATA.button.getJobProfessionLink(profession));
        });

        // на последнем фильтре проверяем его снятие
        if (i === DATA.tags.length - 1) {

            it(`Сохранить список "${tag}" вакансий`, () => {
                currentVacancies = Vacancies.vacanciesBlock.name.map(elem => elem.getText());
            });

            it(`Отменить фильтр "${tag}"`, () => {
                Vacancies.filtersBlock.tags[i].click();
            });

            it('Отображается полный список вакансий', () => {
                expect(Vacancies.vacanciesBlock.name).toHaveTextEqual(defaultVacancies);
            });

        }
    });

});
