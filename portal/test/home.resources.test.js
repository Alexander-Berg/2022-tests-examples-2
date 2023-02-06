/* eslint dot-notation: 0 */
describe('home.resources', function() {
    const mockFs = require('mock-fs');
    const path = require('path');

    var getFromCacheCopy;
    var homeErrorCopy;
    var getZCookieScriptCopy;

    if (!home.env) {
        home.env = {};
    }
    home.staticVersion = '1.234';

    var prepareResources = function (zCookie) {
        return new home.Resources('test', {
            getStaticURL: new home.GetStaticURL({
                s3root: 's3/default'
            }),
            isOperaWebKit: true,
            JSON: {
                common: {
                    zCookie: zCookie
                }
            },
            zCookie: zCookie,
            stat: {
                logShow: function () {}
            }
        }, function (name, data) {
            return name + ': ' + JSON.stringify(data).replace(/\\?"/g, "'") + ' ';
        });
    };

    before(function() {
        const fakeFlags = path.resolve(__dirname, '../../../test_flags.json');

        mockFs({
            [fakeFlags]: JSON.stringify({
            })
        });
        home.flags.setDesc('test_flags.json');

        if (!getFromCacheCopy) {
            getFromCacheCopy = home.getFromCache;
        }
        if (!homeErrorCopy) {
            homeErrorCopy = home.error;
        }
        if (!getZCookieScriptCopy) {
            getZCookieScriptCopy = home.Resources.getZCookieScript;
        }
        home.getFromCache = function (path) {
            var paths = {
                '/dev/test.js': 'INNERTEXT, path=/dev/test.js)',
                '/common/test.js': 'INNERTEXT, path=/common/test.js)'
            };

            if (path in paths) {
                return paths[path];
            }
        };
        home.error = function (msg) {
            throw new Error(msg);
        };
        home.Resources.getZCookieScript = function () {
            return 'zCookie-script ';
        };
    });

    after(function() {
        mockFs.restore();

        home.getFromCache = getFromCacheCopy;
        home.error = homeErrorCopy;
        home.Resources.getZCookieScript = getZCookieScriptCopy;
        home.env.devInstance = undefined;
        home.env.externalStatic = undefined;
    });

    describe('inline вставка файлов', function () {
        var resources;
        beforeEach(function () {
            resources = new home.Resources('dev', {
                JSON: {},
                getStaticURL: new home.GetStaticURL({
                    s3root: 's3/default'
                })
            }, function (name, data) {
                return JSON.stringify(data);
            });
        });

        it('добавляет inline файлы в группе с inlineAlt', function() {
            resources.add('/test.js', 'js', {inline: true});

            resources.getHTML('ready-scripts').should.equal('{"content":"INNERTEXT, path=/dev/test.js)"}');

            resources.end();
        });

        it('добавляет inline файлы в группе без inlineAlt и с isUrl:true', function() {
            resources.add('/test.js', 'delayed-css', {inline: true});

            resources.getHTML('body').should.equal('{"url":"INNERTEXT, path=/dev/test.js)"}');

            resources.end();
        });

        it('добавляет inline файлы в группе с inlineAlt, isUrl:true и префиксом', function() {
            resources.add('/test.js', 'js', {inline: true, prefix: 'common'});

            resources.getHTML('ready-scripts').should.equal('{"content":"INNERTEXT, path=/common/test.js)"}');

            resources.end();
        });

        it('при попытке добавить inline файл с левым путем - пишем ошибку', function() {
            resources.add('/nonexisting.js', 'js', {inline: true});

            (function () {
                resources.getHTML('ready-scripts');
            }).should.throws(Error, 'File not found or empty: dev/nonexisting.js');

            resources.end();
        });
    });

    describe('в dev-окружении', function() {
        var resources;
        before(function() {
            home.env.devInstance = true;
            home.env.externalStatic = false;
        });

        beforeEach(function () {
            resources = new home.Resources('dev', {
                JSON: {},
                getStaticURL: new home.GetStaticURL({
                    s3root: 's3/default'
                })
            }, function (name, data) {
                return JSON.stringify(data);
            });
        });

        it('добавляет ссылки с относительными урлами', function() {
            resources.add('/test', 'js');
            resources.getHTML('ready-scripts').should.equal('{"content":"/tmpl/dev/test"}');
            resources.end();
        });

        it('добавляет ссылки с абсолютными урлами', function() {
            resources.add('//test', 'js');
            resources.getHTML('ready-scripts').should.equal('{"content":"//test"}');
            resources.end();
        });

        it('добавляет несколько ресурсов', function() {
            resources.add('/test', 'js');
            resources.add('/test2', 'js');
            resources.add('/test3', 'css');

            resources.getHTML('head').should.equal('{"href":"/tmpl/dev/test3"}');
            resources.getHTML('ready-scripts').should.equal('{"content":"/tmpl/dev/test"}{"content":"/tmpl/dev/test2"}');
            resources.end();
        });

        it('добавляет ресурсы с кастомным префиксом', function() {
            resources.add('/test', 'js', {prefix: 'prefix'});
            resources.getHTML('ready-scripts').should.equal('{"content":"/tmpl/prefix/test"}');
            resources.end();
        });

        it('добавляет ресурсы с кастомным getStaticURL', function () {
            resources.add('/test', 'js', {
                getStaticURL: new home.GetStaticURL({
                    devHost: '//qwe.rty',
                    s3root: 's3/default'
                })
            });
            resources.getHTML('ready-scripts').should.equal('{"content":"//qwe.rty/tmpl/dev/test"}');
            resources.end();
        });
    });

    describe('в production-окружении', function() {
        var resources;
        before(function() {
            home.env.devInstance = false;
            home.env.externalStatic = true;
        });

        beforeEach(function () {
            resources = new home.Resources('dev', {
                JSON: {},
                getStaticURL: new home.GetStaticURL({
                    s3root: 's3/default'
                })
            }, function (name, data) {
                return JSON.stringify(data);
            });
        });

        it('добавляет ссылки с относительными урлами - ведут на статику', function() {
            resources.add('/test', 'js');
            resources.getHTML('ready-scripts').should.equal('{"content":"//yastatic.net/s3/default/1.234/dev/test"}');
            resources.end();
        });

        it('добавляет ссылки с абсолютными урлами - поведение не отличается от dev-окружения', function() {
            resources.add('//test', 'js');
            resources.getHTML('ready-scripts').should.equal('{"content":"//test"}');
            resources.end();
        });

        it('добавляет несколько ресурсов, ведет на статику', function() {
            resources.add('/test', 'js');
            resources.add('/test2', 'js');
            resources.add('/test3', 'css');

            resources.getHTML('head').should.equal('{"href":"//yastatic.net/s3/default/1.234/dev/test3"}');
            resources.getHTML('ready-scripts').should.equal('{"content":"//yastatic.net/s3/default/1.234/dev/test"}{"content":"//yastatic.net/s3/default/1.234/dev/test2"}');
            resources.end();
        });

        it('добавляет ресурсы с кастомным префиксом, ведет на статику', function() {
            resources.add('/test', 'js', {prefix: 'prefix'});
            resources.getHTML('ready-scripts').should.equal('{"content":"//yastatic.net/s3/default/1.234/prefix/test"}');
            resources.end();
        });

        it('добавляет ресурсы с кастомным getStaticURL', function () {
            resources.add('/test', 'js', {
                getStaticURL: new home.GetStaticURL({
                    s3root: 'qqq',
                    version: '2.0'
                })
            });
            resources.getHTML('ready-scripts').should.equal('{"content":"//yastatic.net/qqq/2.0/dev/test"}');
            resources.end();
        });
    });

    it('сортирует ресурсы', function() {
        var resources = new home.Resources('dev', {
            JSON: {},
            getStaticURL: new home.GetStaticURL({
                s3root: 's3/default'
            })
        }, function (name, data) {
            return JSON.stringify(data);
        });

        resources.add('inline-js', 'inline-js');
        resources.add('test', 'css');
        resources.getHTML('head');
        resources.add('inline-html', 'inline-html');

        resources.getHTML('body').should.equal('{"html":"inline-html"}{"content":"inline-js"}');
        resources.end();
    });

    describe('getResourcesByGroup', function() {
        var resources;

        beforeEach(function () {
            resources = new home.Resources('dev', {
                JSON: {},
                getStaticURL: new home.GetStaticURL({
                    s3root: 's3/default'
                })
            }, function (name, data) {
                return JSON.stringify(data);
            });
        });

        it('возвращает список ресурсов по группам', function() {
            var resourcesList = ['test1.css', 'test2.css'];

            resourcesList.forEach(function (resource) {
                resources.add(resource, 'css');
            });

            resourcesList.forEach(function (resource, i) {
                resources.getResourcesByGroup('css')[i]['url'].should.equal('//yastatic.net/s3/default/1.234/dev/' + resource);
            });
        });

        it('преобразует относительные урлы', function() {
            resources.add('test.css', 'css');

            resources.getResourcesByGroup('css')[0]['url'].should.equal('//yastatic.net/s3/default/1.234/dev/test.css');
        });

        it('не преобразует абсолютные урлы', function() {
            resources.add('http://path.to/remote/test.css', 'css');

            resources.getResourcesByGroup('css')[0]['url'].should.equal('http://path.to/remote/test.css');
        });
    });

    it('пропусает дубликаты ресурсов', function() {
        var resources = new home.Resources('dev', {
            JSON: {},
            getStaticURL: new home.GetStaticURL({
                s3root: 's3/default'
            })
        }, function (name, data) {
            return JSON.stringify(data);
        });

        resources.add('/test.css', 'css');
        resources.add('/test.css', 'css');
        resources.add('/test.js', 'css');
        resources.add('/test.js', 'js');
        resources.add('/test.js', 'js');
        resources.add('inline text', 'inline-js');
        resources.add('/test.js', 'js', {prefix: 'elsewhere'});

        resources.getHTML('head')
            .should.equal('{"href":"//yastatic.net/s3/default/1.234/dev/test.css"}{"href":"//yastatic.net/s3/default/1.234/dev/test.js"}');

        resources.add('/test.js', 'js');
        resources.add('inline text', 'inline-js');
        resources.add('inline text', 'inline-js', {uniqId: '12345'});
        resources.add('inline text', 'inline-js', {uniqId: '12345'});

        resources.getHTML('body').should.equal('{"content":"inline text"}{"content":"inline text"}{"content":"inline text"}');

        resources.getHTML('ready-scripts').should.equal('{"content":"//yastatic.net/s3/default/1.234/elsewhere/test.js"}');

        resources.end();
    });

    describe('zCookie', function() {
        before(function() {
            home.env.useCache = true;
            home.getFromCache = function (path) {
                return '{"file contents": "' + path + '"} ';
            };
        });

        describe('свежая кука', function() {
            describe('один ресурс', function() {
                var resources = prepareResources('m-testtest.css:1.234:l');

                resources.add('/test.css', 'css', {useCache: true});

                it('кэшер и его данные помещены в head', function() {
                    resources.getHTML('head').should.equal("Script: {'content':'zCookie-script resources__ls__init: " +
                        "{'files':'{'testtest.css':{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css'," +
                            "'version':'1.234','name':'testtest.css','fresh':true,'size':36,'hash':'-rsx7hw'}}'" +
                        "} '} " +
                        "<noscript>LinkHref: {'href':'//yastatic.net/s3/default/1.234/test/test.css'} </noscript>");
                });

                it('в ready-scripts пусто', function() {
                    resources.getHTML('ready-scripts').should.equal('');
                });

                it('в body пусто', function() {
                    resources.getHTML('body').should.equal('');
                });
            });
            describe('css и ресурс с useCache: false', function () {
                var resources = prepareResources('m-testtest.css:1.234:l');

                resources.add('/test.css', 'css', {useCache: true});
                resources.add('/test2.css', 'css');

                it('кэшер, его данные и ссылка на не кешируемый ресурс помещены в head', function() {
                    resources.getHTML('head')
                        .should.equal("Script: {'content':'zCookie-script resources__ls__init: " +
                        "{'files':'{'testtest.css':{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css'," +
                            "'version':'1.234','name':'testtest.css','fresh':true,'size':36,'hash':'-rsx7hw'}}'" +
                        "} '} " +
                        "<noscript>LinkHref: {'href':'//yastatic.net/s3/default/1.234/test/test.css'} </noscript>" +
                        "LinkHref: {'href':'//yastatic.net/s3/default/1.234/test/test2.css'} ");
                });

                it('в ready-scripts пусто', function() {
                    resources.getHTML('ready-scripts').should.equal('');
                });

                it('в body пусто', function() {
                    resources.getHTML('body').should.equal('');
                });
            });
        });

        describe('протухшая кука', function() {
            var resources = prepareResources('m-testtest.css:1.233:l');

            resources.add('/test.css', 'css', {useCache: true});

            it('в head помещён инлайн ресурс', function() {
                resources.getHTML('head')
                    .should.equal("Style: {'content':'{'file contents': '/test/test.css'} ','attrs':{'data-css-name':'testtest.css'}} ");
            });

            it('в ready-scripts помещена ссылка на кэшер', function() {
                resources.getHTML('ready-scripts')
                    .should.equal("ScriptSrc: {'content':'//yastatic.net/s3/default/1.234/common/zCookie/_zCookie3.inline.js'} ");
            });

            it('в body помещены данные кэшера', function() {
                resources.getHTML('body')
                    .should.equal("Script: {'content':'resources__ls__init: {'files':'{'testtest.css':" +
                    "{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css','version':'1.234','name':'testtest.css','fresh':false,'size':36,'hash':'-rsx7hw'}}'" +
                    "} '} ");
            });
        });

        describe('без куки', function() {
            describe('один ресурс', function() {
                var resources = prepareResources('');
                resources.add('/test.css', 'css', {useCache: true});

                it('в head помещён инлайн ресурс', function() {
                    resources.getHTML('head')
                        .should.equal("Style: {'content':'{'file contents': '/test/test.css'} ','attrs':{'data-css-name':'testtest.css'}} ");
                });

                it('в ready-scripts помещена ссылка на кэшер', function() {
                    resources.getHTML('ready-scripts')
                        .should.equal("ScriptSrc: {'content':'//yastatic.net/s3/default/1.234/common/zCookie/_zCookie3.inline.js'} ");
                });

                it('в body помещены данные кэшера', function() {
                    resources.getHTML('body')
                        .should.equal("Script: {'content':'resources__ls__init: {'files':'{'testtest.css':" +
                        "{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css','version':'1.234','name':'testtest.css','fresh':false,'size':36,'hash':'-rsx7hw'}}'" +
                        "} '} ");
                });
            });

            describe('css и inline-css', function() {
                var resources = prepareResources('');

                resources.add('/test.css', 'css', {useCache: true});
                resources.add('.class{width: 30px;}', 'inline-css');

                it('в head заинлайнены оба ресурса', function() {
                    resources.getHTML('head')
                        .should.equal("Style: {'content':'{'file contents': '/test/test.css'} ','attrs':{'data-css-name':'testtest.css'}} " +
                        "Style: {'content':'.class{width: 30px;}'} ");
                });

                it('в ready-scripts помещена ссылка на кэшер', function() {
                    resources.getHTML('ready-scripts')
                        .should.equal("ScriptSrc: {'content':'//yastatic.net/s3/default/1.234/common/zCookie/_zCookie3.inline.js'} ");
                });

                it('в body помещены данные кэшера', function() {
                    resources.getHTML('body')
                        .should.equal("Script: {'content':'resources__ls__init: {'files':'{'testtest.css':" +
                        "{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css','version':'1.234','name':'testtest.css','fresh':false,'size':36,'hash':'-rsx7hw'}}'" +
                        "} '} ");
                });
            });

            describe('css и ресурс с useCache: false', function () {
                var resources = prepareResources('');

                resources.add('/test.css', 'css', {useCache: true});
                resources.add('/test2.css', 'css');

                it('в head заинлайнен кешируемый ресурс и ссылка на не кешируемый', function() {
                    resources.getHTML('head')
                        .should.equal("Style: {'content':'{'file contents': '/test/test.css'} ','attrs':{'data-css-name':'testtest.css'}}" +
                        " LinkHref: {'href':'//yastatic.net/s3/default/1.234/test/test2.css'} ");
                });

                it('в ready-scripts помещена ссылка на кэшер', function() {
                    resources.getHTML('ready-scripts')
                        .should.equal("ScriptSrc: {'content':'//yastatic.net/s3/default/1.234/common/zCookie/_zCookie3.inline.js'} ");
                });

                it('в body помещены данные кэшера', function() {
                    resources.getHTML('body')
                        .should.equal("Script: {'content':'resources__ls__init: {'files':" +
                        "'{'testtest.css':{'url':'//yastatic.net/s3/default/1.234/test/test.css','type':'css'," +
                            "'version':'1.234','name':'testtest.css','fresh':false,'size':36,'hash':'-rsx7hw'}}'" +
                        "} '} ");
                });
            });
        });

        describe('кэш отключен (useCache: false)', function() {
            var resources = prepareResources('');

            resources.add('/test.css', 'css');

            it('в head помещёна ссылка', function() {
                resources.getHTML('head')
                    .should.equal("LinkHref: {'href':'//yastatic.net/s3/default/1.234/test/test.css'} ");
            });

            it('в ready-scripts пусто', function() {
                resources.getHTML('ready-scripts').should.equal('');
            });

            it('в body пусто', function() {
                resources.getHTML('body').should.equal('');
            });
        });

        describe('кэш отключен, инлайн включен (useCache: false, inline: true)', function() {
            var resources = prepareResources('');

            resources.add('/test.css', 'css', {inline: true});

            it('в head помещён инлайн ресурс', function() {
                resources.getHTML('head')
                    .should.equal("Style: {'content':'{'file contents': '/test/test.css'} '} ");
            });

            it('в ready-scripts пусто', function() {
                resources.getHTML('ready-scripts').should.equal('');
            });

            it('в body пусто', function() {
                resources.getHTML('body').should.equal('');
            });
        });
    });

    describe('getHTML', function() {
        var resources;

        beforeEach(function () {
            resources = new home.Resources('dev', {
                JSON: {},
                getStaticURL: new home.GetStaticURL({
                    s3root: 's3/default'
                })
            }, function (name, data) {
                return JSON.stringify(data);
            });
        });

        it('запрещает добавлять ресурсы после рендера', function() {
            resources.add('/test', 'js');

            resources.getHTML('ready-scripts').should.equal('{"content":"//yastatic.net/s3/default/1.234/dev/test"}');

            (function () {
                resources.add('/test2', 'js');
                resources.end();
            }).should.throw();
        });

        describe('all', function() {
            before(function() {
                home.env.useCache = true;
                home.getFromCache = function (path) {
                    return '{"file contents": "' + path + '"} ';
                };
            });

            it('возвращает контент', function() {
                resources.add('/test', 'js');

                resources.getHTML('all').should.equal('{"content":"//yastatic.net/s3/default/1.234/dev/test"}');

                resources.end();
            });

            it('возвращает контент из разных мест', function() {
                resources.add('inline-js', 'inline-js');
                resources.add('/test.js', 'js');
                resources.add('test.css', 'css');
                resources.add('inline-html', 'inline-html');

                resources.getHTML('all')
                    .should.equal('{"href":"//yastatic.net/s3/default/1.234/dev/test.css"}{"html":"inline-html"}' +
                        '{"content":"inline-js"}{"content":"//yastatic.net/s3/default/1.234/dev/test.js"}');

                resources.end();
            });

            describe('useCache: false, inline: true', function() {
                var resources = prepareResources('');

                resources.add('/test.css', 'css', {inline: true});

                it('размещает контент в head', function() {
                    resources.getHTML('all')
                        .should.equal("Style: {'content':'{'file contents': '/test/test.css'} '} ");
                });

                it('оставляет пустым ready-scripts', function() {
                    resources.getHTML('ready-scripts').should.equal('');
                });

                it('оставляет пустым body', function() {
                    resources.getHTML('body').should.equal('');
                });
            });
        });
    });

    describe('бандлы', function () {
        var sandbox,
            resources,
            depsTree = {
                get: function (list) {
                    return 'depsTree:' + list;
                },
                postpone: function () {}
            };
        beforeEach(function () {
            sandbox = sinon.createSandbox();
            sandbox.spy(depsTree, 'get');
            sandbox.spy(depsTree, 'postpone');
            home.env.devInstance = false;
            home.env.externalStatic = true;
            home.env.inlineCss = true;

            resources = new home.Resources('test', {
                depsTree,
                JSON: {},
                getStaticURL: new home.GetStaticURL({
                    s3root: 's3/default'
                })
            }, function (name, data) {
                return JSON.stringify(data);
            });
            resources.setupBundles({
                locale: 'ru',
                page: 'page',
                pagesDir: 'dir'
            });

            sandbox.stub(resources, 'getBundleDeps').returns(['dep1', 'dep2']);
        });

        afterEach(function () {
            home.env.inlineCss = false;
            sandbox.restore();
        });

        describe('addBundle', function () {
            it('инлайнит бандл', function () {
                var html = resources.addBundle('bar');
                html.should.equal('{"content":"depsTree:dep1,dep2{\\"file contents\\": \\"test/dir/page__bar/_page__bar.css\\"} "}');
                resources.getHTML('head').should.equal('');
                resources.getHTML('body').should.equal('');
                resources.getHTML('ready-scripts').should.deep.equal('{"content":"{\\"file contents\\": \\"/test/dir/page__bar/_page__bar.ru.js\\"} "}');
                depsTree.get.should.be.calledOnce;
                depsTree.postpone.should.not.be.called;
            });

            it('позволяет не инлайнить бандл', function () {
                var html = resources.addBundle('bar', {inlineJs: false, inlineCss: false});
                html.should.equal('{"href":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.css"}');
                resources.getHTML('head').should.equal('');
                resources.getHTML('body').should.equal('');
                resources.getHTML('ready-scripts').should.deep.equal('{"content":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.ru.js"}');
                depsTree.get.should.not.be.called;
                depsTree.postpone.should.be.calledOnce;
                depsTree.postpone.should.be.deep.calledWith(['dep1', 'dep2']);
            });

            it('запрещает добавлять бандл дважды', function () {
                resources.addBundle('bar');
                resources.addBundle('baz');

                (function () {
                    resources.addBundle('bar');
                }).should.throw();
            });

            it('добавляяет суффиксы', function () {
                resources.setupBundles({
                    locale: 'ru',
                    page: 'page',
                    pagesDir: 'dir',
                    jsSuffix: '.qwe',
                    cssSuffix: '.ewq'
                });

                var html = resources.addBundle('bar', {inlineJs: false, inlineCss: false});
                html.should.equal('{"href":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.ewq.css"}');
                resources.getHTML('head').should.equal('');
                resources.getHTML('body').should.equal('');
                resources.getHTML('ready-scripts').should.deep.equal('{"content":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.ru.qwe.js"}');
            });

            describe('не использует depsTree, если inlineCss == false', function () {
                beforeEach(function () {
                    home.env.inlineCss = false;
                });

                it('не инлайниn бандл с указанием отключения инлайна в опциях', function () {
                    var html = resources.addBundle('bar', {inlineJs: false, inlineCss: false});
                    html.should.equal('{"href":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.css"}');
                    resources.getHTML('head').should.equal('');
                    resources.getHTML('body').should.equal('');
                    resources.getHTML('ready-scripts').should.deep.equal('{"content":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.ru.js"}');
                    depsTree.get.should.not.be.called;
                    depsTree.postpone.should.not.be.called;
                });

                it('не инлайнит бандл без указания инлайна в опциях', function () {
                    var html = resources.addBundle('bar');
                    html.should.equal('{"href":"//yastatic.net/s3/default/1.234/test/dir/page__bar/_page__bar.css"}');
                    resources.getHTML('head').should.equal('');
                    resources.getHTML('body').should.equal('');
                    resources.getHTML('ready-scripts').should.deep.equal('{"content":"{\\"file contents\\": \\"/test/dir/page__bar/_page__bar.ru.js\\"} "}');
                    depsTree.get.should.not.be.called;
                    depsTree.postpone.should.not.be.called;
                });

            });
        });
    });

});
