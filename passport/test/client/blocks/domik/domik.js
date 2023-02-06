describe('Domik', function() {
    beforeEach(function() {
        this.block = passport.block('domik');
    });

    describe('"this.repaintDomik()"', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'repaintDomik');
        });

        afterEach(function() {
            this.block.repaintDomik.restore();
        });

        it('should be called with arg "edit" by "this.switchAccountsListToEdit()"', function() {
            this.block.switchAccountsListToEdit();
            expect(this.block.repaintDomik.calledWith('edit')).to.be(true);
        });

        it('should be called without args by "this.switchAccountsListToStatic()"', function() {
            this.block.switchAccountsListToStatic();
            expect(this.block.repaintDomik.calledWith()).to.be(true);
        });

        it('should be called with arg "add-user" by "this.showMultiForm()"', function() {
            this.block.showMultiForm();
            expect(this.block.repaintDomik.calledWith('add-user')).to.be(true);
        });

        it('should be called without args by "this.hideMultiForm()"', function() {
            this.block.hideMultiForm();
            expect(this.block.repaintDomik.calledWith()).to.be(true);
        });
    });

    describe('"this.submitMultiAuthForm()"', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'submitMultiAuthForm');
        });

        afterEach(function() {
            this.block.submitMultiAuthForm.restore();
        });

        it('should be called with arg "change_default" by "this.changeDefaultAccount()"', function() {
            this.block.changeDefaultAccount();
            expect(this.block.submitMultiAuthForm.calledWith(event, 'change_default')).to.be(true);
        });

        it('should be called with arg "logout" by "this.logoutAccount()"', function() {
            this.block.logoutAccount();
            expect(this.block.submitMultiAuthForm.calledWith(event, 'logout')).to.be(true);
        });
    });

    ['setupPaths', 'setupMultiAuth', 'setupBroker', 'getMail'].forEach(function(method) {
        it('"this.' + method + '()" should called once by "this.init()"', function() {
            sinon.stub(this.block, method);
            this.block.init();

            expect(this.block[method].calledOnce).to.be(true);

            this.block[method].restore();
        });
    });

    it('"this.switchAccountsListToStatic" should drop last action', function() {
        this.block.lastAction = 'logout';
        this.block.switchAccountsListToStatic();

        expect(this.block.lastAction).to.be(null);
    });
});

['Login-auth', 'Password-auth'].forEach(function(block) {
    describe(block, function() {
        beforeEach(function() {
            this.block = passport.block(block.toLowerCase());
        });

        describe('validate', function() {
            beforeEach(function() {
                sinon.stub(this.block, 'validationResult');
            });

            afterEach(function() {
                this.block.validationResult.restore();
            });

            it('should call validationResult with args (false, "missingvalue") if entered value is empty', function() {
                sinon.stub(this.block, 'val').returns('');
                this.block.validate();

                expect(this.block.validationResult.calledWith(false, 'missingvalue')).to.be(true);

                this.block.val.restore();
            });
        });
    });
});

describe('Password-auth', function() {
    beforeEach(function() {
        this.block = passport.block('password-auth');
    });

    describe('validate', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'validationResult');
        });

        afterEach(function() {
            this.block.validationResult.restore();
        });

        it('should call validationResult with args (true, "lang") if entered value has invalid characters', function() {
            sinon.stub(this.block, 'val').returns('пароль');
            this.block.validate();

            expect(this.block.validationResult.calledWith(true, 'lang')).to.be(true);

            this.block.val.restore();
        });
    });
});
