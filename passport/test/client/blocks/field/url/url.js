describe('URL field', function() {
    beforeEach(function() {
        this.block = passport.block('url');
        this.sinon = sinon.sandbox.create();
    });
    afterEach(function() {
        this.sinon.restore();
    });

    describe('validateSync', function() {
        it('should return "toolong" if value is over 1024 symbols long', function() {
            this.sinon.stub(this.block, 'val').returns('http://yandex.ru/' + new Array(1024).join('a'));
            expect(this.block.validateSync()).to.be('toolong');
        });

        it('should return "invalid" if url hostname resolves to current location hostname', function() {
            var hostname = 'bing.com';
            this.sinon.stub(this.block, '_getCurrentHostname').returns(hostname);
            this.sinon.stub(this.block, 'val').returns('http://' + hostname);
            expect(this.block.validateSync()).to.be('invalid');
        });

        it('should return null if url hostname matches current location hostname, but pathname is allowed', function() {
            var hostname = 'bing.com';
            this.sinon.stub(this.block, '_getCurrentHostname').returns(hostname);
            this.sinon.stub(this.block, 'val').returns('http://' + hostname);
            this.sinon.stub(this.block, '_isAllowedOauthPathname').returns(true);
            expect(this.block.validateSync()).to.be(null);
        });
    });

    describe('_isAllowedOauthPathname', function() {
        it('should return false when url can not link to oauth', function() {
            this.sinon.stub(this.block, 'canLinkToOauth', false);
            expect(this.block._isAllowedOauthPathname('verification_code')).to.be(false);
        });

        describe('when url can link to oauth', function() {
            beforeEach(function() {
                this.sinon.stub(this.block, 'canLinkToOauth', true);
            });

            it('should return true for /verification_code', function() {
                expect(this.block._isAllowedOauthPathname('/verification_code')).to.be(true);
            });

            it('should return true for verification_code', function() {
                //IE does this: PASSP-9437 — Ошибка "Невалидная ссылка" отображается в Ие8, если подставить Callback url по ссылке
                expect(this.block._isAllowedOauthPathname('verification_code')).to.be(true);
            });
        });
    });
});
