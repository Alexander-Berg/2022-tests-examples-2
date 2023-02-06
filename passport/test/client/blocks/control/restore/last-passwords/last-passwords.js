describe('Last-passwords', function() {
    beforeEach(function() {
        this.block = passport.block('last-passwords');
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

    //Deprecated

    //describe('checkState', function() {
    //    beforeEach(function() {
    //        sinon.stub(this.block, 'isEmpty');
    //    });
    //
    //    afterEach(function() {
    //        this.block.isEmpty.restore();
    //    });
    //
    //    it('should set isRequired "false" if value is empty', function() {
    //        this.block.isEmpty.returns(true);
    //        this.block.checkState();
    //        expect(this.block.isRequired).to.be(false);
    //    });
    //
    //    it('should set isRequired "true" if value isn\'t empty', function() {
    //        this.block.isEmpty.returns(false);
    //        this.block.checkState();
    //        expect(this.block.isRequired).to.be(true);
    //    });
    //});
});
