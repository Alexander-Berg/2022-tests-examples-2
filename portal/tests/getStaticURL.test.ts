import { addFreezedFiles, GetStaticURL } from '../getStaticURL';

describe('getStaticURL', function() {
    let getStaticURL: GetStaticURL;

    beforeEach(function() {
        getStaticURL = new GetStaticURL({
            version: '1.234',
            s3root: 's3/default'
        });
    });

    addFreezedFiles('frozen', {
        'test.js': '/freezedtest.js',
        '/test2.js': '/freezedtest2.js',
        'long/path/to/test.css': 'https://host.for/freeze/to/hASH1234.css',
        '/some.js': 'https://yastatic.net/someFreezed.js'
    });
    addFreezedFiles('white', {
        '/some.js': '//yastatic.net/s3/default/_/someFreezed.js'
    });

    describe('getAbsolute', function() {
        describe('dev', function() {
            beforeEach(function() {
                home.env.externalStatic = false;
            });

            test('преобразует относительные урлы', function() {
                expect(getStaticURL.getAbsolute('/test.js', 'test')).toEqual('/tmpl/test/test.js');
            });

            test('не преобразует абсолютные урлы', function() {
                expect(getStaticURL.getAbsolute('//path.to/remote/resource.js', 'test')).toEqual('//path.to/remote/resource.js');
                expect(getStaticURL.getAbsolute('http://path.to/remote/resource.js', 'test')).toEqual('http://path.to/remote/resource.js');
                expect(getStaticURL.getAbsolute('https://path.to/remote/resource.js', 'test')).toEqual('https://path.to/remote/resource.js');
            });

            describe('freeze', function() {
                beforeEach(function() {
                    home.env.externalStatic = false;
                });

                test('преобразует относительные урлы, не попавшие во фриз', function() {
                    expect(getStaticURL.getAbsolute('/test.js', 'test')).toEqual('/tmpl/test/test.js');
                });

                test('преобразует относительные урлы, попавшие во фриз', function() {
                    expect(getStaticURL.getAbsolute('/test.js', 'frozen')).toEqual('/freezedtest.js');
                    expect(getStaticURL.getAbsolute('/test2.js', 'frozen')).toEqual('/freezedtest2.js');
                });
            });
        });

        describe('production', function() {
            beforeEach(function() {
                home.env.externalStatic = true;
            });

            test('преобразует относительные урлы со страницей', function() {
                expect(getStaticURL.getAbsolute('/test.js', 'test')).toEqual('//yastatic.net/s3/default/1.234/test/test.js');
            });

            test('преобразует относительные урлы с пустой страницей', function() {
                expect(getStaticURL.getAbsolute('/test.js', '')).toEqual('//yastatic.net/s3/default/1.234/test.js');
            });

            test('не преобразует абсолютные урлы', function() {
                expect(getStaticURL.getAbsolute('//path.to/remote/resource.js', 'test')).toEqual('//path.to/remote/resource.js');
                expect(getStaticURL.getAbsolute('http://path.to/remote/resource.js', 'test')).toEqual('http://path.to/remote/resource.js');
                expect(getStaticURL.getAbsolute('https://path.to/remote/resource.js', 'test')).toEqual('https://path.to/remote/resource.js');
            });

            describe('использует staticHost', function() {
                test('переданный в opts', function() {
                    expect(getStaticURL.getAbsolute('/test.js', '', {
                        staticHost: '//yandex.st'
                    })).toEqual('//yandex.st/s3/default/1.234/test.js');
                });

                test('переданный в конструктор', function() {
                    let getStaticURL = new GetStaticURL({
                        staticHost: '//some.random.host',
                        s3root: 's3/default',
                        version: '1.234'
                    });
                    expect(getStaticURL.getAbsolute('/test.js', ''))
                        .toEqual('//some.random.host/s3/default/1.234/test.js');
                });
            });

            describe('использует s3root', function() {
                test('переданный в opts', function() {
                    expect(getStaticURL.getAbsolute('/test.js', '', {
                        s3root: 'meow'
                    })).toEqual('//yastatic.net/meow/1.234/test.js');
                });

                test('переданный в конструктор', function() {
                    let getStaticURL = new GetStaticURL({
                        s3root: 'meow',
                        version: '1.234'
                    });
                    expect(getStaticURL.getAbsolute('/test.js', ''))
                        .toEqual('//yastatic.net/meow/1.234/test.js');
                });
            });

            describe('использует version', function() {
                test('переданный в opts', function() {
                    expect(getStaticURL.getAbsolute('/test.js', '', {
                        version: '1.111'
                    })).toEqual('//yastatic.net/s3/default/1.111/test.js');
                });

                test('переданный в конструктор', function() {
                    let getStaticURL = new GetStaticURL({
                        version: '1.111',
                        s3root: 's3/default'
                    });
                    expect(getStaticURL.getAbsolute('/test.js', ''))
                        .toEqual('//yastatic.net/s3/default/1.111/test.js');
                });
            });

            test('подменяет одновременно хост и рут', function() {
                expect(getStaticURL.getAbsolute('/somex.js', 'white', {
                    s3root: 'www-s3',
                    staticHost: '//yandex.st'
                })).toEqual('//yandex.st/www-s3/1.234/white/somex.js');
            });

            describe('freeze', function() {
                beforeEach(function() {
                    home.env.externalStatic = true;
                });

                test('преобразует относительные урлы, не попавшие во фриз', function() {
                    expect(getStaticURL.getAbsolute('/test.js', 'test')).toEqual('//yastatic.net/s3/default/1.234/test/test.js');
                });

                test('преобразует относительные урлы, попавшие во фриз', function() {
                    expect(getStaticURL.getAbsolute('/test.js', 'frozen')).toEqual('/freezedtest.js');
                    expect(getStaticURL.getAbsolute('/test2.js', 'frozen')).toEqual('/freezedtest2.js');
                    expect(getStaticURL.getAbsolute('long/path/to/test.css', 'frozen')).toEqual('https://host.for/freeze/to/hASH1234.css');
                });

                test('не преобразует абсолютные урлы', function() {
                    expect(getStaticURL.getAbsolute('//path.to/remote/resource.js', 'test')).toEqual('//path.to/remote/resource.js');
                    expect(getStaticURL.getAbsolute('http://path.to/remote/resource.js', 'test')).toEqual('http://path.to/remote/resource.js');
                    expect(getStaticURL.getAbsolute('https://path.to/remote/resource.js', 'test')).toEqual('https://path.to/remote/resource.js');
                });

                test('поддерживает staticHost', function() {
                    expect(getStaticURL.getAbsolute('/some.js', 'white', {
                        staticHost: '//yandex.st'
                    })).toEqual('//yandex.st/s3/default/_/someFreezed.js');
                });

                test('не поддерживает замену рута для фриза', function() {
                    expect(getStaticURL.getAbsolute('/some.js', 'white', {
                        s3root: 'quack'
                    })).toEqual('//yastatic.net/s3/default/_/someFreezed.js');
                });

                test('подменяет только хост, но не рут', function() {
                    expect(getStaticURL.getAbsolute('/some.js', 'white', {
                        s3root: 'www-s3',
                        staticHost: '//yandex.st'
                    })).toEqual('//yandex.st/s3/default/_/someFreezed.js');
                });
            });
        });
    });

    describe('getHash', function() {
        beforeEach(function() {
            getStaticURL = new GetStaticURL({
                s3root: 's3/default'
            });
        });

        test('возвращает хэши', function() {
            expect(getStaticURL.getHash('/test.js', 'frozen')).toEqual('freezedtest');
            expect(getStaticURL.getHash('long/path/to/test.css', 'frozen')).toEqual('freezetohASH1234');
        });

        test('не перезаписывает s3root в getHash', function() {
            expect(getStaticURL.getHash('/some.js', 'white')).toEqual('s3default_someFreezed');
            expect(getStaticURL.getHash('/some2.js', 'white')).toBeUndefined();
        });
    });

    describe('customRewrite', function() {
        beforeEach(function() {
            home.env.externalStatic = true;
        });

        test('должно работать без маппинга', function() {
            let getStaticURL = new GetStaticURL({
                s3root: 's3/default',
                version: '1.234'
            });

            expect(getStaticURL.getAbsolute('pages/bender/bender.js', 'white')).toEqual('//yastatic.net/s3/default/1.234/white/pages/bender/bender.js');
            expect(getStaticURL.getAbsolute('https://yastatic.net/jquery/2.1.4/jquery.js', '')).toEqual('https://yastatic.net/jquery/2.1.4/jquery.js');
        });

        test('должно работать с маппингом', function() {
            let getStaticURL = new GetStaticURL({
                s3root: 's3/default',
                customRewrite(url) {
                    return url.replace(/^(https?:)?\/\/yastatic.net\/jquery/, '$1//br.yastatic.net/jquery');
                },
                version: '1.234'
            });

            expect(getStaticURL.getAbsolute('pages/bender/bender.js', 'white'))
                .toEqual('//yastatic.net/s3/default/1.234/white/pages/bender/bender.js');
            expect(getStaticURL.getAbsolute('https://yastatic.net/jquery/2.1.4/jquery.js', ''))
                .toEqual('https://br.yastatic.net/jquery/2.1.4/jquery.js');
            expect(getStaticURL.getAbsolute('//yastatic.net/jquery/2.1.4/jquery.js', ''))
                .toEqual('//br.yastatic.net/jquery/2.1.4/jquery.js');
            expect(getStaticURL.getAbsolute('https://yastatic.net/s3/default/_/A/A/A.svg', ''))
                .toEqual('https://yastatic.net/s3/default/_/A/A/A.svg');
        });
    });
});
