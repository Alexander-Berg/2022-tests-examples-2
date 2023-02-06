describe('home.stringf', function () {
    it('replaces', function () {
        home.stringf('').should.equal('');
        home.stringf('', 'apple').should.equal('');
        home.stringf('%s').should.equal('');
        home.stringf('%s', undefined).should.equal('');
        home.stringf('%s', null).should.equal('');
        home.stringf('%s', 'apple').should.equal('apple');
        home.stringf('%s - %s', 'apple').should.equal('apple - ');
        home.stringf('%s - %s', 'apple', 'juice').should.equal('apple - juice');
    });
});
