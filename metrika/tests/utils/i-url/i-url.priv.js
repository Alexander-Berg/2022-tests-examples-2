describe('i-url', function () {
    it('it remove hash', function () {
        expect('test.com/').to.be.equal(BN('i-url').getDomainPath(
            'http://test.com/#adfadsfdsf'
        ));
    });

    it('it remove query', function () {
        expect('test.com/').to.be.equal(BN('i-url').getDomainPath(
            'http://test.com/?i=1&ad'
        ));
    });

    it('keep save path', function () {
        expect('test.com/path/asdf').to.be.equal(BN('i-url').getDomainPath(
            'http://test.com/path/asdf?i=1&ad'
        ));
    });

    it('NullPointer', function () {
        expect('').to.be.equal(BN('i-url').getDomainPath(
            ''
        ));
    });

    it('it protocol indeferent', function () {
        expect('test.com/path/asdf').to.be.equal(BN('i-url').getDomainPath(
            'test.com/path/asdf?i=1&ad'
        ));
    });

});
