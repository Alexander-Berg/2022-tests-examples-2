import fetchMock from 'jest-fetch-mock';

import { Options, VersionUpdateChecker } from '../src';
import { delay, get } from '../src/utils';

import FunctionPropertyNames = jest.FunctionPropertyNames;

const COMMON_INIT_PARAMS: Options = {
    url: 'mock-api',
    checkInterval: 0.5,
    handleVersionChange: () => null,
    handleVersionFetchError: () => null
};

describe('Тесты класса VersionUpdateChecker', () => {
    let checker;

    beforeAll(() => {
        fetchMock.enableMocks();
    });

    beforeEach(() => {
        fetchMock.resetMocks();

        checker = new VersionUpdateChecker({
            ...COMMON_INIT_PARAMS
        });

        jest.spyOn(checker, 'checkVersion' as FunctionPropertyNames<VersionUpdateChecker>);
        jest.spyOn(checker, 'handleVersionChange' as FunctionPropertyNames<VersionUpdateChecker>);
        jest.spyOn(checker, 'handleVersionFetchError' as FunctionPropertyNames<VersionUpdateChecker>);
    });

    afterEach(() => {
        checker.stop();
    });

    describe('Корректная отправка запросов для проверки версии', () => {
        fetchMock.mockResponse(JSON.stringify({ version: '0' }));

        test('Делает запрос сразу после старта', async () => {
            checker.start();

            await delay();

            expect(checker['checkVersion']).toHaveBeenCalledTimes(1);
        });

        test('Если версия не изменилась, делает повторный запрос', async () => {
            checker.start();

            await delay(0.6);

            expect(checker['checkVersion']).toHaveBeenCalledTimes(2);
        });

        test('Правильно останавливает и возобновляет процесс проверки', async () => {
            checker.start();

            await delay(0.6);

            expect(checker['checkVersion']).toHaveBeenCalledTimes(2);

            checker.stop();

            await delay(1);

            expect(checker['checkVersion']).toHaveBeenCalledTimes(2);

            checker.start();

            expect(checker['checkVersion']).toHaveBeenCalledTimes(3);

            await delay(0.6);

            expect(checker['checkVersion']).toHaveBeenCalledTimes(4);
        });
    });

    describe('Корректная работа при передаче начальной версии', () => {
        fetchMock.mockResponse(JSON.stringify({ version: '0' }));

        let checker;

        beforeEach(() => {
            checker = new VersionUpdateChecker({
                ...COMMON_INIT_PARAMS,
                initialVersion: '0'
            });

            jest.spyOn(checker, 'checkVersion' as FunctionPropertyNames<VersionUpdateChecker>);
            jest.spyOn(checker, 'handleVersionChange' as FunctionPropertyNames<VersionUpdateChecker>);
        });

        afterEach(() => {
            checker.stop();
        });

        test('Переданную при инициализации начальную версию считает текущей', async () => {
            checker.start();

            expect(checker.currentVersion).toEqual('0');
        });

        test('Если полученная версия совпадает с начальной, то обработчик изменения не вызывается', async () => {
            checker.start();

            await delay();

            expect(checker['checkVersion']).toHaveBeenCalledTimes(1);
            expect(checker['handleVersionChange']).toHaveBeenCalledTimes(0);
        });

        test('Если полученная версия не совпадает с начальной, то вызывается функция-обработчик', async () => {
            fetchMock.mockResponse(JSON.stringify({ version: '1' }));

            checker.start();

            await delay();

            expect(checker['checkVersion']).toHaveBeenCalledTimes(1);
            expect(checker['handleVersionChange']).toHaveBeenCalledTimes(1);
        });
    });

    describe('Корректная обработка разных форматов ответа ручки с версией', () => {
        test('Версия может быть вложенным свойством объекта при передаче верного versionFieldPath', async () => {
            fetchMock.mockResponse(JSON.stringify({ data: { serviceVersion: '1' } }));

            const checker = new VersionUpdateChecker({
                ...COMMON_INIT_PARAMS,
                versionFieldPath: 'data.serviceVersion'
            });

            checker.start();

            await delay();

            expect(checker.currentVersion).toEqual('1');

            checker.stop();
        });

        test('Ответ ручки может быть строкой', async () => {
            fetchMock.mockResponse('"1"');

            checker.start();

            await delay();

            expect(checker.currentVersion).toEqual('1');
        });
    });

    describe('Корректный запуск обработчиков', () => {
        test('Однократно запускает обработчик с правильными параметрами при изменении версии', async () => {
            fetchMock.mockResponse(JSON.stringify({ version: '0' }));

            checker.start();

            for (let version = 1; version <= 2; version++) {
                fetchMock.mockResponse(JSON.stringify({ version: String(version) }));
                await delay(1);
                expect(checker['handleVersionChange'])
                    .toHaveBeenNthCalledWith(version, String(version - 1), String(version));
            }

            expect(checker['handleVersionChange']).toHaveBeenCalledTimes(2);
        });

        test('В случае ошибки в запросе запускает обработчик этой ошибки', async () => {
            const responseError = new Error('Error while fetching version');
            fetchMock.mockRejectOnce(responseError);

            checker.start();

            await delay();

            expect(checker['handleVersionFetchError']).toHaveBeenCalledTimes(1);
            expect(checker['handleVersionFetchError']).toHaveBeenCalledWith(responseError);
        });
    });

    describe('Корректная работа функции сравнения версий', () => {
        let checker;

        beforeEach(() => {
            fetchMock.mockResponse(JSON.stringify({ version: '1.1.0' }));

            checker = new VersionUpdateChecker({
                ...COMMON_INIT_PARAMS,
                initialVersion: '1.1.0',
                isVersionsEqual: (oldVersion, newVersion) => +oldVersion.split('.')[1] >= +newVersion.split('.')[1]
            });

            jest.spyOn(checker, 'isVersionsEqual' as FunctionPropertyNames<VersionUpdateChecker>);
            jest.spyOn(checker, 'handleVersionChange' as FunctionPropertyNames<VersionUpdateChecker>);
        });

        afterEach(() => {
            checker.stop();
        });

        test('Функция правильно отрабатывает для одинаковых версий', async () => {
            checker.start();

            await delay(0.6);

            expect(checker['isVersionsEqual']).toHaveBeenCalledTimes(2);
            expect(checker['handleVersionChange']).toHaveBeenCalledTimes(0);
        });

        test('Функция правильно отрабатывает для разных версий', async () => {
            checker.start();

            await delay(0.6);

            fetchMock.mockResponse(JSON.stringify({ version: '1.2.0' }));

            await delay(0.6);

            expect(checker['isVersionsEqual']).toHaveBeenCalledTimes(3);
            expect(checker['handleVersionChange']).toHaveBeenCalledTimes(1);
        });
    });
});

