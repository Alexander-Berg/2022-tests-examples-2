import { MockedInterface, mockReq } from '@lib/views/mockReq';
import { DepsTree } from '@lib/utils/depsTree';
import { logError } from '@lib/log/logError';
import { getFromCache } from '@lib/utils/include';
import { Resources } from '../resources';
import { GetStaticURL } from '../getStaticURL';

jest.mock('../../log/logError.ts', () => {
    return {
        logError: jest.fn().mockImplementation(() => {
            throw new Error('logError called!');
        })
    };
});
const mockedLogError = logError as jest.Mock;
jest.mock('../include.ts', () => {
    return {
        serverInclude: () => '',
        getFromCache: jest.fn()
    };
});
const mockedGetFromCache = getFromCache as jest.Mock;

describe('resources', function() {
    function prepareResources(zCookie?: string) {
        let res = new Resources('test', mockReq({}, {
            zCookie,
            isOperaWebKit: 1,
            getStaticURL: new GetStaticURL({
                s3root: 's3/default'
            })
        }), function(name: string, data: unknown) {
            return name + ': ' + JSON.stringify(data).replace(/\\?"/g, "'") + ' ';
        } as ExecViewCompat);

        jest.spyOn(Resources, 'getZCookieScript').mockReturnValue('zCookie-script ');

        return res;
    }

    beforeEach(() => {
        // todo Избавиться
        home.staticVersion = '1.234';

        mockedGetFromCache.mockImplementation((path: string) => {
            let paths = {
                '/dev/test.js': 'INNERTEXT, path=/dev/test.js)',
                '/common/test.js': 'INNERTEXT, path=/common/test.js)'
            };

            if (path in paths) {
                return paths[path as keyof typeof paths];
            }
            return '';
        });
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('inline вставка файлов', function() {
        let resources: Resources;

        beforeEach(() => {
            resources = new Resources('dev', mockReq(), function(name: string, data: unknown) {
                return JSON.stringify(data);
            } as ExecViewCompat);
        });

        test('добавляет inline файлы в группе с inlineAlt', function() {
            resources.add('/test.js', 'js', { inline: true });

            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"INNERTEXT, path=/dev/test.js)"}');

            resources.end();
        });

        test('добавляет inline файлы в группе без inlineAlt и с isUrl:true', function() {
            resources.add('/test.js', 'delayed-css', { inline: true });

            expect(resources.getHTML('body')).toEqual('{"url":"INNERTEXT, path=/dev/test.js)"}');

            resources.end();
        });

        test('добавляет inline файлы в группе с inlineAlt, isUrl:true и префиксом', function() {
            resources.add('/test.js', 'js', { inline: true, prefix: 'common' });

            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"INNERTEXT, path=/common/test.js)"}');

            resources.end();
        });

        test('при попытке добавить inline файл с левым путем - пишем ошибку', function() {
            mockedLogError.mockImplementation(() => {});

            resources.add('/nonexisting.js', 'js', { inline: true });

            resources.getHTML('ready-scripts');

            expect(mockedLogError.mock.calls).toMatchSnapshot();

            resources.end();
        });
    });

    describe('в dev-окружении', function() {
        let resources: Resources;

        beforeAll(() => {
            home.env.devInstance = true;
            home.env.externalStatic = false;
        });

        beforeEach(function() {
            resources = new Resources('dev', mockReq(), function(name: string, data: unknown) {
                return JSON.stringify(data);
            } as ExecViewCompat);
        });

        test('добавляет ссылки с относительными урлами', function() {
            resources.add('/test', 'js');
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"/tmpl/dev/test"}');
            resources.end();
        });

        test('добавляет ссылки с абсолютными урлами', function() {
            resources.add('//test', 'js');
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//test"}');
            resources.end();
        });

        test('добавляет несколько ресурсов', function() {
            resources.add('/test', 'js');
            resources.add('/test2', 'js');
            resources.add('/test3', 'css');

            expect(resources.getHTML('head')).toEqual('{"href":"/tmpl/dev/test3"}');
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"/tmpl/dev/test"}{"content":"/tmpl/dev/test2"}');
            resources.end();
        });

        test('добавляет ресурсы с кастомным префиксом', function() {
            resources.add('/test', 'js', { prefix: 'prefix' });
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"/tmpl/prefix/test"}');
            resources.end();
        });

        test('добавляет ресурсы с кастомным getStaticURL', function() {
            resources.add('/test', 'js', {
                getStaticURL: new GetStaticURL({
                    devHost: '//qwe.rty',
                    s3root: 's3/default'
                })
            });
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//qwe.rty/tmpl/dev/test"}');
            resources.end();
        });
    });

    describe('в production-окружении', function() {
        let resources: Resources;

        beforeAll(function() {
            home.env.devInstance = false;
            home.env.externalStatic = true;
        });

        beforeEach(function() {
            resources = new Resources('dev', mockReq(), function(name: string, data: unknown) {
                return JSON.stringify(data);
            } as ExecViewCompat, new GetStaticURL({
                s3root: 's3/default'
            }));
        });

        test('добавляет ссылки с относительными урлами - ведут на статику', function() {
            resources.add('/test', 'js');
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//yastatic.net/s3/default/1.234/dev/test"}');
            resources.end();
        });

        test('добавляет ссылки с абсолютными урлами - поведение не отличается от dev-окружения', function() {
            resources.add('//test', 'js');
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//test"}');
            resources.end();
        });

        test('добавляет несколько ресурсов, ведет на статику', function() {
            resources.add('/test', 'js');
            resources.add('/test2', 'js');
            resources.add('/test3', 'css');

            expect(resources.getHTML('head')).toEqual('{"href":"//yastatic.net/s3/default/1.234/dev/test3"}');
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//yastatic.net/s3/default/1.234/dev/test"}{"content":"//yastatic.net/s3/default/1.234/dev/test2"}');
            resources.end();
        });

        test('добавляет ресурсы с кастомным префиксом, ведет на статику', function() {
            resources.add('/test', 'js', { prefix: 'prefix' });
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//yastatic.net/s3/default/1.234/prefix/test"}');
            resources.end();
        });

        test('добавляет ресурсы с кастомным getStaticURL', function() {
            resources.add('/test', 'js', {
                getStaticURL: new GetStaticURL({
                    s3root: 'qqq',
                    version: '2.0'
                })
            });
            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//yastatic.net/qqq/2.0/dev/test"}');
            resources.end();
        });
    });

    test('сортирует ресурсы', function() {
        let resources = new Resources('dev', mockReq(), function(name: string, data: unknown) {
            return JSON.stringify(data);
        } as ExecViewCompat);

        resources.add('inline-js', 'inline-js');
        resources.add('test', 'css');
        resources.getHTML('head');
        resources.add('inline-html', 'inline-html');

        expect(resources.getHTML('body')).toEqual('{"html":"inline-html"}{"content":"inline-js"}');
        resources.end();
    });

    describe('getResourcesByGroup', function() {
        let resources: Resources;

        beforeEach(function() {
            resources = new Resources('dev', mockReq(), function(name: string, data: unknown) {
                return JSON.stringify(data);
            } as ExecViewCompat, new GetStaticURL({
                s3root: 's3/default'
            }));
        });

        test('возвращает список ресурсов по группам', function() {
            let resourcesList = ['test1.css', 'test2.css'];

            resourcesList.forEach(function(resource) {
                resources.add(resource, 'css');
            });

            resourcesList.forEach(function(resource, i) {
                expect(resources.getResourcesByGroup('css')[i].url).toEqual('//yastatic.net/s3/default/1.234/dev/' + resource);
            });
        });

        test('преобразует относительные урлы', function() {
            resources.add('test.css', 'css');

            expect(resources.getResourcesByGroup('css')[0].url).toEqual('//yastatic.net/s3/default/1.234/dev/test.css');
        });

        test('не преобразует абсолютные урлы', function() {
            resources.add('http://path.to/remote/test.css', 'css');

            expect(resources.getResourcesByGroup('css')[0].url).toEqual('http://path.to/remote/test.css');
        });
    });

    test('пропусает дубликаты ресурсов', function() {
        let resources = new Resources('dev', mockReq(), function(name: string, data: unknown) {
            return JSON.stringify(data);
        } as ExecViewCompat, new GetStaticURL({
            s3root: 's3/default'
        }));

        resources.add('/test.css', 'css');
        resources.add('/test.css', 'css');
        resources.add('/test.js', 'css');
        resources.add('/test.js', 'js');
        resources.add('/test.js', 'js');
        resources.add('inline text', 'inline-js');
        resources.add('/test.js', 'js', { prefix: 'elsewhere' });

        expect(resources.getHTML('head'))
            .toEqual('{"href":"//yastatic.net/s3/default/1.234/dev/test.css"}{"href":"//yastatic.net/s3/default/1.234/dev/test.js"}');

        resources.add('/test.js', 'js');
        resources.add('inline text', 'inline-js');
        resources.add('inline text', 'inline-js', { uniqId: '12345' });
        resources.add('inline text', 'inline-js', { uniqId: '12345' });

        expect(resources.getHTML('body')).toEqual('{"content":"inline text"}{"content":"inline text"}{"content":"inline text"}');

        expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//yastatic.net/s3/default/1.234/elsewhere/test.js"}');

        resources.end();
    });

    describe('zCookie', function() {
        beforeEach(function() {
            home.env.useCache = true;
            home.env.externalStatic = true;
            mockedGetFromCache.mockImplementation((path: string) => {
                return '{"file contents": "' + path + '"} ';
            });
        });

        describe('свежая кука', function() {
            describe('один ресурс', function() {
                let resources: Resources;

                beforeEach(() => {
                    resources = prepareResources('m-testtest.css:1.234:l');
                    resources.add('/test.css', 'css', { useCache: true });
                });

                test('кэшер и его данные помещены в head', function() {
                    expect(resources.getHTML('head')).toMatchSnapshot();
                });

                test('в ready-scripts пусто', function() {
                    expect(resources.getHTML('ready-scripts')).toEqual('');
                });

                test('в body пусто', function() {
                    expect(resources.getHTML('body')).toEqual('');
                });
            });
            describe('css и ресурс с useCache: false', function() {
                let resources: Resources;

                beforeEach(() => {
                    resources = prepareResources('m-testtest.css:1.234:l');

                    resources.add('/test.css', 'css', { useCache: true });
                    resources.add('/test2.css', 'css');
                });

                test('кэшер, его данные и ссылка на не кешируемый ресурс помещены в head', function() {
                    expect(resources.getHTML('head')).toMatchSnapshot();
                });

                test('в ready-scripts пусто', function() {
                    expect(resources.getHTML('ready-scripts')).toEqual('');
                });

                test('в body пусто', function() {
                    expect(resources.getHTML('body')).toEqual('');
                });
            });
        });

        describe('протухшая кука', function() {
            let resources: Resources;

            beforeEach(() => {
                resources = prepareResources('m-testtest.css:1.233:l');

                resources.add('/test.css', 'css', { useCache: true });
            });

            test('в head помещён инлайн ресурс', function() {
                expect(resources.getHTML('head'))
                    .toEqual("Style: {'content':'{'file contents': '/test/test.css'} ','attrs':{'data-css-name':'testtest.css'}} ");
            });

            test('в ready-scripts помещена ссылка на кэшер', function() {
                expect(resources.getHTML('ready-scripts'))
                    .toEqual("ScriptSrc: {'content':'//yastatic.net/s3/default/1.234/common/zCookie/_zCookie3.inline.js'} ");
            });

            test('в body помещены данные кэшера', function() {
                expect(resources.getHTML('body'))
                    .toEqual("Script: {'content':'resources__ls__init: {'files':'{'testtest.css':" +
                    "{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css','version':'1.234','name':'testtest.css','fresh':false,'size':36,'hash':'-rsx7hw'}}'" +
                    "} '} ");
            });
        });

        describe('без куки', function() {
            describe('один ресурс', function() {
                let resources: Resources;

                beforeEach(() => {
                    resources = prepareResources('');

                    resources.add('/test.css', 'css', { useCache: true });
                });

                test('в head помещён инлайн ресурс', function() {
                    expect(resources.getHTML('head'))
                        .toEqual("Style: {'content':'{'file contents': '/test/test.css'} ','attrs':{'data-css-name':'testtest.css'}} ");
                });

                test('в ready-scripts помещена ссылка на кэшер', function() {
                    expect(resources.getHTML('ready-scripts'))
                        .toEqual("ScriptSrc: {'content':'//yastatic.net/s3/default/1.234/common/zCookie/_zCookie3.inline.js'} ");
                });

                test('в body помещены данные кэшера', function() {
                    expect(resources.getHTML('body'))
                        .toEqual("Script: {'content':'resources__ls__init: {'files':'{'testtest.css':" +
                        "{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css','version':'1.234','name':'testtest.css','fresh':false,'size':36,'hash':'-rsx7hw'}}'" +
                        "} '} ");
                });
            });

            describe('css и inline-css', function() {
                let resources: Resources;

                beforeEach(() => {
                    resources = prepareResources('');

                    resources.add('/test.css', 'css', { useCache: true });
                    resources.add('.class{width: 30px;}', 'inline-css');
                });

                test('в head заинлайнены оба ресурса', function() {
                    expect(resources.getHTML('head'))
                        .toEqual("Style: {'content':'{'file contents': '/test/test.css'} ','attrs':{'data-css-name':'testtest.css'}} " +
                        "Style: {'content':'.class{width: 30px;}'} ");
                });

                test('в ready-scripts помещена ссылка на кэшер', function() {
                    expect(resources.getHTML('ready-scripts'))
                        .toEqual("ScriptSrc: {'content':'//yastatic.net/s3/default/1.234/common/zCookie/_zCookie3.inline.js'} ");
                });

                test('в body помещены данные кэшера', function() {
                    expect(resources.getHTML('body'))
                        .toEqual("Script: {'content':'resources__ls__init: {'files':'{'testtest.css':" +
                        "{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css','version':'1.234','name':'testtest.css','fresh':false,'size':36,'hash':'-rsx7hw'}}'" +
                        "} '} ");
                });
            });

            describe('css и ресурс с useCache: false', function() {
                let resources: Resources;

                beforeEach(() => {
                    resources = prepareResources('');

                    resources.add('/test.css', 'css', { useCache: true });
                    resources.add('/test2.css', 'css');
                });

                test('в head заинлайнен кешируемый ресурс и ссылка на не кешируемый', function() {
                    expect(resources.getHTML('head'))
                        .toEqual("Style: {'content':'{'file contents': '/test/test.css'} ','attrs':{'data-css-name':'testtest.css'}}" +
                        " LinkHref: {'href':'//yastatic.net/s3/default/1.234/test/test2.css'} ");
                });

                test('в ready-scripts помещена ссылка на кэшер', function() {
                    expect(resources.getHTML('ready-scripts'))
                        .toEqual("ScriptSrc: {'content':'//yastatic.net/s3/default/1.234/common/zCookie/_zCookie3.inline.js'} ");
                });

                test('в body помещены данные кэшера', function() {
                    expect(resources.getHTML('body'))
                        .toEqual("Script: {'content':'resources__ls__init: {'files':" +
                        "'{'testtest.css':{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css'," +
                            "'version':'1.234','name':'testtest.css','fresh':false,'size':36,'hash':'-rsx7hw'}}'" +
                        "} '} ");
                });
            });
        });

        describe('кэш отключен (useCache: false)', function() {
            let resources: Resources;

            beforeEach(() => {
                resources = prepareResources('');

                resources.add('/test.css', 'css');
            });

            test('в head помещёна ссылка', function() {
                expect(resources.getHTML('head'))
                    .toEqual("LinkHref: {'href':'//yastatic.net/s3/default/1.234/test/test.css'} ");
            });

            test('в ready-scripts пусто', function() {
                expect(resources.getHTML('ready-scripts')).toEqual('');
            });

            test('в body пусто', function() {
                expect(resources.getHTML('body')).toEqual('');
            });
        });

        describe('кэш отключен, инлайн включен (useCache: false, inline: true)', function() {
            let resources: Resources;

            beforeEach(() => {
                resources = prepareResources('');

                resources.add('/test.css', 'css', { inline: true });
            });

            test('в head помещён инлайн ресурс', function() {
                expect(resources.getHTML('head'))
                    .toEqual("Style: {'content':'{'file contents': '/test/test.css'} '} ");
            });

            test('в ready-scripts пусто', function() {
                expect(resources.getHTML('ready-scripts')).toEqual('');
            });

            test('в body пусто', function() {
                expect(resources.getHTML('body')).toEqual('');
            });
        });
    });

    describe('getHTML', function() {
        let resources: Resources;

        beforeEach(function() {
            resources = new Resources('dev', mockReq({}, {
                getStaticURL: new GetStaticURL({
                    s3root: 's3/default'
                })
            }), function(name: string, data: unknown) {
                return JSON.stringify(data);
            } as ExecViewCompat);
        });

        test('запрещает добавлять ресурсы после рендера', function() {
            resources.add('/test', 'js');

            expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//yastatic.net/s3/default/1.234/dev/test"}');

            resources.add('/test2', 'js');
            /* eslint-disable-next-line @typescript-eslint/unbound-method */
            expect(resources.end).toThrow();
        });

        describe('all', function() {
            beforeEach(function() {
                home.env.useCache = true;
                mockedGetFromCache.mockImplementation((path: string) => {
                    return '{"file contents": "' + path + '"} ';
                });
            });

            test('возвращает контент', function() {
                resources.add('/test', 'js');

                expect(resources.getHTML('all')).toEqual('{"content":"//yastatic.net/s3/default/1.234/dev/test"}');

                resources.end();
            });

            test('возвращает контент из разных мест', function() {
                resources.add('inline-js', 'inline-js');
                resources.add('/test.js', 'js');
                resources.add('test.css', 'css');
                resources.add('inline-html', 'inline-html');

                expect(resources.getHTML('all'))
                    .toEqual('{"href":"//yastatic.net/s3/default/1.234/dev/test.css"}{"html":"inline-html"}' +
                        '{"content":"inline-js"}{"content":"//yastatic.net/s3/default/1.234/dev/test.js"}');

                resources.end();
            });

            describe('useCache: false, inline: true', function() {
                let resources: Resources;

                beforeEach(() => {
                    resources = prepareResources('');

                    resources.add('/test.css', 'css', { inline: true });
                });

                test('размещает контент в head', function() {
                    expect(resources.getHTML('all'))
                        .toEqual("Style: {'content':'{'file contents': '/test/test.css'} '} ");
                });

                test('оставляет пустым ready-scripts', function() {
                    expect(resources.getHTML('ready-scripts')).toEqual('');
                });

                test('оставляет пустым body', function() {
                    expect(resources.getHTML('body')).toEqual('');
                });
            });
        });
    });

    describe('бандлы', function() {
        let resources: Resources;
        let depsTree: MockedInterface<DepsTree>;

        beforeEach(function() {
            home.env.devInstance = false;
            home.env.externalStatic = true;
            home.env.inlineCss = true;

            depsTree = {
                get: jest.fn().mockImplementation((list: string) => {
                    return 'depsTree:' + list;
                }),
                buffer: jest.fn(),
                getUsed: jest.fn(),
                endBuffer: jest.fn(),
                getCommon: jest.fn(),
                listUsed: jest.fn(),
                _resolveDeps: jest.fn(),
                _resolveIntersection: jest.fn(),
                postpone: jest.fn(),
                getPostponed: jest.fn().mockReturnValue('')
            };

            resources = new Resources('test', mockReq({}, {
                depsTree,
                getStaticURL: new GetStaticURL({
                    s3root: 's3/default'
                })
            }), function(name: string, data: unknown) {
                return JSON.stringify(data);
            } as ExecViewCompat);
            resources.setupBundles({
                locale: 'ru',
                page: 'page',
                pagesDir: 'dir'
            });

            jest.spyOn(resources, 'getBundleDeps').mockReturnValue(['dep1', 'dep2']);

            mockedGetFromCache.mockImplementation((path: string) => {
                return '{"file contents": "' + path + '"} ';
            });
        });

        afterEach(function() {
            home.env.inlineCss = false;
        });

        describe('addBundle', function() {
            test('инлайнит бандл', function() {
                let html = resources.addBundle('bar');
                expect(html).toEqual('{"content":"depsTree:dep1,dep2{\\"file contents\\": \\"test/dir/page__bar/_page__bar.css\\"} "}');
                expect(resources.getHTML('head')).toEqual('');
                expect(resources.getHTML('body')).toEqual('');
                expect(resources.getHTML('ready-scripts')).toEqual('{"content":"{\\"file contents\\": \\"/test/dir/page__bar/_page__bar.ru.js\\"} "}');
                expect(depsTree.get.mock.calls).toHaveLength(1);
                expect(depsTree.postpone.mock.calls).toHaveLength(0);
            });

            test('позволяет не инлайнить бандл', function() {
                let html = resources.addBundle('bar', { inlineJs: false, inlineCss: false });
                expect(html).toEqual('{"href":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.css"}');
                expect(resources.getHTML('head')).toEqual('');
                expect(resources.getHTML('body')).toEqual('');
                expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.ru.js"}');
                expect(depsTree.get.mock.calls).toHaveLength(0);
                expect(depsTree.postpone.mock.calls).toMatchSnapshot();
            });

            test('запрещает добавлять бандл дважды', function() {
                resources.addBundle('bar');
                resources.addBundle('baz');

                expect(() => {
                    resources.addBundle('bar');
                }).toThrow();
            });

            test('добавляяет суффиксы', function() {
                resources.setupBundles({
                    locale: 'ru',
                    page: 'page',
                    pagesDir: 'dir',
                    jsSuffix: '.qwe',
                    cssSuffix: '.ewq'
                });

                let html = resources.addBundle('bar', { inlineJs: false, inlineCss: false });
                expect(html).toEqual('{"href":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.ewq.css"}');
                expect(resources.getHTML('head')).toEqual('');
                expect(resources.getHTML('body')).toEqual('');
                expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.ru.qwe.js"}');
            });

            describe('не использует depsTree, если inlineCss == false', function() {
                beforeEach(function() {
                    home.env.inlineCss = false;
                });

                test('не инлайниn бандл с указанием отключения инлайна в опциях', function() {
                    let html = resources.addBundle('bar', { inlineJs: false, inlineCss: false });
                    expect(html).toEqual('{"href":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.css"}');
                    expect(resources.getHTML('head')).toEqual('');
                    expect(resources.getHTML('body')).toEqual('');
                    expect(resources.getHTML('ready-scripts')).toEqual('{"content":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.ru.js"}');
                    expect(depsTree.get.mock.calls).toHaveLength(0);
                    expect(depsTree.postpone.mock.calls).toHaveLength(0);
                });

                test('не инлайнит бандл без указания инлайна в опциях', function() {
                    let html = resources.addBundle('bar');
                    expect(html).toEqual('{"href":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.css"}');
                    expect(resources.getHTML('head')).toEqual('');
                    expect(resources.getHTML('body')).toEqual('');
                    expect(resources.getHTML('ready-scripts')).toEqual('{"content":"{\\"file contents\\": \\"/test/dir/page__bar/_page__bar.ru.js\\"} "}');
                    expect(depsTree.get.mock.calls).toHaveLength(0);
                    expect(depsTree.postpone.mock.calls).toHaveLength(0);
                });
            });
        });
    });
});
