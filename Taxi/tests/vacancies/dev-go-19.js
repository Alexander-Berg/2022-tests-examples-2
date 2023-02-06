const Vacancies = require('../../page/Vacancies');

describe('Вакансии: фильтрация: по городу', () => {

    const DATA = {
        default: 'город',
        cities: [
            'Москва',
            'Санкт-Петербург',
            'Нижний Новгород',
            'Екатеринбург',
            'Сочи',
            'Ростов-на-Дону',
        ],
        // два города из массива выше, которые будем выбирать в тесте
        cityToChoose: ['Екатеринбург', 'Сочи'],
        // фильтр, который будем выбирать в дополнение к городу
        // чтобы отобразилась ошибка отсутствующих вакансий для фильтра
        tagToChoose: {
            name: 'QA',
            index: 3,
        },
        error: {
            text:
                'Увы, мы не нашли вакансий по выбранным параметрам.\n'
              + 'Попробуй изменить фильтры направления и города или посмотреть наши вакансии на сайте Яндекса.',
            link:
                'https://yandex.ru/jobs/vacancies/'
              + '?services=taxi'
              + '&services=eda'
              + '&services=lavka'
              + '&services=dostavka'
              + '&professions=backend-developer'
              + '&professions=frontend-developer'
              + '&professions=tester'
              + '&professions=ml-developer'
              + '&professions=mob-app-developer-android'
              + '&professions=mob-app-developer'
              + '&professions=dev-ops'
              + '&professions=mob-app-developer-ios'
              + '&professions=database-developer'
              + '&professions=full-stack-developer'
              + '&from=devgoyandex',
        },
    };

    let defaultVacancies;
    const [firstCityName, secondCityName] = DATA.cityToChoose;

    it('Открыть страницу вакансий', () => {
        Vacancies.goTo();
    });

    it('Отображается дропдаун города с текстом по умолчанию', () => {
        Vacancies.filtersBlock.city.selected.scrollIntoView({block: 'center'});
        expect(Vacancies.filtersBlock.city.selected).toHaveTextEqual(DATA.default);
    });

    it('Сохранить список вакансий по умолчанию', () => {
        defaultVacancies = Vacancies.vacanciesBlock.name.map(elem => elem.getText());
    });

    it('Открыть дропдаун городов', () => {
        Vacancies.filtersBlock.city.dropdown.click();
    });

    it('Отображаются корректные города', () => {
        expect(Vacancies.filtersBlock.city.cities).toHaveTextEqual(DATA.cities);
    });

    it(`Выбрать город "${firstCityName}"`, () => {
        Vacancies.filtersBlock.city.cities[DATA.cities.indexOf(firstCityName)].click();
    });

    it('Список вакансий после выбора города поменялся', () => {
        expect(Vacancies.vacanciesBlock.name).not.toHaveTextEqual(defaultVacancies);
    });

    it('В дропдауне города поменялся текст на выбранный город', () => {
        expect(Vacancies.filtersBlock.city.selected).toHaveTextEqual(firstCityName);
    });

    it('У вакансий отображается выбранный город', () => {
        expect(Vacancies.vacanciesBlock.tags).toHaveTextArrayIncludes(firstCityName);
    });

    it('Открыть дропдаун городов', () => {
        Vacancies.filtersBlock.city.dropdown.click({js: true});
    });

    it(`Дополнительно выбрать город "${secondCityName}"`, () => {
        Vacancies.filtersBlock.city.cities[DATA.cities.indexOf(secondCityName)].click();
    });

    it(`В дропдауне города поменялся текст на "${firstCityName} +1"`, () => {
        expect(Vacancies.filtersBlock.city.selected).toHaveTextEqual(`${firstCityName} +1`);
    });

    it(`Выбрать фильтр "${DATA.tagToChoose.name}"`, () => {
        Vacancies.filtersBlock.tags[DATA.tagToChoose.index].click();
    });

    it('Отобразилось сообщение об отсутствующих вакансиях', () => {
        expect(Vacancies.filtersBlock.error.text).toHaveTextEqual(DATA.error.text);
    });

    it('В сообщении присутствует корректная ссылка', () => {
        expect(Vacancies.filtersBlock.error.link).toHaveAttributeEqual('href', DATA.error.link);
    });

});
