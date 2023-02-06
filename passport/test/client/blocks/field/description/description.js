describe('Title field', function() {
    beforeEach(function() {
        this.block = passport.block('description');
        this.sinon = sinon.sandbox.create();
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('validateSync', function() {
        it('should return "toolong" if value is over 250 chars', function() {
            this.sinon.stub(this.block, 'val').returns(new Array(252).join('i'));
            expect(this.block.validateSync()).to.be('toolong');
        });

        it('should return null if value is 1 char long', function() {
            this.sinon.stub(this.block, 'val').returns('1');
            expect(this.block.validateSync()).to.be(null);
        });
    });
});
