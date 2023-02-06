const re = require('../../../../utils/consts/re');
const Vacancies = require('../../page/Vacancies');

describe('Вакансии: отображение', () => {

    const COUNT = 21;

    const DATA = {
        title: `Вакансии${COUNT}`,
        quote: {
            name: 'Юрий Мещеряков',
            position: 'Руководитель отдела подбора персонала Яндекс Go',
            image: '/avatars/ymshch.jpg',
            links: [
                '/interview',
                '/office',
            ],
        },
        posts: {
            title: [
                'Кого ищем',
                'Кто ищет',
            ],
            hrefs: /\/vacancies\/\w+/,
        },
        button: {
            text: 'больше вакансий',
            link: 'https://yandex.ru/jobs/vacancies/'
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

    it('Открыть страницу вакансий', () => {
        Vacancies.goTo();
    });

    it('Отображается заголовок', () => {
        expect(Vacancies.title).toHaveTextEqual(DATA.title);
    });

    it('Отображается текст главного поста', () => {
        expect(Vacancies.quoteBlock.text).toHaveTextOk();
    });

    DATA.quote.links.forEach((elem, i) => {
        it(`В тексте главного поста есть ссылка ${elem}`, () => {
            expect(Vacancies.quoteBlock.links[i]).toHaveAttributeArrayIncludes('href', elem);
        });
    });

    it('У главного поста отображается аватарка сотрудника', () => {
        expect(Vacancies.quoteBlock.avatar).toHaveAttributeArrayIncludes('src', DATA.quote.image);
    });

    it('Аватарка сотрудника у главного поста отдаёт 200', () => {
        expect(Vacancies.quoteBlock.avatar).toHaveAttributeLinkRequestStatus('src', 200);
    });

    it('У главного поста отображается имя сотрудника', () => {
        expect(Vacancies.quoteBlock.name).toHaveTextEqual(DATA.quote.name);
    });

    it('У главного поста отображается позиция сотрудника', () => {
        expect(Vacancies.quoteBlock.position).toHaveTextEqual(DATA.quote.position);
    });

    it('У вакансий отображается заголовок', () => {
        expect(Vacancies.vacanciesBlock.header).toHaveTextEqual(DATA.posts.title);
    });

    it(`Отображается ${COUNT} вакансий`, () => {
        expect(Vacancies.vacanciesBlock.team.text).toHaveLength(COUNT);
    });

    it('У вакансий отображается позиция', () => {
        expect(Vacancies.vacanciesBlock.name).toHaveTextOk();
    });

    it('У вакансий отображаются теги', () => {
        expect(Vacancies.vacanciesBlock.tags).toHaveTextOk();
    });

    it('У вакансий отображаются имена нанимающих', () => {
        expect(Vacancies.vacanciesBlock.team.name).toHaveTextMatch(re.nameSurname);
    });

    it('У вакансий отображаются аватарки нанимающих', () => {
        expect(Vacancies.vacanciesBlock.team.avatar).toHaveAttributeMatch('src', re.avatarPic);
    });

    it('Аватарки нанимающих отдают 200', () => {
        expect(Vacancies.vacanciesBlock.team.avatar).toHaveAttributeLinkRequestStatus('src', 200);
    });

    it('У вакансий отображаются должности нанимающих', () => {
        expect(Vacancies.vacanciesBlock.team.position).toHaveTextOk();
    });

    it('У вакансий отображаются тексты нанимающих', () => {
        expect(Vacancies.vacanciesBlock.team.text).toHaveTextOk();
    });

    it('У вакансий корректные ссылки', () => {
        expect(Vacancies.vacanciesBlock.links).toHaveAttributeMatch('href', DATA.posts.hrefs);
    });

    it(`Отображается кнопка "${DATA.button.text}"`, () => {
        expect(Vacancies.vacanciesBlock.more).toHaveTextEqual(DATA.button.text);
    });

    it('У кнопки корректная ссылка', () => {
        expect(Vacancies.vacanciesBlock.more).toHaveAttributeEqual('href', DATA.button.link);
    });

});
