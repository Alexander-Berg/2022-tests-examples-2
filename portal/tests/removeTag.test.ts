import { removeTag } from '../removeTag';

describe('home.removeTag', function() {
    test('Removing tag from text', function() {
        expect(removeTag('span', '<span>Hello</span> world!')).toEqual('Hello world!');
        expect(removeTag('a', '<aside><a href="http://www.moscow.ru" style="color: red;">Moscow</a> is the capital of <a href="http://www.ru">Russia!</a></aside>'))
            .toEqual('<aside>Moscow is the capital of Russia!</aside>');
    });
});
