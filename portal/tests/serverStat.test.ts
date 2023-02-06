import { mockReq, Req3ServerMocked } from '@lib/views/mockReq';
import { Stat, makeStat } from '../serverStat';

describe('serverStat', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('off', () => {
        let fakeHashOff: Partial<Req3Server> = {
            LiveCartridge: 0
        };
        let stat: Stat;
        let req: Req3ServerMocked;

        beforeEach(function() {
            req = mockReq({}, fakeHashOff);
            stat = makeStat(req);
        });

        test('не включается с пустым хэшом', function() {
            const req = mockReq();
            expect(makeStat(req).on).toEqual(false);

            expect(req.setCounter.mock.calls).toHaveLength(0);
        });

        test('не включается с выключенным хэшом', function() {
            expect(stat.on).toEqual(false);
        });

        test('не возвращает рут', function() {
            expect(stat.getRoot()).toEqual('');
        });

        test('не генерирует path', function() {
            expect(stat.getPath('str')).toEqual('');

            expect(req.setCounter.mock.calls).toHaveLength(0);
        });

        test('не изменяет url', function() {
            expect(stat.getUrl('str', 'ya.ru')).toEqual('ya.ru');

            expect(req.setCounter.mock.calls).toHaveLength(0);
        });

        test('не генерирует аттрибуты', function() {
            expect(stat.getAttr('str')).toEqual('');
            expect(stat.getAttr('str', 'ya.ru')).toEqual('');
            expect(stat.getAttr('str', 'ya.ru', { isRedirect: false })).toEqual('');

            expect(req.setCounter.mock.calls).toHaveLength(0);
        });

        test('не генерирует аттрибуты адаптичных счетчиков', function() {
            expect(stat.getAdaptiveCounter('path')).toEqual('');

            expect(req.setCounter.mock.calls).toHaveLength(0);
        });

        test('не генерирует клиентские счётчики', function() {
            expect(stat.getClientCounter('path')).toEqual('');

            expect(req.setCounter.mock.calls).toHaveLength(0);
        });
    });

    describe('on (our urls)', () => {
        let stat: Stat;
        let req: Req3ServerMocked;

        beforeEach(() => {
            req = mockReq({}, {
                LiveCartridge: 1,
                statRoot: 'root',
                ShowID: '1.2.3.4'
            });
            req.setCounter.mockImplementation((path: string, url?: string) => {
                let res: Record<string, unknown> = {
                    our: 1
                };
                if (path) {
                    res.id = 'root.' + path;
                }
                if (url) {
                    res.url = url;
                }
                return res;
            });
            stat = makeStat(req);
        });

        test('включается', function() {
            expect(stat.on).toEqual(true);
        });

        test('возвращает рут', function() {
            expect(stat.getRoot()).toEqual('root');
        });

        test('генерирует path', function() {
            expect(stat.getPath('str')).toEqual('root.str');

            expect(req.setCounter.mock.calls).toHaveLength(1);
        });

        test('не изменяет url', function() {
            expect(stat.getUrl('str', 'ya.ru')).toEqual('ya.ru');
            expect(stat.getUrl('str', 'ya.ru', { logShow: false })).toEqual('ya.ru');

            expect(req.setCounter.mock.calls).toMatchSnapshot();
        });

        test('работает с дополнительными параметрами', function() {
            expect(stat.getUrl('str', 'ya.ru', { customParams: { index: 123 } })).toEqual('ya.ru');
            expect(req.setCounter.mock.calls).toMatchSnapshot();
        });

        test('работает с дополнительными параметрами 2', () => {
            stat.addCustomPageParams({ index: 123 });
            expect(stat.getUrl('str', 'ya.ru')).toEqual('ya.ru');
            expect(req.setCounter.mock.calls).toMatchSnapshot();
        });

        test('генерирует аттрибуты', function() {
            expect(stat.getAttr('str0')).toEqual(' data-statlog="str0" data-statlog-showed="1"');
            expect(stat.getAttr('str1', '', { isRedirect: false })).toEqual(' data-statlog="str1" data-statlog-showed="1" data-statlog-redir="0"');
            expect(stat.getAttr('str2', 'ya.ru')).toEqual(' data-statlog="str2" data-statlog-showed="1"');
            expect(stat.getAttr('str3', 'ya.ru', { isRedirect: false })).toEqual(' data-statlog="str3" data-statlog-showed="1" data-statlog-redir="0"');
            expect(stat.getAttr('str4', 'ya.ru', { logShow: false, precise: true })).toEqual(' data-statlog="str4" data-statlog-precise="1"');

            expect(req.setCounter.mock.calls).toMatchSnapshot();
        });

        test('генерирует атрибуты адаптивных счетчиков', function() {
            expect(stat.getAdaptiveCounter('path')).toEqual(' data-statlog="path" data-statlog-autoshow="1"');
            expect(stat.getAttr('path', null, { adaptive: true })).toEqual(' data-statlog="path" data-statlog-autoshow="1"');
            expect(stat.getAttr('path', null, { adaptive: true, logShow: false })).toEqual(' data-statlog="path" data-statlog-autoshow="1"');
            expect(stat.getAttr('path', null, { adaptive: true, logShow: true })).toEqual(' data-statlog="path" data-statlog-autoshow="1"');

            expect(req.setCounter.mock.calls).toHaveLength(0);
        });

        test('генерирует атрибуты клиентских счётчиков', function() {
            expect(stat.getClientCounter('path')).toEqual(' data-statlog="path"');
            expect(stat.getClientCounter('path', true)).toEqual(' data-statlog="path" data-statlog-redir="0"');

            expect(req.setCounter.mock.calls).toHaveLength(0);
        });

        test('пишет показы переданных счётчиков и возвращает пути без корня', function() {
            expect(stat.logShow('header')).toEqual('header');

            expect(req.setCounter.mock.calls).toHaveLength(1);
        });

        test('не пишет показы, если передать параметр в getAttr', function() {
            expect(stat.getAttr('str0', null, { logShow: false })).toEqual(' data-statlog="str0"');
            expect(stat.getAttr('str0', 'ya.ru', { logShow: false })).toEqual(' data-statlog="str0"');

            expect(req.setCounter.mock.calls).toMatchSnapshot();
        });

        test('не делает ничего, если путь не передали', function() {
            expect(stat.getAttr(undefined, 'ya.ru', { logShow: false })).toEqual('');
            expect(stat.getAdaptiveCounter(null)).toEqual('');
            expect(stat.getClientCounter('')).toEqual('');

            expect(req.setCounter.mock.calls).toHaveLength(0);
        });
    });

    describe('on (other urls)', function() {
        let stat: Stat;
        let req: Req3ServerMocked;

        beforeEach(() => {
            req = mockReq({}, {
                LiveCartridge: 1,
                statRoot: 'root',
                ShowID: '1.2.3.4'
            });
            req.setCounter.mockImplementation((path: string, url?: string) => {
                let res: Record<string, unknown> = {};
                if (path) {
                    res.id = 'root.' + path;
                }
                if (url) {
                    res.our = 0;
                    res.url = '//other/' + url;
                } else {
                    res.our = 1;
                }
                return res;
            });
            stat = makeStat(req);
        });

        test('включается', function() {
            expect(stat.on).toEqual(true);
        });

        test('генерирует path', function() {
            expect(stat.getPath('str')).toEqual('root.str');

            expect(req.setCounter.mock.calls).toHaveLength(1);
        });

        test('подписывает url', function() {
            expect(stat.getUrl('str', 'ya.ru')).toEqual('//other/ya.ru');

            expect(req.setCounter.mock.calls).toMatchSnapshot();
        });

        test('генерирует аттрибуты', function() {
            expect(stat.getAttr('str0')).toEqual(' data-statlog="str0" data-statlog-showed="1"');
            expect(stat.getAttr('str1', '', { isRedirect: false })).toEqual(' data-statlog="str1" data-statlog-showed="1" data-statlog-redir="0"');
            expect(stat.getAttr('str2', 'ya.ru')).toEqual(' data-statlog="str2" data-statlog-showed="1" data-statlog-url="//other/ya.ru"');
            expect(stat.getAttr('str3', 'ya.ru', { isRedirect: false })).toEqual(' data-statlog="str3" data-statlog-showed="1" data-statlog-redir="0"');

            expect(req.setCounter.mock.calls).toMatchSnapshot();
        });
    });

    describe('custom params', function() {
        let stat: Stat;
        let req: Req3ServerMocked;

        beforeEach(() => {
            req = mockReq({}, {
                LiveCartridge: 1,
                statRoot: 'root',
                ShowID: '1.2.3.4'
            });
            stat = makeStat(req);
        });

        test('передаёт дополнительные параметры', function() {
            stat.getAttr('path', 'url', { customParams: 123 });
            stat.getUrl('path', 'url', { customParams: { a: 'b' } });
            stat.getPath('path', 4);
            stat.logShow('path', 5);

            expect(req.setCounter.mock.calls).toMatchSnapshot();
        });

        test('добавляет дополнительные параметры в путь для логгирования на клиенте', function() {
            expect(stat.getAttr('path', null, {
                logShow: false,
                customParams: 42
            })).toEqual(' data-statlog="path(id=42)"');

            expect(stat.getAttr('path', null, {
                logShow: false,
                customParams: {
                    foo: 42,
                    bar: 'baz'
                }
            })).toEqual(' data-statlog="path(foo=42;bar=baz)"');
        });

        test('энкодит дополнительные параметры', function() {
            expect(stat.getAttr('path', null, {
                logShow: false,
                customParams: {
                    pi: '3,14',
                    place: '31,46;42,36'
                }
            })).toEqual(' data-statlog="path(pi=3%2C14;place=31%2C46%3B42%2C36)"');
        });

        test('не логируется undefined', function() {
            expect(stat.getAttr('path', null, {
                logShow: false,
                customParams: {
                    pi: '3,14',
                    place: undefined
                }
            })).toEqual(' data-statlog="path(pi=3%2C14)"');
        });

        test('пустая строка, если в объекте толкьо undefined value', function() {
            expect(stat.getAttr('path', null, {
                logShow: false,
                customParams: {
                    place: undefined
                }
            })).toEqual(' data-statlog="path"');
        });

        test('пустая строка из пустого объекта', function() {
            expect(stat.getAttr('path', null, {
                logShow: false,
                customParams: {
                    place: undefined
                }
            })).toEqual(' data-statlog="path"');
        });
    });

    describe('logShow', function() {
        let stat: Stat;
        let req: Req3ServerMocked;

        beforeEach(() => {
            req = mockReq({}, {
                LiveCartridge: 1,
                statRoot: 'root',
                ShowID: '1.2.3.4'
            });
            stat = makeStat(req);
        });

        test('возвращает значение', function() {
            expect(stat.logShow('path0')).toEqual('path0');
        });

        test('вызывает setCounter', function() {
            stat.logShow('path0');
            stat.logShow('path1');
            expect(req.setCounter.mock.calls).toMatchSnapshot();
        });
    });

    describe('getShows', function() {
        let stat: Stat;
        let req: Req3ServerMocked;

        beforeEach(() => {
            req = mockReq({}, {
                LiveCartridge: 1,
                statRoot: 'root',
                ShowID: '1.2.3.4'
            });
            stat = makeStat(req);
        });

        test('возвращает пустой массив с выключенной статистикой', function() {
            expect(stat.getShows()).toEqual([]);
            stat.logShow('abcde');
            expect(stat.getShows()).toEqual([]);
        });

        test('возвращает пустой массив с включённой статистикой и выключенным collect\'ом', function() {
            let stat = makeStat(req, { collect: false });
            expect(stat.getShows()).toEqual([]);
            stat.getAttr('abcde', null, { logShow: false });
            expect(stat.getShows()).toEqual([]);
            stat.getAttr('abcde', null, { logShow: true });
            expect(stat.getShows()).toEqual([]);
            stat.logShow('abcde2');
            expect(stat.getShows()).toEqual([]);
        });

        test('возвращает массив с включенной статистикой и включённым collect\'ом', function() {
            let stat = makeStat(req, { collect: true });
            expect(stat.getShows()).toEqual([]);
            stat.getAttr('abcde', null, { logShow: false });
            expect(stat.getShows()).toEqual([]);
            stat.getAttr('abcde', null, { logShow: true });
            expect(stat.getShows()).toEqual(['abcde']);
            stat.logShow('abcde2');
            expect(stat.getShows()).toEqual(['abcde', 'abcde2']);
        });
    });

    describe('apphost root', function() {
        test('В аппхосте тоже работает рут', function() {
            let stat = makeStat(mockReq({}, {
                statRoot: 'v14',
                LiveCartridge: 1,
                ShowID: '1.2.3.4'
            }));

            expect(stat.getRoot()).toEqual('v14');

            stat = makeStat(mockReq({}, {
                statRoot: 'v14',
                LiveCartridge: 0,
                ShowID: '1.2.3.4'
            }));

            expect(stat.getRoot()).toEqual('');
        });
    });
});
