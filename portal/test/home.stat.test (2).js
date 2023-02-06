/* eslint dot-notation: 1, no-unused-expressions: 0 */
describe('home.stat', function() {
    var fakeHashOur = {
        clckBase: 'clck.tld/base',
        page: 'testpage',
        hostname: 'testhost.me',
        request_id: '12345678.34534.3453',
        LiveCartridge: 1
    };

    var fakeHashOff = {
        LiveCartridge: 0
    };

    describe('getAttr', function() {
        var stat = new home.Stat(fakeHashOur, 11, 1234567);

        it('редиректный', function() {
            stat.getAttr('str0').should.equal(' data-statlog="str0" data-redir="true"');

        });
        it('не резиректный', function() {
            stat.getAttr('str1', '', {isRedirect: false}).should.equal(' data-statlog="str1"');

        });

        var statOff = new home.Stat(fakeHashOff, 11, 1234567);

        it('не возвращает атрибутов при отключенной статистике', function() {
            statOff.getAttr('str0').should.equal('');
            statOff.getAttr('str1', '', {isRedirect: false}).should.equal('');
        });
    });
    
    describe('imgScr', function() {
        var stat = new home.Stat(fakeHashOur, 11, 1234566);

        it('генерирует правильный урл', function() {
            stat.imgSrc('path.to.block').should.equal('//clck.tld/base/counter/dtype=stred/pid=11/cid=1234566' +
                '/path=testpage.path.to.block/sid=12345678.34534.3453/*');

        });

        var statOff = new home.Stat(fakeHashOff, 11, 1234567);

        it('не возвращет урл при отключенной статистике', function() {
            statOff.imgSrc('path.to.block').should.equal('');
        });
    });
    
    describe('getUrl', function() {
        var stat = new home.Stat(fakeHashOur, 11, 1234565);

        it('генерирует редирект для абсолютных урлов', function() {
            stat.getUrl('path.to.block', '//ya.ru/blabla?param=%20val').should.equal('//clck.tld/base/redir/dtype=stred/pid=11/cid=1234565' +
                '/path=testpage.path.to.block/sid=12345678.34534.3453/*//ya.ru/blabla?param=%20val');

        });
        it('генерирует редирект для относительных урлов', function() {
            stat.getUrl('path.to.block', '/blabla?param=%20val').should.equal('//clck.tld/base/redir/dtype=stred/pid=11/cid=1234565' +
                '/path=testpage.path.to.block/sid=12345678.34534.3453/*//testhost.me/blabla?param=%20val');

        });
        
        it('генерирует редирект для поломанных урлов', function() {
            stat.getUrl('path.to.block', '/blabla?param=%C4%F3%E1%ED%E0').should.equal('//clck.tld/base/redir/dtype=stred/pid=11/cid=1234565' +
                '/path=testpage.path.to.block/sid=12345678.34534.3453/*//testhost.me/blabla?param=%C4%F3%E1%ED%E0');

        });

        var statOff = new home.Stat(fakeHashOff, 11, 1234567);

        it('не изменяет урл при отключенной статистике', function() {
            statOff.getUrl('path.to.block', '//ya.ru/blabla?param=%20val').should.equal('//ya.ru/blabla?param=%20val');
            statOff.getUrl('path.to.block', '/blabla?param=%20val').should.equal('/blabla?param=%20val');
            statOff.getUrl('path.to.block', '/blabla?param=%C4%F3%E1%ED%E0').should.equal('/blabla?param=%C4%F3%E1%ED%E0');
        });
    });

});
