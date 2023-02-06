['Additional-email', 'Blacklist-mail', 'Collector-mail', 'Sender-mail', 'Whitelist-mail'].forEach(function(block) {
    describe(block, function() {
        beforeEach(function() {
            this.block = passport.block(block.toLowerCase());
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
            });

            afterEach(function() {
                this.block.validationResult.restore();
            });

            it("should call validationResult with args (false, 'invalid') if entered value is invalid", function() {
                sinon.stub(this.block, 'val').returns(['invalid-email!#$@yandex.ru']);
                this.block.validate();

                expect(this.block.validationResult.calledWith(false, 'invalid')).to.be(true);

                this.block.val.restore();
            });

            it('should call validationResult with args (true, null) if entered value is valid', function() {
                sinon.stub(this.block, 'val').returns(['valid-email@yandex.ru']);
                this.block.validate();

                expect(this.block.validationResult.calledWith(true, null)).to.be(true);

                this.block.val.restore();
            });
        });
    });
});
