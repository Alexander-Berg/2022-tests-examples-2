/* eslint-env es6 */
describe('home.views', function() {
    var testViews = home.getView(),
        execTestView = testViews.execView;

    it('игнорирует дубликаты', function() {
        testViews('test-duplicate', () => 'first definition');
        testViews('test-duplicate', () => 'second definition');

        execTestView('test-duplicate', {}).should.equal('first definition');
    });

    describe('наследование', function() {
        var view = home.getView();
        var execView = view.execView;
        var view2 = view.inherit();
        var execView2 = view2.execView;

        view('test-dev', () => 'test definition');

        view2('testSideEffect', () => 'ok');
        view2('ok', () => ': ok');

        it('использует базовые шаблоны', function() {
            execView2('test-dev', {}).should.equal('test definition');
        });

        it('не влияет на базовые шаблоны', function() {
            execView('testSideEffect', {}).should.equal('');

            view2('test-dev', () => 'test definition overloaded', true);

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
        view('template', data => data.key0);

        view('view-t0', (data, req, execView) => execView('view2-t1', data));

        view('view-t1', (data, req, execView) => execView('view2-t2', data));

        view('view-a0', (data, req, execView) => execView('view2-a0', data));

        view2('template2', data => data.key1);

        view2('template3', data => data.key1);

        view2('view2-t0', (data, req, execView) => execView('view-t0', data));

        view2('view2-t1', (data, req, execView) => execView('view-t1', data));

        view2('view2-t2', () => 'test');

        view2('view2-a0', data => data.key1);

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

        views('test', (data, req, exec) => `abc ${exec('test2')}`);

        views('test2', () => '123');

        views.execView('test', {}).should.equal('abc 123');
    });


    describe('req объект', function() {
        var view = home.getView(),
            execView = view.execView;

        view('req-seeker-str', (data, req, exec) => `${exec('req-seeker-func', data)} ${data.first} ${data.second}`);

        view('req-seeker-func', function (data, req) {
            return data.first + ' and ' + req.first + req.second;
        });

        view('func-template', function (data, req, execView) {
            return execView('req-seeker-func', {
                first: 'baz'
            });
        });

        view('func-override', function(data, req, execView) {
            return execView.withReq('req-seeker-str', data, {
                first: 'override'
            });
        });

        it('не теряется при вызове', function() {
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

    describe('cached views', function() {
        var views = home.getView();

        views('sequence', (data, req, exec) => `${exec('aaa')},${exec('aaa')},${exec('aaa')}`);

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
                times = 0;

            cachedView('aaa', function(req) {
                times++;
                return 'a!' + req.a;
            });

            execView('aaa', {a: 42}).should.equal('a!42');
            times.should.equal(1);

            execView('aaa', {a: 11}).should.equal('a!11');
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
    });

    it('Удаляет шаблоны из списка', function() {
        testViews('some', () => 'first definition');

        execTestView('some', {}).should.equal('first definition');
        testViews.cleanViews(['some']);
        execTestView('some', {}).should.equal('');

        testViews('some', () => 'second definition');

        execTestView('some', {}).should.equal('second definition');
    });
});
