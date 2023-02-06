describe('Phones', function() {
    beforeEach(function() {
        this.block = passport.block('phones');
    });

    describe('"this.val()" should return', function() {
        it('an Array if Field is multiply', function() {
            this.block.options = {
                multiplyFields: true
            };

            expect(this.block.val()).to.be.an(Array);

            this.block.options = {};
        });

        it("a String if Field isn't multiply", function() {
            expect(this.block.val()).to.be.a('string');
        });
    });

    describe('validate', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'validationResult');
            this.block.init();
        });

        afterEach(function() {
            this.block.validationResult.restore();
        });

        it("should call validationResult with args (false, 'invalid') if entered value is invalid", function() {
            sinon.stub(this.block, 'val').returns(['phone? +7 921 323 12 55']);
            this.block.validate();

            expect(this.block.validationResult.calledWith(false, 'invalid')).to.be(true);

            this.block.val.restore();
        });

        it('should call validationResult with args (true, null) if entered value is valid', function() {
            sinon.stub(this.block, 'val').returns(['+7 921 323 12 55']);
            this.block.validate();

            expect(this.block.validationResult.calledWith(true, null)).to.be(true);

            this.block.val.restore();
        });
    });
});
