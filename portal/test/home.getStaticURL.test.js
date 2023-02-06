/* eslint no-unused-expressions: 0 */

describe('home.getStaticURL', function () {
    var getStaticURL;
    beforeEach(function() {
        getStaticURL = new home.GetStaticURL({
            version: '1.234',
            rewrite: false,
            s3root: 's3/default'
        });

        if (!home.env) {
            home.env = {};
        }
    });

    home.GetStaticURL.addFreezedFiles('frozen', {
        'test.js': '/freezedtest.js',
        '/test2.js': '/freezedtest2.js',
        'long/path/to/test.css': 'https://host.for/freeze/to/hASH1234.css',
        '/some.js': 'https://yastatic.net/someFreezed.js'
    });
    home.GetStaticURL.addFreezedFiles('white', {
        '/some.js': '//yastatic.net/s3/default/_/someFreezed.js'
    });

    describe('getAbsolute', function () {
        describe('dev', function () {
            beforeEach(function() {
                home.env.externalStatic = false;
            });

            it('преобразует относительные урлы', function() {
                getStaticURL.getAbsolute('/test.js', 'test').should.equal('/tmpl/test/test.js');
            });

            it('не преобразует абсолютные урлы', function() {
                getStaticURL.getAbsolute('//path.to/remote/resource.js', 'test').should.equal('//path.to/remote/resource.js');
                getStaticURL.getAbsolute('http://path.to/remote/resource.js', 'test').should.equal('http://path.to/remote/resource.js');
                getStaticURL.getAbsolute('https://path.to/remote/resource.js', 'test').should.equal('https://path.to/remote/resource.js');
            });

            describe('freeze', function() {
                beforeEach(function() {
                    home.env.externalStatic = false;
                });

                it('преобразует относительные урлы, не попавшие во фриз', function() {
                    getStaticURL.getAbsolute('/test.js', 'test').should.equal('/tmpl/test/test.js');
                });

                it('преобразует относительные урлы, попавшие во фриз', function() {
                    getStaticURL.getAbsolute('/test.js', 'frozen').should.equal('/freezedtest.js');
                    getStaticURL.getAbsolute('/test2.js', 'frozen').should.equal('/freezedtest2.js');
                });
            });
        });

        describe('production', function() {
            beforeEach(function() {
                home.env.externalStatic = true;
            });

            it('преобразует относительные урлы со страницей', function() {
                getStaticURL.getAbsolute('/test.js', 'test').should.equal('//yastatic.net/s3/default/1.234/test/test.js');
            });

            it('преобразует относительные урлы с пустой страницей', function() {
                getStaticURL.getAbsolute('/test.js', '').should.equal('//yastatic.net/s3/default/1.234/test.js');
            });

            it('не преобразует абсолютные урлы', function() {
                getStaticURL.getAbsolute('//path.to/remote/resource.js', 'test').should.equal('//path.to/remote/resource.js');
                getStaticURL.getAbsolute('http://path.to/remote/resource.js', 'test').should.equal('http://path.to/remote/resource.js');
                getStaticURL.getAbsolute('https://path.to/remote/resource.js', 'test').should.equal('https://path.to/remote/resource.js');
            });

            describe('использует staticHost', function () {
                it('переданный в opts', function () {
                    getStaticURL.getAbsolute('/test.js', '', {
                        staticHost: '//yandex.st'
                    }).should.equal('//yandex.st/s3/default/1.234/test.js');
                });

                it('переданный в конструктор', function () {
                    var getStaticURL = new home.GetStaticURL({
                        staticHost: '//some.random.host',
                        s3root: 's3/default'
                    });
                    getStaticURL.getAbsolute('/test.js', '')
                        .should.equal('//some.random.host/s3/default/1.234/test.js');
                });
            });

            describe('использует s3root', function () {
                it('переданный в opts', function () {
                    getStaticURL.getAbsolute('/test.js', '', {
                        s3root: 'meow'
                    }).should.equal('//yastatic.net/meow/1.234/test.js');
                });

                it('переданный в конструктор', function () {
                    var getStaticURL = new home.GetStaticURL({
                        s3root: 'meow'
                    });
                    getStaticURL.getAbsolute('/test.js', '')
                        .should.equal('//yastatic.net/meow/1.234/test.js');
                });
            });

            describe('использует version', function () {
                it('переданный в opts', function () {
                    getStaticURL.getAbsolute('/test.js', '', {
                        version: '1.111'
                    }).should.equal('//yastatic.net/s3/default/1.111/test.js');
                });

                it('переданный в конструктор', function () {
                    var getStaticURL = new home.GetStaticURL({
                        version: '1.111',
                        s3root: 's3/default'
                    });
                    getStaticURL.getAbsolute('/test.js', '')
                        .should.equal('//yastatic.net/s3/default/1.111/test.js');
                });
            });

            it('подменяет одновременно хост и рут', function () {
                getStaticURL.getAbsolute('/somex.js', 'white', {
                    s3root: 'www-s3',
                    staticHost: '//yandex.st'
                }).should.equal('//yandex.st/www-s3/1.234/white/somex.js');
            });

            describe('freeze', function() {
                beforeEach(function() {
                    home.env.externalStatic = true;
                });

                it('преобразует относительные урлы, не попавшие во фриз', function() {
                    getStaticURL.getAbsolute('/test.js', 'test').should.equal('//yastatic.net/s3/default/1.234/test/test.js');
                });

                it('преобразует относительные урлы, попавшие во фриз', function() {
                    getStaticURL.getAbsolute('/test.js', 'frozen').should.equal('/freezedtest.js');
                    getStaticURL.getAbsolute('/test2.js', 'frozen').should.equal('/freezedtest2.js');
                    getStaticURL.getAbsolute('long/path/to/test.css', 'frozen').should.equal('https://host.for/freeze/to/hASH1234.css');
                });

                it('не преобразует абсолютные урлы', function() {
                    getStaticURL.getAbsolute('//path.to/remote/resource.js', 'test').should.equal('//path.to/remote/resource.js');
                    getStaticURL.getAbsolute('http://path.to/remote/resource.js', 'test').should.equal('http://path.to/remote/resource.js');
                    getStaticURL.getAbsolute('https://path.to/remote/resource.js', 'test').should.equal('https://path.to/remote/resource.js');
                });

                it('поддерживает staticHost', function () {
                    getStaticURL.getAbsolute('/some.js', 'white', {
                        staticHost: '//yandex.st'
                    }).should.equal('//yandex.st/s3/default/_/someFreezed.js');
                });

                it('не поддерживает замену рута для фриза', function () {
                    getStaticURL.getAbsolute('/some.js', 'white', {
                        s3root: 'quack'
                    }).should.equal('//yastatic.net/s3/default/_/someFreezed.js');
                });

                it('подменяет только хост, но не рут', function () {
                    getStaticURL.getAbsolute('/some.js', 'white', {
                        s3root: 'www-s3',
                        staticHost: '//yandex.st'
                    }).should.equal('//yandex.st/s3/default/_/someFreezed.js');
                });
            });
        });
    });

    describe('getHash', function () {
        beforeEach(function () {
            getStaticURL = new home.GetStaticURL({
                rewrite: false,
                s3root: 's3/default'
            });
        });

        it('возвращает хэши', function() {
            getStaticURL.getHash('/test.js', 'frozen').should.equal('freezedtest');
            getStaticURL.getHash('long/path/to/test.css', 'frozen').should.equal('freezetohASH1234');
        });

        it('не перезаписывает s3root в getHash', function () {
            getStaticURL.getHash('/some.js', 'white').should.equal('s3default_someFreezed');
            expect(getStaticURL.getHash('/some2.js', 'white')).to.be.undefined;

            getStaticURL.getHash('/some.js', 'white', {
                s3root: 'www-s3'
            }).should.equal('s3default_someFreezed');
            expect(getStaticURL.getHash('/some2.js', 'white', {
                s3root: 'www-s3'
            })).to.be.undefined;
        });
    });

    describe('customRewrite', function () {
        beforeEach(function() {
            home.env.externalStatic = true;
        });

        it('должно работать без маппинга', function() {
            var getStaticURL = new home.GetStaticURL({
                s3root: 's3/default'
            });

            getStaticURL.getAbsolute('pages/bender/bender.js', 'white').should.equal('//yastatic.net/s3/default/1.234/white/pages/bender/bender.js');
            getStaticURL.getAbsolute('https://yastatic.net/jquery/2.1.4/jquery.js', '').should.equal('https://yastatic.net/jquery/2.1.4/jquery.js');
        });

        it('должно работать с маппингом', function() {
            var getStaticURL = new home.GetStaticURL({
                s3root: 's3/default',
                customRewrite: function (url) {
                    return url.replace(/^(https?:)?\/\/yastatic.net\/jquery/, '$1//br.yastatic.net/jquery');
                }
            });

            getStaticURL.getAbsolute('pages/bender/bender.js', 'white')
                .should.equal('//yastatic.net/s3/default/1.234/white/pages/bender/bender.js');
            getStaticURL.getAbsolute('https://yastatic.net/jquery/2.1.4/jquery.js', '')
                .should.equal('https://br.yastatic.net/jquery/2.1.4/jquery.js');
            getStaticURL.getAbsolute('//yastatic.net/jquery/2.1.4/jquery.js', '')
                .should.equal('//br.yastatic.net/jquery/2.1.4/jquery.js');
            getStaticURL.getAbsolute('https://yastatic.net/s3/default/_/A/A/A.svg', '')
                .should.equal('https://yastatic.net/s3/default/_/A/A/A.svg');
        });
    });
});
