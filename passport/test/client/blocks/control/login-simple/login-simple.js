describe('Login-simple', function() {
    beforeEach(function() {
        this.block = passport.block('login-simple');
    });

    describe('validate', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'validationResult');
        });

        afterEach(function() {
            this.block.validationResult.restore();
        });

        it("should call validationResult with args (false, 'missingvalue') if value is empty", function() {
            sinon.stub(this.block, 'val').returns('');
            this.block.validate();

            expect(this.block.validationResult.calledWith(false, 'missingvalue')).to.be(true);

            this.block.val.restore();
        });
    });
});
