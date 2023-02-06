const Main = require('../../page/Main');
const re = require('../../../../utils/consts/re');
const timeouts = require('../../../../utils/consts/timeouts');

const checkPosts = () => {
    it('Текст постов корректный', () => {
        expect(Main.teamBlock.posts.text).toHaveTextOk();
    });

    it('У постов корректные имена сотрудников', () => {
        expect(Main.teamBlock.posts.name).toHaveTextMatch(re.nameSurname);
    });

    it('У постов корректные картинки сотрудников', () => {
        expect(Main.teamBlock.posts.image).toHaveAttributeMatch('src', re.avatarPic);
    });

    it('Запросы картинок сотрудников возвращают 200', () => {
        expect(Main.teamBlock.posts.image).toHaveAttributeLinkRequestStatus('src', 200);
    });
};

describe('Главная: как мы работаем', () => {

    const DATA = {
        title: 'Как мы работаем22',
        posts: {
            count: 6,
            pagination: 2,
        },
        button: 'больше цитат',
    };

    it('Открыть главную страницу', () => {
        Main.goTo();
    });

    it(`Отображается заголовок "${DATA.title}"`, () => {
        Main.teamBlock.title.scrollIntoView();
        expect(Main.teamBlock.title).toHaveTextEqual(DATA.title);
    });

    it(`Отображаются ${DATA.posts.count} постов`, () => {
        expect(Main.teamBlock.posts.text).toHaveLength(DATA.posts.count);
    });

    checkPosts();

    it(`Отображается кнопка "${DATA.button}"`, () => {
        expect(Main.teamBlock.more).toHaveTextEqual(DATA.button);
    });

    it(`При нажатии кнопки "${DATA.button}" отображается на ${DATA.posts.pagination} поста больше`, () => {
        Main.teamBlock.more.click();
        expect(Main.teamBlock.posts.text).toHaveLength(DATA.posts.count + DATA.posts.pagination);
    });

    it(`Кнопка "${DATA.button}" пропадает после подгрузки всех постов`, () => {
        browser.waitUntil(() => {
            Main.teamBlock.more.click();
            return !Main.teamBlock.more.isDisplayed();
        }, {
            timeout: timeouts.waitUntil,
            timeoutMsg: `Кнопка "${DATA.button}" не пропала после подгрузки всех постов`,
        });
    });

    // проверяем посты ещё раз: после подгрузки всех скрытых
    checkPosts();

});
