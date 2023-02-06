import {extractTicketFromPath} from '../extractTicketFromPath';

describe('extractTicketFromPath', () => {
    test('Корректно достает тикет из URL', () => {
        const str = 'https://st.yandex-team.ru/TAXIFRONTINFRA-2543';
        const expected = 'TAXIFRONTINFRA-2543';

        expect(extractTicketFromPath(str)).toEqual(expected);
    });

    test('Корректно достает тикет из URL со слешем на конце', () => {
        const str = 'https://st.yandex-team.ru/TAXIFRONTINFRA-2543/';
        const expected = 'TAXIFRONTINFRA-2543';

        expect(extractTicketFromPath(str)).toEqual(expected);
    });

    test('Корректно оставлет тикет, если он не является URL', () => {
        const str = 'TAXIFRONTINFRA-2543';
        const expected = 'TAXIFRONTINFRA-2543';

        expect(extractTicketFromPath(str)).toEqual(expected);
    });

    test('Возвращает undefined, если на вход приходит undefined или ничего не передали', () => {
        expect(extractTicketFromPath()).toBeUndefined();
    });
});
