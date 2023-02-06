describe('Title field', function() {
    beforeEach(function() {
        this.block = passport.block('title');
        this.sinon = sinon.sandbox.create();
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('validateSync', function() {
        it('should return "toolong" if title is over 100 chars', function() {
            this.sinon.stub(this.block, 'val').returns(new Array(102).join('i'));
            expect(this.block.validateSync()).to.be('toolong');
        });

        it('should return null if title is 1 char long', function() {
            this.sinon.stub(this.block, 'val').returns('1');
            expect(this.block.validateSync()).to.be(null);
        });
    });
});
