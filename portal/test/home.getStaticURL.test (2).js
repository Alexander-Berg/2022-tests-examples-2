describe('home.getStaticURL', function () {
    
    describe('getStaticURL', function() {

        describe('dev', function() {
            before(function() {
                config.dev = true;
            });

            it('преобразует относительные урлы', function() {
                home.getStaticURL('/test.js').should.equal('/test/test.js');
            });

            it('не преобразует абсолютные урлы', function() {
                home.getStaticURL('//path.to/remote/resource.js').should.equal('//path.to/remote/resource.js');
                home.getStaticURL('http://path.to/remote/resource.js').should.equal('http://path.to/remote/resource.js');
                home.getStaticURL('https://path.to/remote/resource.js').should.equal('https://path.to/remote/resource.js');
            });
        });

        describe('production', function() {
            before(function() {
                config.dev = false;
            });

            it('преобразует относительные урлы', function() {
                home.getStaticURL('/test.js').should.match(/^\/\/yastatic\.net\/s3\/home-static\/tune\//)
                    .and.match(/\/test.js$/);
            });

            it('не преобразует абсолютные урлы', function() {
                home.getStaticURL('//path.to/remote/resource.js').should.equal('//path.to/remote/resource.js');
                home.getStaticURL('http://path.to/remote/resource.js').should.equal('http://path.to/remote/resource.js');
                home.getStaticURL('https://path.to/remote/resource.js').should.equal('https://path.to/remote/resource.js');
            });
        });
    });

    describe('freeze', function() {
        before(function() {
            home.getStaticURL.addProject('1.235', 'frozen', {
                'test.js': '/freezedtest.js',
                '/test2.js': '/freezedtest2.js',
                'long/path/to/test.css': 'https://host.for/freeze/to/hASH1234.css'
            });
        });

        describe('dev', function() {
            before(function() {
                config.dev = true;
            });

            it('преобразует относительные урлы с отключенным фризом', function() {
                home.getStaticURL.enableFreeze(false);
                home.getStaticURL('/test.js').should.equal('/test/test.js');
                home.getStaticURL('/test2.js').should.equal('/test/test2.js');
                home.getStaticURL.enableFreeze(true);
            });

            it('преобразует относительные урлы, не попавшие во фриз', function() {
                home.getStaticURL('/testa.js').should.equal('/test/testa.js');
            });

            it('преобразует относительные урлы, попавшие во фриз', function() {
                home.getStaticURL('/test.js').should.equal('/freezedtest.js');
                home.getStaticURL('/test2.js').should.equal('/freezedtest2.js');
            });
        });

        describe('production', function() {
            before(function() {
                config.dev = false;
            });

            it('преобразует относительные урлы с отключенным фризом', function() {
                home.getStaticURL.enableFreeze(false);
                home.getStaticURL('/test.js').should.equal('//yastatic.net/frozen/1.235/test.js');
                home.getStaticURL('/test2.js').should.equal('//yastatic.net/frozen/1.235/test2.js');
                home.getStaticURL.enableFreeze(true);
            });

            it('преобразует относительные урлы, не попавшие во фриз', function() {
                home.getStaticURL('/testa.js').should.equal('//yastatic.net/frozen/1.235/testa.js');
            });

            it('преобразует относительные урлы, попавшие во фриз', function() {
                home.getStaticURL('/test.js').should.equal('/freezedtest.js');
                home.getStaticURL('/test2.js').should.equal('/freezedtest2.js');
                home.getStaticURL('long/path/to/test.css').should.equal('https://host.for/freeze/to/hASH1234.css');
            });

            it('не преобразует абсолютные урлы', function() {
                home.getStaticURL('//path.to/remote/resource.js').should.equal('//path.to/remote/resource.js');
                home.getStaticURL('http://path.to/remote/resource.js').should.equal('http://path.to/remote/resource.js');
                home.getStaticURL('https://path.to/remote/resource.js').should.equal('https://path.to/remote/resource.js');
            });

            it('возвращает хэши', function() {
                home.getStaticURL.getHash('/test.js').should.equal('freezedtest');
                home.getStaticURL.getHash('long/path/to/test.css').should.equal('freezetohASH1234');
            });
        });
    });
});
