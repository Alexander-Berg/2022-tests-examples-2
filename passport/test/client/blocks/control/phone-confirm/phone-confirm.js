describe('Phone-confirm', function() {
    var subblocks = ['entry', 'code', 'acknowledgement'];

    beforeEach(function() {
        this.block = passport.block('phone-confirm');

        this.PhoneModel = this.block.PhoneModel;

        this.unsanitized = ' 8 (913) 910 65-15 ';
        this.maxSendings = 3;
        this.maxConfirmations = 5;
        this.confirmationCode = '1234';

        this.model = new this.PhoneModel(this.unsanitized);
        this.model.setMode(new this.PhoneModel.Mode());
    });

    describe('PhoneModel', function() {
        beforeEach(function() {
            this.requestDeferred = new $.Deferred();
            this.request = sinon.stub().returns(this.requestDeferred);

            this.model
                .setSendingsLeft(this.maxSendings)
                .setConfirmationsLeft(this.maxConfirmations)
                .setRequest(this.request);

            this.clock = sinon.useFakeTimers();

            this.apiResponses = {
                /**
                 * Phone bundle response for the successful submit/commit
                 * @see http://wiki.yandex-team.ru/passport/python/api/bundle/phone#primeruspeshnogootveta
                 *
                 * Has additional "now" field set with the current frontend server time
                 */
                successful: {
                    status: 'ok',
                    number: {
                        international: '+7 916 123-45-67',
                        e164: '+79161234567',
                        original: '+79161234567'
                    },
                    deny_resend_until: Math.round($.now() / 1000) + 50, //Server responds with unix timestamp
                    now: $.now()
                },

                /**
                 * Phone bundle response for the failed commit/submit
                 * @see http://wiki.yandex-team.ru/passport/python/api/bundle/phone#primerotvetasoshibkojj
                 */
                failed: {
                    status: 'error',
                    errors: ['code.invalid']
                }
            };
        });

        afterEach(function() {
            this.clock.restore();
        });

        describe('Constructor', function() {
            _.each(
                {
                    'an empty string': '',
                    'a number': 1,
                    'a boolean': true,
                    'an array': [],
                    'an object': {}
                },
                function(value, description) {
                    it('should throw if unsanitizedNumber is ' + description, function() {
                        var that = this;

                        expect(function() {
                            new that.PhoneModel(value);
                        }).to.throwException(/Unsanitized number should be a string/);
                    });
                }
            );
        });

        describe('sendCode', function() {
            it('should return a jquery promise', function() {
                expect(this.model.sendCode()).to.be.aJqueryDeferredPromise();
            });

            it('should request the code from api', function() {
                this.model.sendCode();
                expect(this.request.calledOnce).to.be(true);
            });

            it('should call the "phone-confirm-code-submit" method of the api', function() {
                this.model.sendCode();
                expect(this.request.calledWith('phone-confirm-code-submit')).to.be(true);
            });

            it('should pass the unsanitized phone number to the api', function() {
                this.model.sendCode();
                expect(this.request.firstCall.args[1]).to.have.property('number', this.unsanitized);
            });

            it('should throw if maximum number of retries is already reached', function() {
                sinon.stub(this.model, 'getSendingsLeft').returns(0);

                var model = this.model;

                expect(function() {
                    model.sendCode();
                }).to.throwException(/Maximum allowed codes sent\. No more retries allowed\./);
            });

            it('should wait for the timeout before sending another request', function() {
                var getTimeout = sinon.stub(this.model, 'getTimeout').returns(10);

                this.model.sendCode();
                expect(this.request.called).to.be(false);

                getTimeout.returns(0);
                this.clock.tick(10000);
                expect(this.request.calledOnce).to.be(true);
            });

            it('should only send one request if two calls were made during timeout', function() {
                var getTimeout = sinon.stub(this.model, 'getTimeout').returns(10);

                this.model.sendCode();
                this.model.sendCode();

                getTimeout.returns(0);
                this.clock.tick(10000);

                expect(this.request.calledOnce).to.be(true);
            });

            it('should reject the promise with errors api returned', function(done) {
                var apiErrors = ['code.invalid', 'number.invalid'];

                this.model
                    .sendCode()
                    .fail(function(errors) {
                        expect(errors).to.eql(apiErrors);
                        done();
                    })
                    .done(asyncFail(done, 'Expected the promise to be rejected'));

                this.requestDeferred.resolve($.extend({}, this.apiResponses.failed, {errors: apiErrors}));
            });

            it('should resolve if the api returned a successful response', function(done) {
                this.model
                    .sendCode()
                    .done(done)
                    .fail(asyncFail(done, 'Expected the promise to resolve'));

                this.requestDeferred.resolve(this.apiResponses.successful);
            });

            it('should make isCodeSent return true if the api returned a successful response', function(done) {
                var model = this.model;

                expect(model.isCodeSent()).to.be(false);

                model
                    .sendCode()
                    .done(function() {
                        expect(model.isCodeSent()).to.be(true);
                        done();
                    })
                    .fail(asyncFail(done, 'Expected the promise to resolve'));

                this.requestDeferred.resolve(this.apiResponses.successful);
            });

            it('should resolve if the api returned a single "phone.confirmed" error', function(done) {
                var model = this.model;

                expect(model.isCodeSent()).to.be(false);

                this.model
                    .sendCode()
                    .done(function() {
                        expect(model.isCodeSent()).to.be(true);
                        done();
                    })
                    .fail(asyncFail(done, 'Expected the promise to resolve'));

                this.requestDeferred.resolve($.extend({}, this.apiResponses.failed, {errors: ['phone.confirmed']}));
            });

            it('should make codeIsSent return true if the api returned a single ' + '"phone.confirmed" error', function(
                done
            ) {
                this.model
                    .sendCode()
                    .done(done)
                    .fail(asyncFail(done, 'Expected the promise to resolve'));

                this.requestDeferred.resolve($.extend({}, this.apiResponses.failed, {errors: ['phone.confirmed']}));
            });

            it('should save the sanitized code returned from api so that getSanitized returns it', function() {
                this.model.sendCode();
                this.requestDeferred.resolve(this.apiResponses.successful);
                expect(this.model.getSanitized()).to.be(this.apiResponses.successful.number.international);
            });

            it('should resolve instantly if the phone is already confirmed', function() {
                sinon.stub(this.model, 'isConfirmed').returns(true);
                expect(this.model.sendCode().state()).to.be('resolved');
            });

            it('should set sendings value to 0 if api responded with "smslimit.exceeded"', function(done) {
                var model = this.model;

                model
                    .sendCode()
                    .fail(function() {
                        expect(model.getSendingsLeft()).to.be(0);
                        done();
                    })
                    .done(asyncFail(done, 'Expected the promise to be rejected'));

                this.requestDeferred.resolve($.extend({}, this.apiResponses.failed, {errors: ['smslimit.exceeded']}));
            });
        });

        describe('confirmCode', function() {
            it('should return a jquery promise', function() {
                expect(this.model.confirmCode(this.confirmationCode)).to.be.aJqueryDeferredPromise();
            });

            it('should request the confirmation from api', function() {
                this.model.confirmCode(this.confirmationCode);
                expect(this.request.calledOnce).to.be(true);
            });

            it('should call the "phone-confirm-code" method of the api', function() {
                this.model.confirmCode(this.confirmationCode);
                expect(this.request.calledWith('phone-confirm-code')).to.be(true);
            });

            it('should pass the confirmation code to the api', function() {
                this.model.confirmCode(this.confirmationCode);
                expect(this.request.firstCall.args[1]).to.have.property('code', this.confirmationCode);
            });

            it('should throw if maximum number of confirmations already reached', function() {
                sinon.stub(this.model, 'getConfirmationsLeft').returns(0);

                var model = this.model;
                var confirmation = this.confirmationCode;

                expect(function() {
                    //No more confirmations allowed at this point — should throw.
                    model.confirmCode(confirmation);
                }).to.throwException(/Maximum allowed confirmations done\. No more allowed\./);
            });

            it('should resolve with true if api call is successful', function(done) {
                this.model
                    .confirmCode(this.confirmationCode)
                    .done(function(result) {
                        expect(result).to.be(true);
                        done();
                    })
                    .fail(asyncFail(done, 'Expected the promise to resolve'));

                this.requestDeferred.resolve(this.apiResponses.successful);
            });

            it('should reject with errors if api returned a single "code.invalid" error', function(done) {
                var apiErrors = ['code.invalid'];

                this.model
                    .confirmCode(this.confirmationCode)
                    .fail(function(errors) {
                        expect(errors).to.eql(apiErrors);
                        done();
                    })
                    .done(asyncFail(done, 'Expected the promise to be rejected'));

                this.requestDeferred.resolve($.extend({}, this.apiResponses.failed, {errors: apiErrors}));
            });

            it('should resolve with true if the code is already confirmed', function(done) {
                sinon.stub(this.model, 'isConfirmed').returns(true);

                this.model
                    .confirmCode(this.confirmationCode)
                    .done(function(result) {
                        expect(result).to.be(true);
                        done();
                    })
                    .fail(asyncFail(done, 'Expected the promise to resolve'));
            });

            it('should not call the api if the code is already confirmed', function() {
                sinon.stub(this.model, 'isConfirmed').returns(true);

                this.model.confirmCode(this.confirmationCode);
                expect(this.request.called).to.be(false);
            });

            it(
                'should affect the state so that isConfirmed returns true after the request ' +
                    'was successfully confirmed',
                function() {
                    this.model.confirmCode(this.confirmationCode);
                    this.requestDeferred.resolve(this.apiResponses.successful);

                    expect(this.model.isConfirmed()).to.be(true);
                }
            );

            it(
                'should reject the promise with errors api returned, if those errors are anything ' +
                    'but a single "code.invalid"',
                function(done) {
                    var apiErrors = ['number.invalid', 'captcha.required'];

                    this.model
                        .confirmCode(this.confirmationCode)
                        .fail(function(errors) {
                            expect(errors).to.eql(apiErrors);
                            done();
                        })
                        .done(asyncFail(done, 'Expected the promise to be rejected'));

                    this.requestDeferred.resolve($.extend({}, this.apiResponses.failed, {errors: apiErrors}));
                }
            );

            it(
                'should set confirmationsLeft value to 0 if api responded with ' + '"confirmations_limit.exceeded"',
                function(done) {
                    var model = this.model;

                    model
                        .confirmCode(this.confirmationCode)
                        .fail(function() {
                            expect(model.getConfirmationsLeft()).to.be(0);
                            done();
                        })
                        .done(asyncFail(done, 'Expected the promise to be rejected'));

                    this.requestDeferred.resolve(
                        $.extend({}, this.apiResponses.failed, {errors: ['confirmations_limit.exceeded']})
                    );
                }
            );
        });

        describe('getUnsanitized', function() {
            it('should return the unsanitized number the model was created with', function() {
                expect(this.model.getUnsanitized()).to.be(this.unsanitized);
            });
        });

        describe('getSendingsLeft', function() {
            it('should decrease after the code was sent successfuly', function() {
                this.model.sendCode();
                this.requestDeferred.resolve(this.apiResponses.successful);

                expect(this.model.getSendingsLeft()).to.be(this.maxSendings - 1);
            });
        });

        describe('getConfirmationsLeft', function() {
            it('should decrease after the code confirmation attempt', function() {
                this.model.confirmCode(this.confirmationCode);
                this.requestDeferred.resolve(this.apiResponses.failed); //Code.invalid

                expect(this.model.getConfirmationsLeft()).to.be(this.maxConfirmations - 1);
            });
        });

        describe('getTimeout', function() {
            it('should return 0 if no codes had been sent yet', function() {
                expect(this.model.getTimeout()).to.be(0);
            });

            it(
                'should return the difference between now and the next allowed timestamp ' + 'returned from server',
                function() {
                    this.model.sendCode();
                    this.requestDeferred.resolve(this.apiResponses.successful);

                    expect(this.model.getTimeout()).to.be(
                        this.apiResponses.successful.deny_resend_until * 1000 - $.now()
                    );
                }
            );

            it('should offset for the difference between user time and server time', function() {
                this.model.sendCode();

                var now = $.now();
                var offset = 3000;

                this.requestDeferred.resolve(
                    $.extend({}, this.apiResponses.successful, {now: now - offset /*Server timestamp*/})
                );
                expect(this.model.getTimeout()).to.be(
                    this.apiResponses.successful.deny_resend_until * 1000 - now + offset
                );
            });

            it('should return 0 if timeout has passed (is negative)', function() {
                this.model.sendCode();
                this.requestDeferred.resolve(this.apiResponses.successful);

                this.clock.tick(100000);
                expect(this.model.getTimeout()).to.be(0);
            });
        });

        describe('setTimeout', function() {
            _.each(
                {
                    'a string': '123',
                    'a boolean': true,
                    'an array': [],
                    'an object': {}
                },
                function(value, description) {
                    it('should throw if the timeout is ' + description, function() {
                        var model = this.model;

                        expect(function() {
                            model.setTimeout(value);
                        }).to.throwException(/Timeout should be a number/);
                    });
                }
            );

            it('should set timeout for the model', function() {
                var timeout = 12345;

                this.model.setTimeout(timeout);
                expect(this.model.getTimeout()).to.be(timeout);
            });
        });
    });

    describe('PhoneManager', function() {
        beforeEach(function() {
            this.manager = new this.block.PhoneManager(this.PhoneModel);
            this.clock = sinon.useFakeTimers();
        });

        afterEach(function() {
            this.clock.restore();
        });

        describe('getModel', function() {
            _.each(
                {
                    'an empty string': '',
                    'a number': 1,
                    'a boolean': true,
                    'an array': [],
                    'an object': {}
                },
                function(value, description) {
                    it('should throw if unsanitized number is ' + description, function() {
                        var manager = this.manager;

                        expect(function() {
                            manager.getModel(value);
                        }).to.throwException(/Unsanitized number should be a string/);
                    });
                }
            );

            it('should return a phoneModel', function() {
                expect(this.manager.getModel(this.unsanitized)).to.be.a(this.PhoneModel);
            });

            it('should return a model for the given unsanitized number', function() {
                expect(this.manager.getModel(this.unsanitized).getUnsanitized()).to.be(this.unsanitized);
            });

            it('should return a previous model for the given unsanitized number, if it exists', function() {
                var firstModel = this.manager.getModel(this.unsanitized);

                this.manager.getModel('123123123123');
                expect(this.manager.getModel(this.unsanitized)).to.be(firstModel);
            });

            it('should update a timeout on a new model, if previous model has it', function() {
                var timeout = 1337;
                var firstModel = this.manager.getModel(this.unsanitized);

                sinon.stub(firstModel, 'getTimeout').returns(timeout);

                expect(this.manager.getModel('123123123').getTimeout()).to.be(timeout);
            });

            it('should abort the timeout on a previously active model', function() {
                var timeout = 1337;
                var firstModel = this.manager.getModel(this.unsanitized);

                sinon.stub(firstModel, 'getTimeout').returns(timeout);
                sinon.stub(firstModel, 'clearTimeout');

                this.manager.getModel('123123123');
                expect(firstModel.clearTimeout.calledOnce).to.be(true);
            });
        });

        describe('getActive', function() {
            it('should return the last active model', function() {
                this.manager.getModel('123123123');
                var active = this.manager.getModel(this.unsanitized);

                expect(this.manager.getActive()).to.be(active);
            });
        });
    });

    describe('Main view', function() {
        beforeEach(function() {
            this.originalPhoneModelInstance = this.block.currentPhone;
            this.block.currentPhone = null; //Reset

            this.domEvent = {
                preventDefault: sinon.stub()
            };
        });

        afterEach(function() {
            this.block.currentPhone = this.originalPhoneModelInstance;
        });

        describe('Init', function() {
            it('should create a phoneManager', function() {
                this.block.init();
                expect(this.block.phoneManager).to.be.a(this.block.PhoneManager);
            });

            describe('with options', function() {
                beforeEach(function() {
                    $.each(this.block.subBlocks, function(subblock) {
                        var deferred = new $.Deferred();

                        subblock.inited = deferred;
                        deferred.resolve(subblock);
                    });

                    sinon.stub(this.block, 'emit');
                    sinon.stub(this.block, 'show');
                    sinon.stub(this.block.subBlocks.entry, 'val').returns('number');
                });

                afterEach(function() {
                    this.block.subBlocks.entry.val.restore();
                    this.block.emit.restore();
                    this.block.show.restore();
                });

                // it('should show acknowledgement if state is confirmed', function() {
                //     this.block.init({state: 'confirmed'});
                //     expect(this.block.show.calledWithExactly('acknowledgement')).to.be(true);
                // });

                it('should not show acknowledgement if state is not confirmed', function() {
                    this.block.init();
                    expect(this.block.show.called).to.be(false);
                });
            });
        });

        describe('Communication with sub-blocks', function() {
            /**
             * Listening to $(document) is pretty ugly.
             * //TODO: remove $(document) from event listening tests
             */

            var communicationEvents = [
                'restart',
                'phoneEntered',
                'phoneConfirmed',
                'couldNotSend',
                'sendingLimitReached',
                'confirmationsLimitReached'
            ];
            var getSubblock = function(block, name) {
                return block.subBlocks[name];
            };

            beforeEach(function() {
                var block = this.block;

                communicationEvents.forEach(function(event) {
                    sinon.stub(block, event);
                });
            });
            afterEach(function() {
                var block = this.block;

                communicationEvents.forEach(function(event) {
                    block[event].restore();
                });
            });

            subblocks.forEach(function(subblock) {
                communicationEvents.forEach(function(event) {
                    it(
                        'should call this.' + event + ' method when "' + subblock + '" sub-block emits "' + event + '"',
                        function() {
                            getSubblock(this.block, subblock).emit(event);
                            expect(this.block[event].calledOnce).to.be(true);
                        }
                    );

                    it(
                        'should intercept the "' +
                            event +
                            '" from "' +
                            subblock +
                            '" sub-block, so that other blocks do not get it',
                        function() {
                            var spy = sinon.spy();

                            $(document).on(event + '.all', spy);

                            getSubblock(this.block, subblock).emit(event);
                            expect(spy.called).to.be(false);

                            $(document).off(event + '.all', spy);
                        }
                    );
                });

                it(
                    'should allow other events to propagate from "' + subblock + '" subblock without interception',
                    function() {
                        var spy = sinon.spy();

                        $(document).on('otherEvents.all', spy);

                        getSubblock(this.block, subblock).emit('otherEvents');
                        expect(spy.called).to.be(true);

                        $(document).off('otherEvents.all', spy);
                    }
                );
            });
        });

        describe('setModel', function() {
            beforeEach(function() {
                this.originalModel = this.block.currentPhone;
            });
            afterEach(function() {
                this.block.currentPhone = this.originalModel;
            });

            ['code', 'acknowledgement'].forEach(function(subblock) {
                it('should set the model for the ' + subblock + ' subblock', function() {
                    subblock = this.block.subBlocks[subblock];
                    sinon.stub(subblock, 'setModel');

                    this.block.setModel(this.model);
                    expect(subblock.setModel.calledWithExactly(this.model)).to.be(true);

                    subblock.setModel.restore();
                });
            });
        });

        describe('validate', function() {
            beforeEach(function() {
                var block = this.block;

                subblocks.forEach(function(subblock) {
                    sinon.spy(block.subBlocks[subblock], 'validate');
                });

                this.initedAlready = block.inited.already;
                this.isRequired = block.isRequired;
                this.skipEntryValidation = block.skipEntryValidation;
                this.hasConfirmedPhone = block.options.hasConfirmedPhone;

                block.inited.already = true;
                block.isRequired = true;
                block.skipEntryValidation = false;
                block.options.hasConfirmedPhone = false;

                sinon.stub(block, 'emit');
                sinon.stub(block, 'error');

                sinon.stub(block.phoneManager, 'getActive');
            });
            afterEach(function() {
                var block = this.block;

                subblocks.forEach(function(subblock) {
                    block.subBlocks[subblock].validate.restore();
                });

                block.inited.already = this.initedAlready;
                block.isRequired = this.isRequired;
                block.skipEntryValidation = this.skipEntryValidation;
                block.options.hasConfirmedPhone = this.hasConfirmedPhone;

                block.emit.restore();
                block.error.restore();
                block.phoneManager.getActive.restore();
            });

            it('should call "validate" on phone-entry subblock', function() {
                var block = this.block;

                block.validate();

                expect(block.subBlocks['entry'].validate.calledOnce).to.be(true);
            });

            it('should pass "suppressError" argument to phone-entry subblock\'s validate', function() {
                var suppressError = 'Should be passed no matter what';

                var block = this.block;

                block.validate(suppressError);
                expect(block.subBlocks.entry.validate.calledWithExactly(suppressError)).to.be(true);
            });

            it("shouldn't validate phone-entry if block already has confirmed phone", function() {
                var block = this.block;

                var hasConfirmedPhone = block.options.hasConfirmedPhone;

                block.options.hasConfirmedPhone = true;

                block.validate();
                expect(block.subBlocks.entry.validate.called).to.be(false);

                if (hasConfirmedPhone !== undefined) {
                    block.options.hasConfirmedPhone = hasConfirmedPhone;
                } else {
                    delete block.options.hasConfirmedPhone;
                }
            });

            it("shouldn't validate phone-entry if block has skipEntryValidation flag", function() {
                var block = this.block;

                var skipEntryValidation = block.skipEntryValidation;

                block.skipEntryValidation = true;

                block.validate();
                expect(block.subBlocks.entry.validate.called).to.be(false);

                if (skipEntryValidation !== undefined) {
                    block.skipEntryValidation = skipEntryValidation;
                } else {
                    delete block.skipEntryValidation;
                }
            });

            it('should emit "validation, false" if there is no active phone model present', function() {
                this.block.phoneManager.getActive.returns(null);
                this.block.validate();
                expect(this.block.emit.calledWithExactly('validation', false)).to.be(true);
            });

            it('should resolve with false if there is no phone model present', function(done) {
                this.block.phoneManager.getActive.returns(null);
                this.block.validate().then(function(result) {
                    expect(result).to.be(false);
                    done();
                });
            });

            it('should emit "validation, false" if there is a phone model, but it it not confirmed', function() {
                this.block.phoneManager.getActive.returns(this.model);
                this.block.validate();
                expect(this.block.emit.calledWithExactly('validation', false)).to.be(true);
            });

            it('should resolve with false if there is a phone model, but it it not confirmed', function(done) {
                this.block.phoneManager.getActive.returns(this.model);
                this.block.validate().then(function(result) {
                    expect(result).to.be(false);
                    done();
                });
            });

            it('should emit "validation, true" if the phone model is confirmed', function() {
                sinon.stub(this.model, 'isConfirmed').returns(true);
                this.block.phoneManager.getActive.returns(this.model);

                this.block.validate();
                expect(this.block.emit.calledWithExactly('validation', true)).to.be(true);
            });

            it('should resolve with true if the phone model is confirmed', function(done) {
                sinon.stub(this.model, 'isConfirmed').returns(true);
                this.block.phoneManager.getActive.returns(this.model);

                this.block.validate().then(function(result) {
                    expect(result).to.be(true);
                    done();
                });
            });

            it('should not trigger this.error if suppressError is truthy', function() {
                this.block.validate(true);
                expect(this.block.error.called).to.be(false);
            });

            it('should trigger this.error if suppressError is falsey', function() {
                this.block.validate(false);
                expect(this.block.error.calledOnce).to.be(true);
            });

            it(
                'should trigger this.error with "needsconfirmation" if the model is not ' +
                    'confirmed and suppressError is falsey',
                function() {
                    this.block.validate(false);
                    expect(this.block.error.calledWithExactly('needsconfirmation')).to.be(true);
                }
            );

            it('should trigger this.error with null if the model confirmed and suppressError is falsey', function() {
                sinon.stub(this.model, 'isConfirmed').returns(true);
                this.block.phoneManager.getActive.returns(this.model);

                this.block.validate(false);
                expect(this.block.error.calledWithExactly(null)).to.be(true);
            });
        });

        describe('validate not required', function() {
            beforeEach(function() {
                sinon.stub(this.block, 'emit');
                sinon.stub(this.block.phoneManager, 'getActive');

                this.isRequired = this.block.isRequired;
                this.initedAlready = this.block.inited.already;

                this.block.isRequired = false;
                this.block.inited.already = true;

                this.block.phoneManager.getActive.returns(null);
            });
            afterEach(function() {
                this.block.isRequired = this.isRequired;

                this.block.emit.restore();
                this.block.phoneManager.getActive.restore();
            });

            it('should emit "validation, true" if not required', function() {
                this.block.validate();
                expect(this.block.emit.calledWithExactly('validation', true)).to.be(true);
            });

            it('should resolve with true if not required', function(done) {
                this.block.validate().then(function(result) {
                    expect(result).to.be(true);
                    done();
                });
            });
        });

        describe('phoneEntered', function() {
            beforeEach(function() {
                this.sendingDeferred = new $.Deferred();
                this.originalModel = this.block.currentPhone;

                sinon.stub(this.model, 'sendCode').returns(this.sendingDeferred);
                sinon.stub(this.block, 'PhoneModel').returns(this.model);
                sinon.stub(this.block.phoneManager, 'getModel').returns(this.model);
                sinon.stub(this.block, 'show');
                sinon.stub(this.block, 'startSendingFeedback');
                sinon.stub(this.block, 'stopSendingFeedback');
                sinon.spy(this.block, 'setModel');
            });
            afterEach(function() {
                this.block.PhoneModel.restore();
                this.block.show.restore();
                this.block.setModel.restore();
                this.block.phoneManager.getModel.restore();
                this.block.startSendingFeedback.restore();
                this.block.stopSendingFeedback.restore();

                this.block.currentPhone = this.originalModel;
            });

            it('should call phoneManager.getModel with the passed phone number', function() {
                this.block.phoneEntered(this.unsanitized);
                expect(this.block.phoneManager.getModel.calledWithExactly(this.unsanitized)).to.be(true);
            });

            describe('when the code was not sent for the model', function() {
                beforeEach(function() {
                    sinon.stub(this.model, 'isCodeSent').returns(false);
                    this.block.phoneEntered(this.unsanitized);
                });

                it('should store the new model', function() {
                    expect(this.block.setModel.calledWithExactly(this.model)).to.be(true);
                });

                it('should send the code for the new model', function() {
                    expect(this.model.sendCode.calledOnce).to.be(true);
                });

                it('should trigger this.show with "code" after the code was sent successfully', function() {
                    expect(this.block.show.called).to.be(false);
                    this.sendingDeferred.resolve();
                    expect(this.block.show.calledOnce).to.be(true);
                });

                it('should trigger this.couldNotSend if sending failed', function() {
                    sinon.stub(this.block, 'couldNotSend');
                    this.sendingDeferred.reject(['phone.codeinvalid']);
                    expect(this.block.couldNotSend.calledOnce).to.be(true);
                    this.block.couldNotSend.restore();
                });

                it('should trigger this.phoneCompromised if sending failed with error "phone.compromised"', function() {
                    sinon.stub(this.block, 'phoneCompromised');
                    this.sendingDeferred.reject(['phone.compromised']);
                    expect(this.block.phoneCompromised.calledOnce).to.be(true);
                    this.block.phoneCompromised.restore();
                });

                it('should call startSendingFeedback before sending the code', function() {
                    expect(this.block.startSendingFeedback.calledOnce).to.be(true);
                    expect(this.block.startSendingFeedback.calledBefore(this.model.sendCode)).to.be(true);
                });

                it('should call stopSendingFeedback after the code was sent', function() {
                    expect(this.block.stopSendingFeedback.called).to.be(false);
                    this.sendingDeferred.resolve();
                    expect(this.block.stopSendingFeedback.calledOnce).to.be(true);
                    expect(this.block.stopSendingFeedback.calledWithExactly()).to.be(true);
                });

                it(
                    'should call stopSendingFeedback with true as arg if the code was ' + 'not sent successfully',
                    function() {
                        expect(this.block.stopSendingFeedback.called).to.be(false);
                        this.sendingDeferred.reject(['some.error']);
                        expect(this.block.stopSendingFeedback.calledOnce).to.be(true);
                        expect(this.block.stopSendingFeedback.calledWithExactly(true)).to.be(true);
                    }
                );
            });

            describe('when the code was sent for te model', function() {
                beforeEach(function() {
                    sinon.stub(this.model, 'isCodeSent').returns(true);
                });

                it('should keep the old model', function() {
                    this.block.phoneEntered(this.unsanitized);
                    expect(this.block.currentPhone).to.be(this.model);
                });

                it('should not send the code', function() {
                    this.block.phoneEntered(this.unsanitized);
                    expect(this.model.sendCode.called).to.be(false);
                });

                it('should trigger this.show with "code" if the model is not confirmed', function() {
                    sinon.stub(this.model, 'isConfirmed').returns(false);
                    this.block.phoneEntered(this.unsanitized);
                    expect(this.block.show.calledWithExactly('code')).to.be(true);
                });

                it('should trigger this.show with "acknowledgement" if the model is confirmed', function() {
                    sinon.stub(this.model, 'isConfirmed').returns(true);
                    this.block.phoneEntered(this.unsanitized);
                    expect(this.block.show.calledWithExactly('acknowledgement')).to.be(true);
                });
            });
        });

        describe('show', function() {
            beforeEach(function() {
                var block = this.block;

                subblocks.forEach(function(blockname) {
                    var subblock = block.subBlocks[blockname];

                    sinon.stub(subblock, 'show');
                    sinon.stub(subblock, 'hide');
                });

                this.stage = 'acknowledgement';

                sinon.stub(block, 'validate');
                sinon.stub(block, 'error');
            });
            afterEach(function() {
                var block = this.block;

                subblocks.forEach(function(blockname) {
                    var subblock = block.subBlocks[blockname];

                    subblock.show.restore();
                    subblock.hide.restore();
                });

                block.validate.restore();
                block.error.restore();
            });

            subblocks.forEach(function(blockname) {
                it(
                    'should trigger the "show" method of the "' +
                        blockname +
                        '" block when triggered with ' +
                        blockname,
                    function() {
                        this.block.show(blockname);
                        expect(this.block.subBlocks[blockname].show.calledOnce).to.be(true);
                    }
                );
            });

            it('should trigger the "hide" method on all the sub-blocks before any one is shown', function() {
                var block = this.block;

                var blockname = subblocks[0];
                var singleBlock = block.subBlocks[blockname];

                block.show(blockname);

                subblocks.forEach(function(subblock) {
                    subblock = block.subBlocks[subblock];
                    expect(subblock.hide.calledBefore(singleBlock.show)).to.be(true);
                });
            });

            it('should call this.error without arguments to hide any existing errors', function() {
                this.block.show(this.stage);
                expect(this.block.error.calledWithExactly()).to.be(true);
            });

            it('should call this.validate', function() {
                this.block.show(this.stage);
                expect(this.block.validate.calledOnce).to.be(true);
                expect(this.block.validate.calledWithExactly(true)).to.be(true);
            });
        });

        describe('couldNotSend', function() {
            beforeEach(function() {
                sinon.stub(this.block, 'error');
                sinon.stub(this.block, 'setModel');

                this.block.couldNotSend();
            });
            afterEach(function() {
                this.block.error.restore();
                this.block.setModel.restore();
            });

            it('should show an error', function() {
                expect(this.block.error.calledWithExactly('couldnotsend')).to.be(true);
            });
        });
    });

    describe('Phone entry', function() {
        beforeEach(function() {
            this.phoneEntry = this.block.subBlocks.entry;
        });

        describe('initConfirmation', function() {
            it('should validate the block', function() {
                sinon.stub(this.phoneEntry, 'validate').returns(new $.Deferred());
                this.phoneEntry.initConfirmation(this.domEvent);
                expect(this.phoneEntry.validate.calledOnce).to.be(true);
                this.phoneEntry.validate.restore();
            });

            it(
                'should trigger "phoneEntered" with currently entered phone if the ' + 'validation was successful',
                function() {
                    var deferred = new $.Deferred();

                    sinon.stub(this.phoneEntry, 'validate').returns(deferred);
                    sinon.stub(this.phoneEntry, 'emit');

                    sinon.stub(passport.validator, 'check').returns(true);

                    this.phoneEntry.initConfirmation(this.domEvent);

                    expect(this.phoneEntry.emit.called).to.be(false);
                    deferred.resolve();
                    expect(this.phoneEntry.emit.called).to.be(true);

                    passport.validator.check.restore();
                    this.phoneEntry.validate.restore();
                    this.phoneEntry.emit.restore();
                }
            );
        });
    });

    describe('Code entry', function() {
        beforeEach(function() {
            this.codeEntry = this.block.subBlocks.code;
            sinon.stub(this.codeEntry, 'emit');
            sinon.stub(this.codeEntry, 'error');
            sinon.stub(this.codeEntry, 'val').returns(this.confirmationCode);
            sinon.stub(this.codeEntry, 'getModel').returns(this.model);
            sinon.stub(this.codeEntry, 'updateDestinationPhone');
            sinon.stub(this.codeEntry, 'startSendingFeedback');
            sinon.stub(this.codeEntry, 'stopSendingFeedback');

            this.sendingDeferred = new $.Deferred();
            sinon.stub(this.model, 'sendCode').returns(this.sendingDeferred);

            this.confirmationDeferred = new $.Deferred();
            sinon.stub(this.model, 'confirmCode').returns(this.confirmationDeferred);
        });

        afterEach(function() {
            this.codeEntry.emit.restore();
            this.codeEntry.error.restore();
            this.codeEntry.val.restore();
            this.codeEntry.getModel.restore();
            this.codeEntry.updateDestinationPhone.restore();
            this.codeEntry.startSendingFeedback.restore();
            this.codeEntry.stopSendingFeedback.restore();
        });

        describe('back', function() {
            beforeEach(function() {
                this.codeEntry.back(this.domEvent);
            });

            it('should trigger the "restart" event', function() {
                expect(this.codeEntry.emit.calledWithExactly('restart')).to.be(true);
            });
        });

        describe('sendCode', function() {
            it('should throw if the model is not set', function() {
                this.codeEntry.getModel.returns(null);

                var codeEntry = this.codeEntry;

                expect(function() {
                    codeEntry.show();
                }).to.throwException(/Model should be set/);
            });

            it('should call sendCode of the model', function() {
                this.codeEntry.sendCode(this.domEvent);
                expect(this.model.sendCode.calledOnce).to.be(true);
            });

            it('should trigger "couldNotSend" event if sending failed', function() {
                this.codeEntry.sendCode(this.domEvent);
                this.sendingDeferred.reject();
                expect(this.codeEntry.emit.calledWithExactly('couldNotSend')).to.be(true);
            });

            it('should trigger "sendingLimitReached" event if model does not allows sending', function() {
                sinon.stub(this.model, 'getSendingsLeft').returns(0);
                this.codeEntry.sendCode(this.domEvent);
                expect(this.codeEntry.emit.calledWithExactly('sendingLimitReached')).to.be(true);
            });

            it('should call startSendingFeedback before sending the code', function() {
                this.codeEntry.sendCode(this.domEvent);
                expect(this.codeEntry.startSendingFeedback.calledOnce).to.be(true);
                expect(this.codeEntry.startSendingFeedback.calledBefore(this.model.sendCode)).to.be(true);
            });

            it('should call stopSendingFeedback after the code was sent', function() {
                this.codeEntry.sendCode(this.domEvent);
                expect(this.codeEntry.stopSendingFeedback.called).to.be(false);
                this.sendingDeferred.resolve();
                expect(this.codeEntry.stopSendingFeedback.calledOnce).to.be(true);
                expect(this.codeEntry.stopSendingFeedback.calledWithExactly()).to.be(true);
            });

            it('should call stopSendingFeedback with true as arg if the code was not sent successfully', function() {
                this.codeEntry.sendCode(this.domEvent);
                expect(this.codeEntry.stopSendingFeedback.called).to.be(false);
                this.sendingDeferred.reject();
                expect(this.codeEntry.stopSendingFeedback.calledOnce).to.be(true);
                expect(this.codeEntry.stopSendingFeedback.calledWithExactly(true)).to.be(true);
            });
        });

        describe('confirmCode', function() {
            it('should throw if the model is not set', function() {
                this.codeEntry.getModel.returns(null);

                var codeEntry = this.codeEntry;
                var event = this.domEvent;

                expect(function() {
                    codeEntry.confirmCode(event);
                }).to.throwException(/Model should be set/);
            });

            it('should show "missingvalue" error if the value is empty', function() {
                this.codeEntry.val.returns('');
                this.codeEntry.confirmCode(this.domEvent);
                expect(this.codeEntry.error.calledWithExactly('missingvalue')).to.be(true);
            });

            it('should not call the models confirmCode if the code is empty', function() {
                this.codeEntry.val.returns('');
                this.codeEntry.confirmCode(this.domEvent);
                expect(this.model.confirmCode.called).to.be(false);
            });

            it('should call confirmCode of the model', function() {
                this.codeEntry.confirmCode(this.domEvent);
                expect(this.model.confirmCode.calledOnce).to.be(true);
                expect(this.model.confirmCode.calledWith(this.confirmationCode)).to.be(true);
            });

            it('should trigger "phoneConfirmed" event when the model is confirmed successfully', function() {
                this.codeEntry.confirmCode(this.domEvent);
                this.confirmationDeferred.resolve(true);
                expect(this.codeEntry.emit.calledWithExactly('phoneConfirmed')).to.be(true);
            });

            it(
                'should trigger "confirmationsLimitReached" if model does not ' + 'allows any more confirmations',
                function() {
                    sinon.stub(this.model, 'getConfirmationsLeft').returns(0);
                    this.codeEntry.confirmCode(this.domEvent);
                    expect(this.codeEntry.emit.calledWithExactly('confirmationsLimitReached')).to.be(true);
                }
            );

            it('should show "codeinvalid" error if code was not accepted', function() {
                this.codeEntry.confirmCode(this.domEvent);
                this.confirmationDeferred.reject(['code.invalid']);
                expect(this.codeEntry.error.calledWithExactly('codeinvalid')).to.be(true);
            });

            it('should show "generic" error if code confirmation failed', function() {
                this.codeEntry.confirmCode(this.domEvent);
                this.confirmationDeferred.reject();
                expect(this.codeEntry.error.calledWithExactly('generic')).to.be(true);
            });
        });

        describe('show', function() {
            it('should throw if the model is not set', function() {
                this.codeEntry.getModel.returns(null);

                var codeEntry = this.codeEntry;

                expect(function() {
                    codeEntry.show();
                }).to.throwException(/Model should be set/);
            });

            it('should trigger "phoneConfirmed" event if the model is already confirmed', function() {
                sinon.stub(this.model, 'isConfirmed').returns(true);
                this.codeEntry.show();
                expect(this.codeEntry.emit.calledWithExactly('phoneConfirmed')).to.be(true);
            });

            it('should clear the input', function() {
                this.codeEntry.show();
                expect(this.codeEntry.val.calledWithExactly('')).to.be(true);
            });

            it('should focus the input', function() {
                sinon.stub(this.codeEntry, 'focus');

                this.codeEntry.show();
                expect(this.codeEntry.focus.calledOnce).to.be(true);

                this.codeEntry.focus.restore();
            });

            it('should hide errors', function() {
                this.codeEntry.show();
                expect(this.codeEntry.error.calledWithExactly()).to.be(true);
            });

            it('should update the destination phone', function() {
                this.codeEntry.show();
                expect(this.codeEntry.updateDestinationPhone.calledWithExactly(this.model.getSanitized())).to.be(true);
            });
        });
    });

    describe('Acknowledgement', function() {
        beforeEach(function() {
            this.acknowledgement = this.block.subBlocks.acknowledgement;
            this.originalModel = this.acknowledgement.getModel();

            this.acknowledgement.setModel(this.model);
            sinon.stub(this.model, 'getSanitized').returns('');
            sinon.stub(this.model, 'isConfirmed').returns(true);
        });
        afterEach(function() {
            this.acknowledgement.setModel(this.originalModel);
        });

        describe('show', function() {
            it('should call the model for its sanitized code', function() {
                this.acknowledgement.show();
                expect(this.model.getSanitized.calledOnce).to.be(true);
            });

            it('should throw if the model is not set', function() {
                var acknowledgement = this.acknowledgement;

                sinon.stub(acknowledgement, 'getModel').returns(null);
                expect(function() {
                    acknowledgement.show();
                }).to.throwException(/Model should be set/);

                acknowledgement.getModel.restore();
            });

            it('should throw if the model is not confirmed', function() {
                this.model.isConfirmed.returns(false);

                var acknowledgement = this.acknowledgement;

                expect(function() {
                    acknowledgement.show();
                }).to.throwException(/Model should be confirmed/);
            });

            it("should render the view with the model's number", function() {
                sinon.stub(this.acknowledgement, 'setNumber');

                this.acknowledgement.show();
                expect(this.acknowledgement.setNumber.calledWithExactly(this.model.getSanitized())).to.be(true);

                this.acknowledgement.setNumber.restore();
            });
        });
    });
});
