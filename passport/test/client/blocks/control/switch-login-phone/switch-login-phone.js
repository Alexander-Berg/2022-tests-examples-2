/* eslint-disable max-len */

/*
describe('Switch-login-phone', function() {

    beforeEach(function() {
        this.blockLoginPhone = passport.block('switch-login-phone');

        var stubBlock = function(validateDeferred) {
            return {
                validate: sinon.stub().returns(validateDeferred.promise()),
                emit: sinon.stub(),
                inited: {
                    already: true
                },
                val: sinon.stub().returns('aaa'),
                focus: sinon.stub(),
                error: sinon.stub(),
                isEmpty: sinon.stub()
            };
        };

        this.loginPresetValidateDeferred = new $.Deferred();
        this.loginPreset = stubBlock(this.loginPresetValidateDeferred);

        this.phoneConfirmValidateDeferred = new $.Deferred();
        this.phoneConfirm = stubBlock(this.phoneConfirmValidateDeferred);
        this.phoneConfirm.updatePhoneMask = sinon.stub();
        this.phoneConfirm.getModel  = sinon.stub().returns(null);

        sinon.stub(passport, 'block')
            .withArgs('login-preset').returns(this.loginPreset)
            .withArgs('phone-confirm').returns(this.phoneConfirm);

        this.blockLoginPhone.subBlocks.loginPreset = this.loginPreset;
        this.blockLoginPhone.subBlocks.phoneConfirm = this.phoneConfirm;
        sinon.stub(this.blockLoginPhone, 'emit');
    });
    afterEach(function() {
        this.blockLoginPhone.emit.restore();
        passport.block.restore();
    });


    describe('validate', function() {

        var blocks = [
            {
                name: 'phone-confirm',
                val: 'phone',
                control: 'phoneConfirm',
                deferred: 'phoneConfirmValidateDeferred'
            },
            {
                name: 'login-preset',
                val: 'login',
                control: 'loginPreset',
                deferred: 'loginPresetValidateDeferred'
            }
        ];

        blocks.forEach(function(block) {

            describe('when switch is in "' + block.val + '"', function() {
                beforeEach(function() {
                    this.blockLoginPhone.val(block.val);
                });

                it('should call validate on the ' + block.name + ' block', function() {
                    this.blockLoginPhone.validate();
                    expect(this[block.control].validate.calledOnce).to.be(true);
                });

                it('should pass suppressError to ' + block.name, function() {
                    this.blockLoginPhone.validate(true);
                    expect(this[block.control].validate.calledWithExactly(true)).to.be(true);
                });

                it('should resolve with true if ' + block.name + '\'s validate resolved with true', function(done) {
                    this[block.deferred].resolve(true);
                    this.blockLoginPhone.validate().then(function(result) {
                        expect(result).to.be(true);
                        done();
                    });
                });

                it('should emit "validation, true" if ' + block.name + '\'s validate resolved with true', function(done) {
                    const self = this;

                    self[block.deferred].resolve(true);
                    self.blockLoginPhone.validate().then(function(result) {
                        expect(self.blockLoginPhone.emit.calledWithExactly('validation', true)).to.be(true);
                        done();
                    });
                });

                it('should resolve with false if ' + block.name + '\'s validate resolved with false', function(done) {
                    this[block.deferred].resolve(false);
                    this.blockLoginPhone.validate().then(function(result) {
                        expect(result).to.be(false);
                        done();
                    });
                });

                it('should emit "validation, false" if ' + block.name + '\'s validate resolved with false', function(done) {
                    const self = this;

                    self[block.deferred].resolve(false);
                    self.blockLoginPhone.validate().then(function(result) {
                        expect(self.blockLoginPhone.emit.calledWithExactly('validation', false)).to.be(true);
                        done();
                    });
                });

                it('should not show error when ' + block.name + '\'s validate resolved with false, but suppressErrors passed', function() {
                    this[block.deferred].resolve(false);
                    sinon.stub(this.blockLoginPhone, 'error');

                    this.blockLoginPhone.validate(true);
                    expect(this.blockLoginPhone.error.called).to.be(false);

                    this.blockLoginPhone.error.restore();
                });
            });
        });

        it('when switch is in pnone and phone is confirmed should call validate in login-preset block', function() {
            this.blockLoginPhone.val('phone');
            this.phoneConfirm.getModel.returns({
                isConfirmed: sinon.stub().returns(true)
            });

            this.blockLoginPhone.validate();
            expect(this.loginPreset.validate.calledOnce).to.be(true);
        });
    });

    describe('switcherLoginPhone', function() {

        describe('when switch to phone', function() {
            beforeEach(function() {
                this.blockLoginPhone.val('login');
                sinon.stub(this.blockLoginPhone, 'switchToPhone');

            });
            afterEach(function() {
                this.blockLoginPhone.switchToPhone.restore();
                this.phoneConfirm.isEmpty.returns(false);

            });

            it('should not call if val not equal login', function() {
                this.blockLoginPhone.val('phone');
                this.blockLoginPhone.switcherLoginPhone({}, {}, ['startswithdigit']);
                expect(this.blockLoginPhone.switchToPhone.called).to.be(false);
            });

            it('should call #switchToPhone if "startwithdigit" error', function() {
                this.phoneConfirm.isEmpty.returns(true);
                this.blockLoginPhone.switcherLoginPhone({}, {}, ['startswithdigit']);
                expect(this.blockLoginPhone.switchToPhone.calledOnce).to.be(true);

            });

            it('should call #switchToPhone if "prohibitedsymbols" error and login val start from "+"', function() {
                this.phoneConfirm.isEmpty.returns(true);
                this.loginPreset.val.returns('+');
                this.blockLoginPhone.switcherLoginPhone({}, {}, ['prohibitedsymbols']);
                expect(this.blockLoginPhone.switchToPhone.calledOnce).to.be(true);

            });

            it('should not call #swithcToPhone if #isSubBlocksInited return false', function() {
                sinon.stub(this.blockLoginPhone, 'isSubBlocksInited').returns(false);

                this.blockLoginPhone.switcherLoginPhone({}, {}, ['startswithdigit']);
                expect(this.blockLoginPhone.switchToPhone.called).to.be(false);

                this.blockLoginPhone.isSubBlocksInited.restore();
            });
        });

        describe('when switch to login', function() {
            beforeEach(function() {
                sinon.stub(this.blockLoginPhone, 'switchToLogin');

            });
            afterEach(function() {
                this.blockLoginPhone.switchToLogin.restore();
            });

            it('should not call if val not equal login', function() {
                this.blockLoginPhone.val('login');
                this.blockLoginPhone.switcherLoginPhone();
                expect(this.blockLoginPhone.switchToLogin.called).to.be(false);
            });

            it('should call if val equal empty string', function() {
                this.phoneConfirm.isEmpty.returns(true);

                this.blockLoginPhone.val('phone');
                this.phoneConfirm.val.returns('');
                this.blockLoginPhone.switcherLoginPhone();
                expect(this.blockLoginPhone.switchToLogin.calledOnce).to.be(true);

                this.phoneConfirm.isEmpty.returns(false);

            });

            it('should not call #swithcToLogin if #isSubBlocksInited return false', function() {
                sinon.stub(this.blockLoginPhone, 'isSubBlocksInited').returns(false);

                this.blockLoginPhone.val('phone');
                this.blockLoginPhone.switcherLoginPhone();
                expect(this.blockLoginPhone.switchToLogin.called).to.be(false);

                this.blockLoginPhone.isSubBlocksInited.restore();
            });
        });

    });
/*
    describe('switchToPhone', function() {
        beforeEach(function() {
            this.$loginPresetOld = this.blockLoginPhone.$loginPreset;
            this.$phoneConfirmOld = this.blockLoginPhone.$phoneConfirm;
            this.blockLoginPhone.$loginPreset = {
                addClass: sinon.stub(),
                removeClass: sinon.stub()
            };
            this.blockLoginPhone.$phoneConfirm = {
                addClass: sinon.stub(),
                removeClass: sinon.stub()
            };
        });
        afterEach(function() {
            this.blockLoginPhone.$loginPreset = this.$loginPresetOld;
            this.blockLoginPhone.$phoneConfirm = this.$phoneConfirmOld;
        });

        it('should called once phoneConfirm.error', function() {
            this.blockLoginPhone.switchToPhone();
            expect(this.phoneConfirm.error.called).to.be(true);
        });

        it('should called $loginPreset.addClass() with correct params', function() {
            this.blockLoginPhone.switchToPhone();
            expect(this.blockLoginPhone.$loginPreset.addClass.calledWithExactly('g-hidden')).to.be(true);
        });

        it('should called $phoneConfirm.removeClass() with correct params', function() {
            this.blockLoginPhone.switchToPhone();
            expect(this.blockLoginPhone.$phoneConfirm.removeClass.calledWithExactly('g-hidden')).to.be(true);
        });

        it('should called #phoneConfirm.val() with correct params', function() {
            var loginValues = [
                ['+7ololo', '+7'],
                ['7oooooo', '7'],
                ['7ldkj990alsdkj00', '799000'],
                ['8+ljkkjj-', '8']
            ];
            loginValues.forEach(function(a) {
                this.loginPreset.val.returns(a[0])
                this.blockLoginPhone.switchToPhone();
                expect(this.phoneConfirm.val.calledWithExactly(a[1])).to.be(true);
            }.bind(this));
        });



        it('should called once #phoneConfirm.focus', function() {
            this.blockLoginPhone.switchToPhone();
            expect(this.phoneConfirm.focus.calledOnce).to.be(true);
        });

        it('should called once "phoneConfirm.focus()" before "phoneConfirm.val()"', function() {
            this.blockLoginPhone.switchToPhone();
            expect(this.phoneConfirm.focus.calledBefore(this.phoneConfirm.val)).to.be(true);
        });

        it('should called once #phoneConfirm.updatePhoneMask', function() {
            this.blockLoginPhone.switchToPhone();
            expect(this.phoneConfirm.updatePhoneMask.calledOnce).to.be(true);
        });

        it('should called once #emit with params "showPhone"', function() {
            this.blockLoginPhone.switchToPhone();
            expect(this.blockLoginPhone.emit.calledWithExactly('showPhone')).to.be(true);
        });

        it('should val equal "phone"', function() {
            this.blockLoginPhone.val('login');
            this.blockLoginPhone.switchToPhone();
            expect(this.blockLoginPhone.val()).to.be('phone');
        });


        it('should called #validate with params true ', function() {
            sinon.stub(this.blockLoginPhone, 'validate');

            this.blockLoginPhone.switchToPhone();
            expect(this.blockLoginPhone.validate.calledWithExactly(true)).to.be(true);

            this.blockLoginPhone.validate.restore();
        });
    });

    describe('switchToLogin', function() {
        beforeEach(function() {
            this.$loginPresetOld = this.blockLoginPhone.$loginPreset;
            this.$phoneConfirmOld = this.blockLoginPhone.$phoneConfirm;
            this.blockLoginPhone.$loginPreset = {
                addClass: sinon.stub(),
                removeClass: sinon.stub()
            };
            this.blockLoginPhone.$phoneConfirm = {
                addClass: sinon.stub(),
                removeClass: sinon.stub()
            };
            this.loginPreset.loginBlock = {
                loginRequirements: {
                    addClass: sinon.stub()
                }
            };
        });
        afterEach(function() {
            this.blockLoginPhone.$loginPreset = this.$loginPresetOld;
            this.blockLoginPhone.$phoneConfirm = this.$phoneConfirmOld;
        });

        it('should called once loginPreset.error', function() {
            this.blockLoginPhone.switchToLogin();
            expect(this.loginPreset.error.calledOnce).to.be(true);
        });

        it('should called $loginPreset.addClass() with correct params', function() {
            this.blockLoginPhone.switchToLogin();
            expect(this.blockLoginPhone.$phoneConfirm.addClass.calledWithExactly('g-hidden')).to.be(true);
        });

        it('should called $phoneConfirm.removeClass() with correct params', function() {
            this.blockLoginPhone.switchToLogin();
            expect(this.blockLoginPhone.$loginPreset.removeClass.calledWithExactly('g-hidden')).to.be(true);
        });

        it('should called #loginPreset.val() with correct params', function() {
            this.blockLoginPhone.switchToLogin();
            expect(this.loginPreset.val.calledWithExactly('')).to.be(true);
        });

        it('should called once #loginPreset.focus', function() {
            this.blockLoginPhone.switchToLogin();
            expect(this.loginPreset.focus.calledOnce).to.be(true);
        });

        it('should called once #emit with params "hidePhone"', function() {
            this.blockLoginPhone.switchToLogin();
            expect(this.blockLoginPhone.emit.calledWithExactly('hidePhone')).to.be(true);
        });

        it('should val equal "phone"', function() {
            this.blockLoginPhone.val('phone');
            this.blockLoginPhone.switchToLogin();
            expect(this.blockLoginPhone.val()).to.be('login');
        });


        it('should called #validate with params true ', function() {
            sinon.stub(this.blockLoginPhone, 'validate');

            this.blockLoginPhone.switchToPhone();
            expect(this.blockLoginPhone.validate.calledWithExactly(true)).to.be(true);

            this.blockLoginPhone.validate.restore();
        });
    });
});
*/
