/* eslint-disable jest/expect-expect */

import { showid } from '../showid';

describe('home__showid', () => {
    let oldVersion: typeof home.staticVersion;

    beforeAll(() => {
        oldVersion = home.staticVersion;
        jest.spyOn(Date, 'now').mockReturnValue(567000);
        jest.spyOn(Math, 'random').mockReturnValue(0.123456789);
    });

    afterAll(() => {
        home.staticVersion = oldVersion;
        jest.clearAllMocks();
    });

    function checkshowId(str: string, versionStr: string) {
        expect(str).not.toMatch(/[a-z]/i);
        const groups = str.split('.');
        expect(groups).toHaveLength(4);
        // В первой группе время
        expect(groups[0]).toEqual('567');
        // Во второй группе версия
        expect(groups[1]).toEqual(versionStr);
        // В предпоследней группе рандом
        expect(groups[2]).toEqual('12345');
        // В последней группе - tail
        expect(groups[3]).toEqual('22222');
    }

    test('не меняет цифровые версии', () => {
        home.staticVersion = '12345';

        checkshowId(showid('22222'), home.staticVersion);
    });

    test('переводит буквы в числа', () => {
        home.staticVersion = '123hotfix4beta3';

        checkshowId(showid('22222'), '45324143');
    });

    test('выкидывает все остальные символы', () => {
        home.staticVersion = 'ололо.Версия-один111!!!##';

        checkshowId(showid('22222'), '111');
    });
});
