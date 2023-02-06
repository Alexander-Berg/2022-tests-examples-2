describe('home.views', function() {
    var testViews = home.getView(),
        execTestView = testViews.execView;

    it('игнорирует дубликаты', function() {
        testViews('test-duplicate', 'first definition');
        testViews('test-duplicate', 'second definition');

        execTestView('test-duplicate', {}).should.equal('first definition');
    });

    describe('наследование', function() {
        var view = home.getView();
        var execView = view.execView;
        var view2 = view.inherit();
        var execView2 = view2.execView;

        view('test-dev', 'test definition');

        view2('testSideEffect', 'ok');
        view2('ok', ': ok');

        it('использует базовые шаблоны', function() {
            execView2('test-dev', {}).should.equal('test definition');
        });

        it('не влияет на базовые шаблоны', function() {
            execView('testSideEffect', {}).should.equal('');

            view2('test-dev', 'test definition overloaded', true);

            execView('test-dev', {}).should.equal('test definition');
        });

        it('добавляет шаблон', function() {
            execView2('testSideEffect', {}).should.equal('ok');

            execView2('test-dev', {}).should.equal('test definition overloaded');
        });

        var data = {
            key0: 'value0',
            key1: 'value1'
        };
        view('template', '[% key0 %]');

        view('view-t0', '[% view2-t1 %]');

        view('view-t1', function (data, req, execView) {
            return execView('view2-t2', data);
        });

        view('view-a0', '[% view2-a0 %]');


        view2('template2', '[% key1 %]');

        view2('template3', function (data) {
            return data.key1;
        });

        view2('view2-t0', '[% view-t0 %]');

        view2('view2-t1', function (data, req, execView) {
            return execView('view-t1', data);
        });

        view2('view2-t2', function () {
            return 'test';
        });

        view2('view2-a0', '[% key1 %]');

        it('подставляет данные в шаблон', function() {
            execView('template', data).should.equal('value0');

            execView2('template2', data).should.equal('value1');

            execView2('template3', data).should.equal('value1');
        });

        it('позволяет вызывать шаблоны из всех уровней', function() {
            execView2('view2-t0', data).should.equal('test');

            execView2('view-a0', data).should.equal('value1');
        });
    });

    describe('langs', function() {
        it('изолирует языкозависимые шаблоны', function() {
            var view = home.getView(),
                execViewRu = view.createLang('ru').execView,
                execViewEn = view.createLang('en').execView;

            view('common-template', 'common');
            view.ru('template', 'doesn\'t include [% common-template %]');
            view.en('template2', 'doesn\'t include [% template %]');

            execViewRu('template', {}).should.equal('doesn\'t include ');

            execViewEn('template2', {}).should.equal('doesn\'t include ');
        });

        it('наследует шаблоны по языками', function() {
            var view = home.getView();
            view.createLang('ru');
            var view2 = view.inherit();
            var view2ru = view2.createLang('ru');
            var execView2 = view2.execView;
            var execView2Ru = view2.createLang('ru').execView;

            view('foo', 'common');
            view.ru('foo', 'ru template');

            view2('bar', 'includes [% foo %]');
            view2ru('bar', 'ru includes [% foo %]');

            execView2('bar', {}).should.equal('includes common');

            execView2Ru('bar', {}).should.equal('ru includes ru template');
        });
    });

    it('поддерживает шаблоны без результата', function() {
        var views = home.getView(),
            total = 0;

        views('test', function () {
            ++total;
        });

        views.execView('test', {}).should.equal('');
        total.should.equal(1);
    });

    it('выполняет связанные шаблоны', function() {
        var views = home.getView();

        views('test', 'abc [% test2 %]');

        views('test2', '123');

        views.execView('test', {}).should.equal('abc 123');
    });

    it('не игнорирует пустую строку в данных', function() {
        var views = home.getView();

        views('smth', 'template');

        views('usage', 'nothing[% smth %]between');

        views.execView('usage', {
            smth: ''
        }).should.equal('nothingbetween');
    });

    it('Допускает falsy значения как результат шаблона', function () {
        var views = home.getView();

        views('unicorns', function() {
            return 0;
        });

        views('say-prefix', 'There are [% exec:unicorns %] prefixed unicorns');
        views('say-noprefix', 'There are [% unicorns %] unicorns');

        views.execView('unicorns', {}).should.equal(0);
        views.execView('say-prefix', {}).should.equal('There are 0 prefixed unicorns');
        views.execView('say-noprefix', {}).should.equal('There are 0 unicorns');
    });

    it('Заменяет undefined значения', function () {
        var views = home.getView();

        views('void', function() {
            return;
        });

        views('say-prefix', 'prefixed:<[% exec:void %]>');
        views('say-noprefix', '<[% void %]>');

        views.execView('unicorns', {}).should.equal('');
        views.execView('say-prefix', {}).should.equal('prefixed:<>');
        views.execView('say-noprefix', {}).should.equal('<>');
    });

    describe('req объект', function() {
        var view = home.getView(),
            execView = view.execView;

        view('req-seeker-str', '[% req-seeker-func %] [% first %] [% second %]');

        view('req-seeker-func', function (data, req) {
            return data.first + ' and ' + req.first + req.second;
        });

        view('func-template', function (data, req, execView) {
            return execView('req-seeker-func', {
                first: 'baz'
            });
        });
        
        view('func-override', function(data, req, execView) {
            return execView('req-seeker-str', data, {
                first: 'override'
            });
        });
        
        it('не теряется при вызове из строкового шаблона', function() {
            execView('req-seeker-str', {
                first: 'foo',
                second: 'bar'
            }).should.equal('foo and foobar foo bar');
        });
        
        it('не теряется при вызове из шаблона-функции', function() {
            execView('func-template', {
                first: 'foo',
                second: 'bar'
            }).should.equal('baz and foobar');
        });

        it('переопределяется при первом вызове', function() {
            execView('req-seeker-str', {
                first: 'foo',
                second: 'bar'
            }, {
                first: 'baz',
                second: 'qwe'
            }).should.equal('foo and bazqwe foo bar');
        });

        it('переопределяется при вызове execView', function() {
            execView('func-override', {
                first: 'foo',
                second: 'bar'
            }).should.equal('foo and overrideundefined foo bar');
        });
    });

    it('может сгенерировать документ', function() {
        testViews('test-document',
            '<html class="b-page">[% test-head %][% test-body %]</html>');

        testViews('test-head',
            '<head>[% test-title %][% test-script__user-super_druper %]</head>');

        testViews('test-title',
            function () {
                return '<title>My title</title>';
            });

        testViews('test-body',
            '<body>[% hello %]</body>');

        testViews('test-body',
            '<body>[% hello %]</body>');

        testViews('test-script__user-super_druper', function () {});

        execTestView('test-document', {
            hello: 'привет',
            views: testViews
        }).should.equal('<html class="b-page"><head><title>My title</title></head><body>привет</body></html>');
    });

    describe('cached views', function() {
        var views = home.getView();

        views('sequence', '[% exec:aaa %],[% exec:aaa %],[% exec:aaa %]');

        views('aaa', function(data, req) {
            return 'parent' + (req.a + data.q) + '>';
        });


        it('не допускает использование строковых шаблонов', function() {
            var child = views.inherit();

            (function() {
                child.cached('aaa', 'bla [% req:HomePageNoArgs %]');
            }).should.throw(TypeError);
        });


        it('изолирует разные сессии', function() {
            var child = views.inherit(),
                cachedView = child.cached,
                execView = child.execView,
                ruCachedView = child.createLang('ru').cached,
                ruExecView = child.getLang('ru').execView,
                times = 0;

            cachedView('aaa', function(req) {
                times++;
                return 'a!' + req.a;
            });

            execView('aaa', {a: 42}).should.equal('a!42');
            times.should.equal(1);

            execView('aaa', {a: 11}).should.equal('a!11');
            times.should.equal(2);


            times = 0;
            ruCachedView('aaa', function(req) {
                times++;
                return 'ru a!' + req.a;
            });

            ruExecView('aaa', {a: 42}).should.equal('ru a!42');
            times.should.equal(1);

            ruExecView('aaa', {a: 11}).should.equal('ru a!11');
            times.should.equal(2);
        });

        it('кэширует результат', function() {
            var child = views.inherit(),
                cachedView = child.cached,
                execView = child.execView,
                times = 0;

            cachedView('aaa', function(req) {
                times++;
                return 'a!' + req.a;
            });

            execView('sequence', {a: 42}).should.equal('a!42,a!42,a!42');
            times.should.equal(1);
        });


        it('вызывает base', function() {
            var middle = views.inherit(),
                child = middle.inherit(),
                execView = child.execView;

            middle.cached('aaa', function aaa(req, execView) {
                return execView(aaa.base, {q: 4}) + '<middle' + (req.a - 1);
            });

            child.cached('aaa', function aaa(req, execView) {
                return execView(aaa.base) + 'a!' + req.a;
            });
            execView('aaa', {a: 12}).should.equal('parent16><middle11a!12');
        });

        describe('langs', function() {
            var ruViews = views.createLang('ru');

            ruViews('sequence', 'ru[% exec:aaa %],[% exec:aaa %],[% exec:aaa %]');

            ruViews('aaa', function(data, req) {
                return 'ru parent' + (req.a + data.q) + '>';
            });

            it('изолирует разные сессии', function() {
                var child = views.inherit(),
                    cachedView = child.createLang('ru').cached,
                    execView = child.getLang('ru').execView,
                    times = 0;

                cachedView('aaa', function(req) {
                    times++;
                    return 'ru a!' + req.a;
                });

                execView('aaa', {a: 42}).should.equal('ru a!42');
                times.should.equal(1);

                execView('aaa', {a: 11}).should.equal('ru a!11');
                times.should.equal(2);
            });

            it('кэширует результат', function() {
                var child = views.inherit(),
                    cachedView = child.createLang('ru').cached,
                    execView = child.getLang('ru').execView,
                    times = 0;

                cachedView('aaa', function(req) {
                    times++;
                    return 'ru a!' + req.a;
                });

                execView('sequence', {a: 42}).should.equal('ruru a!42,ru a!42,ru a!42');
                times.should.equal(1);
            });

            it('вызывает base', function() {
                var middle = views.inherit(),
                    middleRu = middle.createLang('ru'),
                    child = middle.inherit(),
                    childRu = child.createLang('ru'),
                    execView = child.createLang('ru').execView;

                middleRu.cached('aaa', function aaa(req, execView) {
                    return execView(aaa.base, {q: 4}) + '<ru middle' + (req.a - 1);
                });

                childRu.cached('aaa', function aaa(req, execView) {
                    return execView(aaa.base) + 'ru a!' + req.a;
                });
                execView('aaa', {a: 12}).should.equal('ru parent16><ru middle11ru a!12');
            });
        });
    });

    describe('base', function() {
        var views = home.getView(),
            middle = views.inherit(),
            child = middle.inherit(),
            execView = child.execView;

        before(function () {
            middle('bbb', function() {
                return 'should not be called';
            });

            middle('aaa', function aaa(data, req, execView) {
                return 'middle:' + [data.a, req.q, execView('bbb', {a: 2})];
            });

            child('aaa', function aaa(data, req, execView) {
                return 'child:' + [data.a, req.e] + execView(aaa.base, {a: 1});
            });

            child('bbb', function(data, req) {
                return 'child bbb:' + [data.a, req.w];
            });
        });

        it('допускает вызов из base шаблонов верхнего уровня', function() {
            execView('aaa', {
                a: 0,
                q: 'middle req.q;',
                w: 'child req.w;',
                e: 'child req.e;'
            }).should.equal('child:0,child req.e;middle:1,middle req.q;,child bbb:2,child req.w;');
        });

        describe('langs', function() {
            var ruExecView;

            before(function() {
                views.createLang('ru');
                var middleRu = middle.createLang('ru'),
                    childRu = child.createLang('ru');
                ruExecView = child.createLang('ru').execView;

                middleRu('bbb', function() {
                    return 'should not be called';
                });

                middleRu('aaa', function aaa(data, req, execView) {
                    return 'ru middle:' + [data.a, req.q, execView('bbb', {a: 2})];
                });

                childRu('aaa', function aaa(data, req, execView) {
                    return 'ru child:' + [data.a, req.e] + execView(aaa.base, {a: 1});
                });

                childRu('bbb', function(data, req) {
                    return 'ru child bbb:' + [data.a, req.w];
                });
            });

            it('допускает вызов из base шаблонов верхнего уровня', function() {
                ruExecView('aaa', {
                    a: 0,
                    q: 'middle req.q;',
                    w: 'child req.w;',
                    e: 'child req.e;'
                }).should.equal('ru child:0,child req.e;ru middle:1,middle req.q;,ru child bbb:2,child req.w;');
            });
        });
    });

    describe('createLang/getLang', function() {
        var views;

        beforeEach(function () {
            views = home.getView();
        });

        it('Не создаёт один язык дважды', function () {
            var ru = views.createLang('ru');

            views.createLang('ru').should.equal(ru);
        });

        it('Не позволяет создать язык, которого нет в наследуемом уровне', function () {
            var test = views.inherit();

            expect(function () {
                test.createLang('ru');
            }).to.throw('home.views: Lang "ru" not present in base.');
        });

        it('Cоздаёт язык, который в наследуемом уровне есть', function () {
            var test = views.inherit();

            views.createLang('ru');

            expect(function () {
                test.createLang('ru');
            }).to.not.throw();
        });

        it('Не допускает использования не созданного языка', function () {
            expect(function () {
                views.getLang('ru');
            }).to.throw('home.views: Lang "ru" used before it was created');
        });
    });
});
