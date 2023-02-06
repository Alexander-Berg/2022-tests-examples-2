describe('Human-confirmation', function() {
    beforeEach(function() {
        this.block = passport.block('human-confirmation');
    });

    describe('onInit', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'showSwitch');
            sinon.stub(this.block, 'switchToCaptcha');
            sinon.stub(this.block, 'switchToPhone');
            sinon.stub(this.block, 'hintUpdated');
            sinon.stub(this.block, 'val');
        });

        afterEach(function() {
            this.block.showSwitch.restore();
            this.block.switchToCaptcha.restore();
            this.block.switchToPhone.restore();
            this.block.hintUpdated.restore();
            this.block.val.restore();
        });

        it('should call showSwitch', function() {
            this.block.onInit(this.block);
            expect(this.block.showSwitch.calledOnce).to.be(true);
        });

        describe('when value is "captcha"', function() {
            beforeEach(function() {
                this.block.options.value = 'captcha';
            });

            afterEach(function() {
                this.block.options.value = '';
            });

            it('should call switchToCaptcha', function() {
                this.block.onInit(this.block);
                expect(this.block.switchToCaptcha.calledOnce).to.be(true);
            });

            it('should not call switchToPhone', function() {
                this.block.onInit(this.block);
                expect(this.block.switchToPhone.called).to.be(false);
            });

            it('should call hintUpdated', function() {
                this.block.onInit(this.block);
                expect(this.block.hintUpdated.calledOnce).to.be(true);
            });
        });

        describe('when switch is in "phone" ', function() {
            beforeEach(function() {
                this.block.options.value = 'phone';
            });

            afterEach(function() {
                this.block.options.value = '';
            });

            it('should call switchToPhone', function() {
                this.block.onInit(this.block);
                expect(this.block.switchToPhone.calledOnce).to.be(true);
            });

            it('should not call switchToCaptcha', function() {
                this.block.onInit(this.block);
                expect(this.block.switchToCaptcha.called).to.be(false);
            });
        });
    });

    describe('validate', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'emit');

            var stubBlock = function(validateDeferred) {
                return {
                    validate: sinon.stub().returns(validateDeferred.promise()),
                    isEmpty: sinon.stub(),
                    emit: sinon.stub(),
                    val: sinon.stub
                };
            };

            this.questionValidateDeferred = new $.Deferred();
            this.question = stubBlock(this.questionValidateDeferred);

            this.userQuestionValidateDeferred = new $.Deferred();
            this.userQuestion = stubBlock(this.userQuestionValidateDeferred);

            this.answerValidateDeferred = new $.Deferred();
            this.answer = stubBlock(this.answerValidateDeferred);

            this.captchaValidateDeferred = new $.Deferred();
            this.captcha = stubBlock(this.captchaValidateDeferred);

            this.control = stubBlock(new $.Deferred());

            this.phoneConfirmValidateDeferred = new $.Deferred();
            this.phoneConfirm = stubBlock(this.phoneConfirmValidateDeferred);

            this.captchaGroup = [this.question, this.userQuestion, this.answer, this.captcha];

            this.captchaGroupDeferreds = [
                this.questionValidateDeferred,
                this.userQuestionValidateDeferred,
                this.answerValidateDeferred,
                this.captchaValidateDeferred
            ];

            sinon
                .stub(passport, 'block')
                .withArgs('question')
                .returns(this.question)
                .withArgs('user-question')
                .returns(this.userQuestion)
                .withArgs('answer')
                .returns(this.answer)
                .withArgs('captcha')
                .returns(this.captcha)
                .withArgs('control')
                .returns(this.control)
                .withArgs('phone-confirm')
                .returns(this.phoneConfirm);
        });
        afterEach(function() {
            this.block.emit.restore();
        });

        describe('when switch is in "phone"', function() {
            beforeEach(function() {
                this.block.val('phone');
            });

            afterEach(function() {
                passport.block.restore();
            });

            it('should call validate on the phone-confirm block', function() {
                this.block.validate();
                expect(this.phoneConfirm.validate.calledOnce).to.be(true);
            });

            it('should pass suppressError to phone-confirm', function() {
                this.block.validate(true);
                expect(this.phoneConfirm.validate.calledWithExactly(true)).to.be(true);
            });

            it("should resolve with true if phone-confirm's validate resolved with true", function(done) {
                this.phoneConfirmValidateDeferred.resolve(true);
                this.block.validate().then(function(result) {
                    expect(result).to.be(true);
                    done();
                });
            });

            it('should emit "validation, true" if phone-confirm\'s validate resolved with true', function() {
                this.phoneConfirmValidateDeferred.resolve(true);
                this.block.validate();
                expect(this.block.emit.calledWithExactly('validation', true)).to.be(true);
            });

            it("should resolve with false if phone-confirm's validate resolved with false", function(done) {
                this.phoneConfirmValidateDeferred.resolve(false);
                this.block.validate().then(function(result) {
                    expect(result).to.be(false);
                    done();
                });
            });

            it('should emit "validation, false" if phone-confirm\'s validate resolved with false', function() {
                this.phoneConfirmValidateDeferred.resolve(false);
                this.block.validate();
                expect(this.block.emit.calledWithExactly('validation', false)).to.be(true);
            });

            it("should not show errors of its own when phone-confirm's validate resolved with false", function() {
                this.phoneConfirmValidateDeferred.resolve(false);
                sinon.stub(this.block, 'error');

                this.block.validate();

                expect(this.block.error.called).to.be(false);

                this.block.error.restore();
            });
        });

        describe('when switch is in "captcha"', function() {
            beforeEach(function() {
                this.block.val('captcha');
            });

            afterEach(function() {
                passport.block.restore();
            });

            it('should call validate on the captcha-related children', function() {
                this.block.validate();
                this.captchaGroup.forEach(function(childBlock) {
                    expect(childBlock.validate.calledOnce).to.be(true);
                });
            });

            it("should pass suppressError to children's validate", function() {
                this.block.validate(true);
                this.captchaGroup.forEach(function(childBlock) {
                    expect(childBlock.validate.calledWithExactly(true)).to.be(true);
                });
            });

            it("should resolve with true if all related children's validate resolved with true", function(done) {
                this.captchaGroupDeferreds.forEach(function(deferred) {
                    deferred.resolve(true);
                });

                this.block.validate().then(function(result) {
                    expect(result).to.be(true);
                    done();
                });
            });

            it('should emit "validation, true" if all related children\'s validate resolved with true', function() {
                this.captchaGroupDeferreds.forEach(function(deferred) {
                    deferred.resolve(true);
                });

                this.block.validate();
                expect(this.block.emit.calledWithExactly('validation', true)).to.be(true);
            });

            it("should resolve with false if any child block's validate resolved with false", function(done) {
                for (var i = 0; i < this.captchaGroupDeferreds.length - 1; i++) {
                    var deferred = this.captchaGroupDeferreds[i];

                    deferred.resolve(true); //All except one resolve with true
                }
                //One resolves with false
                this.captchaGroupDeferreds[this.captchaGroupDeferreds.length - 1].resolve(false);

                this.block.validate().then(function(result) {
                    expect(result).to.be(false);
                    done();
                });
            });

            it('should emit "validation, false" if any child block\'s validate resolved with false', function() {
                for (var i = 0; i < this.captchaGroupDeferreds.length - 1; i++) {
                    var deferred = this.captchaGroupDeferreds[i];

                    deferred.resolve(true); //All except one resolve with true
                }
                //One resolves with false
                this.captchaGroupDeferreds[this.captchaGroupDeferreds.length - 1].resolve(false);

                this.block.validate();
                expect(this.block.emit.calledWithExactly('validation', false)).to.be(true);
            });

            it("should show no errors of its own when any child block's validate resolved with false", function() {
                for (var i = 0; i < this.captchaGroupDeferreds.length - 1; i++) {
                    var deferred = this.captchaGroupDeferreds[i];

                    deferred.resolve(true); //All except one resolve with true
                }
                //One resolves with false
                this.captchaGroupDeferreds[this.captchaGroupDeferreds.length - 1].resolve(false);

                sinon.stub(this.block, 'error');

                this.block.validate();

                expect(this.block.error.called).to.be(false);

                this.block.error.restore();
            });
        });
    });

    describe('hintUpdated', function() {
        beforeEach(function() {
            //There is a setTimeout in hintUpdated to change the priority of event handlers
            this.clock = sinon.useFakeTimers();

            this.trackedBlocks = [
                passport.block('question'),
                passport.block('user-question'),
                passport.block('answer')
            ];

            this.trackedBlocks.forEach(function(block) {
                sinon.stub(block, 'isEmpty').returns(false);
            });

            sinon.stub(this.block, 'showSwitch');
            sinon.stub(this.block, 'hideSwitch');
        });
        afterEach(function() {
            this.trackedBlocks.forEach(function(block) {
                block.isEmpty.restore();
            });

            this.block.showSwitch.restore();
            this.block.hideSwitch.restore();

            this.clock.restore();
        });

        it('should call isEmpty on question, user-question and answer', function() {
            this.block.hintUpdated();
            this.clock.tick(10);
            this.trackedBlocks.forEach(function(block) {
                expect(block.isEmpty.calledOnce).to.be(true);
            });
        });

        it("should call showSwitch if any of question, user-question or answer's isEmpty returns true", function() {
            this.trackedBlocks[1].isEmpty.returns(true);
            this.block.hintUpdated();
            this.clock.tick(10);
            expect(this.block.showSwitch.calledOnce).to.be(true);
            expect(this.block.hideSwitch.called).to.be(false);
        });

        it("should call hideSwitch if all of question, user-question and answer's isEmpty return false", function() {
            this.block.hintUpdated();
            this.clock.tick(10);
            expect(this.block.showSwitch.called).to.be(false);
            expect(this.block.hideSwitch.calledOnce).to.be(true);
        });
    });
});
