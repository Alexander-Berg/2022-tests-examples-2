/* eslint no-unused-expressions: 0 */
/*
describe('zCookie', function() {
    describe('clear cookie', function() {
        var pl = new PL();

        var files = {
            rapido: {version: '1.234'},
            another: {version: '2.3.4'}
        };

        it('не изменяет пустую куку', function() {
            pl.clearCookie('', files).should.equal('');
        });

        it('не изменяет свежую куку', function() {
            pl.clearCookie('m-rapido:1.234:l', files).should.equal('m-rapido:1.234:l');
            pl.clearCookie('m-rapido-https:1.234:l', files).should.equal('m-rapido-https:1.234:l');
            pl.clearCookie('m-rapido-https:1.234:l|m-rapido:1.234:l', files)
                .should.equal('m-rapido-https:1.234:l|m-rapido:1.234:l');
        });

        it('удаляет старую куку', function() {
            pl.clearCookie('m-rapido:1.31:l', files).should.equal('');
            pl.clearCookie('m-rapido-https:1.31:l', files).should.equal('');
        });

        it('удаляет только старую запись из куки', function() {
            pl.clearCookie('m-rapido:1.234:l|m-rapido:1.23:l', files).should.equal('m-rapido:1.234:l');
            pl.clearCookie('m-rapido:1.234:l|m-rapido2:1.23:l', files).should.equal('m-rapido:1.234:l');
            pl.clearCookie('m-rapido3:1.234:l|m-rapido2:1.23:l', files).should.equal('');
            pl.clearCookie('m-rapido:1.234:l|m-another:2.3.4:c', files).should.equal('m-rapido:1.234:l|m-another:2.3.4:c');
        });

        it('удаляет куку со слишком свежей версией', function() {
            pl.clearCookie('m-rapido:9999:c', files).should.equal('');
        });
    });

    describe('clear local storage', function() {
        var pl = new PL(),
            files = {
                'page.css': {version: '1.234'},
                'another.css': {version: '2.3.4'}
            };
        beforeEach(function() {
            pl = new PL();
        });

        function createAssert(vals, resultCount) {
            var keys = Object.keys(vals);

            pl.ls = {
                length: keys.length,
                key: function (index) {
                    return keys[index];
                },
                getItem: function (key) {
                    return vals[key];
                },
                removeItem: function (key) {
                    delete vals[key];
                    keys.splice(keys.indexOf(key), 1);
                }
            };

            pl.clearLs(files);
            keys.length.should.equal(resultCount);
        }

        it('не изменяет пустое хранилище', function() {
            createAssert({}, 0);
        });
        it('удаляет старые файлы', function() {
            createAssert({'page.css': 'v=1.2@data'}, 0);
        });
        it('не изменяет свежие файлы', function() {
            createAssert({'page.css': 'v=1.234@s=4@data'}, 1);
        });
        it('удаляет неизвестные файлы', function() {
            createAssert({'wtf.css': 'v=1.234@s=4@data'}, 0);
        });
        it('не удаляет чужие записи', function() {
            createAssert({
                'page.css': 'v=1.2@data',
                asd: '4124',
                gdsgs: 'fgasga'
            }, 2);
            createAssert({
                'page.css': 'v=1.234@s=4@data',
                asd: '4124',
                gdsgs: 'fgasga'
            }, 3);
            createAssert({
                'page.css': 'v=1.234@s=4@data',
                'wtf.css': 'v=1.24@s=4@data',
                asd: '4124',
                gdsgs: 'fgasga'
            }, 3);
            createAssert({
                'page.css': 'v=1.234@s=4@data',
                'test2.css': 'v=1.24@s=4@data',
                'test.css': 'v=1.24@s=4@data',
                asd: '4124',
                gdsgs: 'fgasga'
            }, 3);
        });
    });

    describe('валидация', function () {
        var pl,
            sendStat,
            getItem,
            removeItem;

        beforeEach(function() {
            pl = new PL();
            getItem = sinon.spy(function (file) {
                return 'v=123.456@s=21@<contents of ' + file + '>';
            });
            removeItem = sinon.stub();
            pl.ls = {
                getItem: getItem,
                removeItem: removeItem
            };
            sendStat = pl.sendStat = sinon.stub();
        });

        it('ничего не происходит, если в ls нет такого файла', function () {
            pl.ls.getItem = function () {};
            var result = pl.loadFromLs('example', {
                version: '123.4',
                hash: 'face8d'
            });

            sendStat.should.not.be.called;
            removeItem.should.not.be.called;
            result.should.equal('');
        });

        it('отбрасывается неверная версия', function() {
            var result = pl.loadFromLs('example', {
                version: '123.4',
                hash: 'face8d'
            });

            sendStat.should.not.be.called;
            removeItem.should.be.calledWith('example');
            result.should.equal('');
        });

        it('отбрасывается запись неверной длины', function () {
            var result = pl.loadFromLs('long example', {
                version: '123.456',
                hash: 'face8d'
            });

            sendStat.should.be.calledWith('zcookie.error.get');
            removeItem.should.be.calledWith('long example');
            result.should.equal('');
        });

        it('отбрасывается запись с неверным хэшом', function () {
            var result = pl.loadFromLs('example', {
                version: '123.456',
                hash: 'face8d'
            });

            sendStat.should.be.calledWith('zcookie.error.hash');
            removeItem.should.be.calledWith('example');
            result.should.equal('');
        });

        it('валидная запись проходит проверку', function () {
            var result = pl.loadFromLs('example', {
                version: '123.456',
                hash: '6e1yfk'
            });

            sendStat.should.not.be.called;
            removeItem.should.not.be.called;
            result.should.equal('<contents of example>');
        });
    });
});
*/
