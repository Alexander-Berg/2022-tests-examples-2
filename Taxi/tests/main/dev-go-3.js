const Header = require('../../page/Header');
const Main = require('../../page/Main');
const re = require('../../../../utils/consts/re');

describe('Главная: главная цитата', () => {

    const QUOTE = {
        name: 'Артём Молчанов',
        position: 'Руководитель продуктового направления Яндекс.Такси',
        text: 'Когда-то вся разработка помещалась в одну комнату, хоть и большую. И делала сервис для заказа такси. Теперь нам и целого здания мало, а Яндекс Go не только про машины, но и про товары, еду и продукты, самокаты.'
        + '\nВсем этим ежедневно пользуются миллионы людей, и наши друзья и родные тоже. Да и ваши, уверен. А мы делаем так, чтобы всё это работало: нон-стоп придумываем и улучшаем фичи, разрабатываем архитектуры и алгоритмы — и простые, и сложные.',
    };

    it('Открыть главную страницу', () => {
        Main.goTo();
    });

    it('Отображается текст главной цитаты', () => {
        Header.quoteBlock.paragraphs[0].scrollIntoView();
        expect(Header.quoteBlock.paragraphs).toHaveTextEqual(QUOTE.text);
    });

    it('Под цитатой отображается аватарка', () => {
        expect(Header.quoteBlock.person.avatar).toHaveAttributeMatch('src', re.avatarPic);
        expect(Header.quoteBlock.person.avatar).toHaveAttributeLinkRequestStatus('src', 200);
    });

    it('Под цитатой отображается имя', () => {
        expect(Header.quoteBlock.person.name).toHaveTextEqual(QUOTE.name);
    });

    it('Под цитатой отображается должность', () => {
        expect(Header.quoteBlock.person.position).toHaveTextEqual(QUOTE.position);
    });

});
