const Main = require('../../page/Main');
const re = require('../../../../utils/consts/re');

describe('Главная: кого ищем', () => {

    const DATA = {
        title: 'Кого ищем21',
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
            title: 'Кого ищем\nКто ищет',
            count: 3,
            tags: /^(Москва|Санкт-Петербург|mobile|backend)$/,
        },
        button: {
            text: 'больше вакансий',
            link: '/vacancies',
        },
    };

    it('Открыть главную страницу', () => {
        Main.goTo();
    });

    it(`Отображается заголовок "${DATA.title}"`, () => {
        Main.vacanciesBlock.title.scrollIntoView();
        expect(Main.vacanciesBlock.title).toHaveTextEqual(DATA.title);
    });

    it('Отображается текст главного поста', () => {
        expect(Main.vacanciesBlock.quote.text).toHaveTextOk();
    });

    DATA.quote.links.forEach((elem, i) => {
        it(`В тексте главного поста есть ссылка ${elem}`, () => {
            expect(Main.vacanciesBlock.quote.links[i]).toHaveAttributeArrayIncludes('href', elem);
        });
    });

    it('У главного поста отображается аватарка сотрудника', () => {
        expect(Main.vacanciesBlock.quote.image).toHaveAttributeArrayIncludes('src', DATA.quote.image);
    });

    it('Аватарка сотрудника у главного поста отдаёт 200', () => {
        expect(Main.vacanciesBlock.quote.image).toHaveAttributeLinkRequestStatus('src', 200);
    });

    it('У главного поста отображается имя сотрудника', () => {
        expect(Main.vacanciesBlock.quote.name).toHaveTextEqual(DATA.quote.name);
    });

    it('У главного поста отображается позиция сотрудника', () => {
        expect(Main.vacanciesBlock.quote.position).toHaveTextEqual(DATA.quote.position);
    });

    it('У вакансий отображается заголовок', () => {
        expect(Main.vacanciesBlock.posts.title).toHaveTextEqual(DATA.posts.title);
    });

    it(`Отображается ${DATA.posts.count} вакансии`, () => {
        expect(Main.vacanciesBlock.posts.team.text).toHaveLength(DATA.posts.count);
    });

    it('У вакансий отображается позиция', () => {
        expect(Main.vacanciesBlock.posts.position).toHaveTextOk();
    });

    it('У вакансий отображаются теги', () => {
        expect(Main.vacanciesBlock.posts.tags).toHaveTextMatch(DATA.posts.tags);
    });

    it('У вакансий отображаются имена нанимающих', () => {
        expect(Main.vacanciesBlock.posts.team.name).toHaveTextMatch(re.nameSurname);
    });

    it('У вакансий отображаются аватарки нанимающих', () => {
        expect(Main.vacanciesBlock.posts.team.image).toHaveAttributeMatch('src', re.avatarPic);
    });

    it('Аватарки нанимающих отдают 200', () => {
        expect(Main.vacanciesBlock.posts.team.image).toHaveAttributeLinkRequestStatus('src', 200);
    });

    it('У вакансий отображаются должности нанимающих', () => {
        expect(Main.vacanciesBlock.posts.team.position).toHaveTextOk();
    });

    it('У вакансий отображаются тексты нанимающих', () => {
        expect(Main.vacanciesBlock.posts.team.text).toHaveTextOk();
    });

    it(`Отображается кнопка "${DATA.button.text}"`, () => {
        expect(Main.vacanciesBlock.more).toHaveTextEqual(DATA.button.text);
    });

    it(`У кнопки корректная ссылка ${DATA.button.link}`, () => {
        expect(Main.vacanciesBlock.more).toHaveAttributeArrayIncludes('href', DATA.button.link);
    });

});
