const Main = require('../../page/Main');
const re = require('../../../../utils/consts/re');

describe('Главная: о чём пишем', () => {

    const DATA = {
        title: 'О чём пишем13',
        cards: {
            count: 4,
            title: /^(backend|DWH)\nhabr$/,
            habrLinks: /^https:\/\/habr\.com\/ru\/company\/yandex\/blog\/\d{6}$/,
        },
    };

    const defaultCards = [];

    it('Открыть главную страницу', () => {
        Main.goTo();
    });

    it(`Отображается заголовок "${DATA.title}"`, () => {
        Main.writersBlock.title.scrollIntoView();
        expect(Main.writersBlock.title).toHaveTextEqual(DATA.title);
    });

    it(`Отображаются ${DATA.cards.count} карточки`, () => {
        expect(Main.writersBlock.cards.active).toHaveLength(DATA.cards.count);
    });

    it('У карточек корректные ссылки', () => {
        expect(Main.writersBlock.cards.link).toHaveAttributeMatch('href', DATA.cards.habrLinks);
    });

    it('У карточек корректные заголовки', () => {
        expect(Main.writersBlock.cards.title).toHaveTextMatch(DATA.cards.title);
    });

    it('У карточек корректные тексты', () => {
        expect(Main.writersBlock.cards.text).toHaveTextOk();
    });

    it('Сохраняем тексты дефолтных карточек', () => {
        Main.writersBlock.cards.text
            .forEach(elem => defaultCards.push(elem.getText()));
    });

    it('У карточек корректные имена сотрудников', () => {
        expect(Main.writersBlock.cards.name).toHaveTextMatch(re.nameSurname);
    });

    it('У карточек корректные картинки сотрудников', () => {
        expect(Main.writersBlock.cards.image).toHaveAttributeMatch('src', re.avatarPic);
    });

    it('Запросы картинок сотрудников возвращают 200', () => {
        expect(Main.writersBlock.cards.image).toHaveAttributeLinkRequestStatus('src', 200);
    });

    it('Под карточками отображаются стрелки прокрутки', () => {
        Main.writersBlock.arrows
            .forEach(elem => expect(elem).toBeDisplayed());
    });

    it('После клика на стрелку прокрутки отобразились новые карточки', () => {
        Main.writersBlock.arrows[1].click();
        expect(Main.writersBlock.cards.text).not.toHaveTextEqual(defaultCards);
    });

});