describe('Тесты утилити-функции get', () => {
    describe('Корректное базовое использование', () => {
        test('Плоский объект', () => {
            expect(get({ a: 1 }, 'a')).toStrictEqual(1);
        });

        test('Массив', () => {
            expect(get([0, 1], '1')).toStrictEqual(1);
        });

        test('Вложенный массив', () => {
            expect(get([0, [0, 1, 2]], '1.1')).toStrictEqual(1);
        });

        test('Глубокая вложенность', () => {
            expect(get({ a: { b: { c: { d: 1 } } } }, 'a.b.c.d')).toStrictEqual(1);
        });

        test('Сложная структура объектов и массивов', () => {
            expect(get({ a: [{ b: { c: 1, d: 2 } }, [{ e: [0, 1, 2] }]], f: [0, 1] }, 'a.1.0.e.1')).toStrictEqual(1);
        });
    });

    describe('Корректная работа в случае, когда по указанному пути ничего не содержится', () => {
        test('Отсутствующее в объекте свойство', () => {
            expect(get({ a: 1 }, 'b')).toStrictEqual(undefined);
        });

        test('Отсутствующий в массиве индекс', () => {
            expect(get([0, 1], '2')).toStrictEqual(undefined);
        });

        test('Отсутствующий путь во вложенной структуре', () => {
            expect(get({ a: { b: [{ c: 1 }] } }, 'a.b.0.e')).toStrictEqual(undefined);
            expect(get({ a: { b: [{ c: 1 }] } }, 'a.c.0')).toStrictEqual(undefined);
            expect(get({ a: { b: [{ c: 1 }] } }, 'b')).toStrictEqual(undefined);
        });
    });

    describe('Корректно возвращает falsy значения', () => {
        test('false', () => {
            expect(get({ a: { b: false } }, 'a.b')).toStrictEqual(false);
        });

        test('null', () => {
            expect(get({ a: { b: null } }, 'a.b')).toStrictEqual(null);
        });

        test('undefined', () => {
            expect(get({ a: { b: undefined } }, 'a.b')).toStrictEqual(undefined);
        });

        test('0', () => {
            expect(get({ a: { b: 0 } }, 'a.b')).toStrictEqual(0);
        });

        test('Пустая строка', () => {
            expect(get({ a: { b: '' } }, 'a.b')).toStrictEqual('');
        });
    });
});
