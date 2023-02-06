describe('Phone', function() {
    beforeEach(function() {
        this.block = passport.block('phone');
        this.blockControl = passport.block('control');
    });

    describe('validate', function() {
        beforeEach(function() {
            this.already = this.block.inited.already;
            this.block.inited.already = true;

            sinon.stub(this.blockControl, 'validate');
        });
        afterEach(function() {
            this.blockControl.validate.restore();
            this.block.inited.already = this.already;
        });

        it('should call control validate with right params', function() {
            var params = {};

            this.block.validate(params);
            expect(this.blockControl.validate.calledWithExactly(params)).to.be(true);
        });

        it('should return result of control validation', function() {
            var params = {};

            this.blockControl.validate.returns(params);
            expect(this.block.validate()).to.be.equal(params);
        });

        it('should return resolved deferred with "false" if not inited already', function(done) {
            this.block.inited.already = false;
            this.block.validate().then(function(result) {
                expect(result).to.be(false);
                done();
            });
        });
    });
});
