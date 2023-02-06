/* global describe, beforeEach, afterEach, sinon, expect, it */
var error = ['some error'];

describe('YaSMS', function() {
    beforeEach(function() {
        this.block = passport.block('yasms');
        this.block.captcha = passport.block('captcha');
    });

    describe('init', function() {
        describe('should call', function() {
            ['setDefaultState', 'bindControls', 'checkSwitchFieldType'].forEach(function(method) {
                it(method, function() {
                    sinon.stub(this.block, method);
                    this.block.init();

                    expect(this.block[method].called).to.be(true);
                    this.block[method].restore();
                });
            });
        });

        it('should set "canSwitchInputType" flag as "true"', function() {
            this.block.init();
            expect(this.block.canSwitchInputType).to.be(true);
        });
    });

    describe('', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'switchState');
        });

        afterEach(function() {
            this.block.switchState.restore();
        });

        it('showReplaceState should call "switchState" method with argument "replace"', function() {
            this.block.showReplaceState();
            expect(this.block.switchState.calledWith('replace')).to.be(true);
        });

        it('showRemoveState should call "switchState" method with argument "remove"', function() {
            this.block.showRemoveState();
            expect(this.block.switchState.calledWith('remove')).to.be(true);
        });
    });

    generalTests.call(this);

    describe('operationAlias', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'switchState');
            sinon.stub(this.block, 'processError');

            sinon.stub(this.block, 'getSecure').returns({
                id: 0
            });

            sinon.stub(this.block, 'getControl').returns({
                $node: document.createElement('span'),
                disable: function() {},
                enable: function() {},
                toggle: function() {},
                uncheck: function() {},
                check: function() {},
                isChecked: function() {
                    return true;
                }
            });

            sinon.stub(passport.api, 'request').returns(
                new $.Deferred().resolve({
                    status: 'ok',
                    operation: {}
                })
            );
        });

        afterEach(function() {
            this.block.getSecure.restore();
            this.block.switchState.restore();
            this.block.getControl.restore();
            this.block.processError.restore();
            passport.api.request.restore();
        });

        it('should set operation type "aliasify" if toggler is checked', function() {
            this.block.operationAlias();
            expect(this.block.operation.type).to.eql('aliasify');
        });

        it('should set operation type "dealiasify" if toggler is not checked', function() {
            this.block.getControl.restore();
            sinon.stub(this.block, 'getControl').returns({
                $node: document.createElement('span'),
                disable: function() {},
                isChecked: function() {
                    return false;
                }
            });

            this.block.operationAlias();
            expect(this.block.operation.type).to.eql('dealiasify');
        });

        it('should call "switchState" method with argument "confirm"', function() {
            this.block.operationAlias();
            expect(this.block.switchState.calledWith('confirm')).to.be(true);
        });

        it('should call "error" method with errors array if API response with error', function() {
            passport.api.request.restore();

            sinon.stub(passport.api, 'request').returns(
                new $.Deferred().resolve({
                    status: 'error',
                    errors: error
                })
            );

            this.block.operationAlias();
            expect(this.block.processError.calledWith(error)).to.be(true);
        });
    });

    describe('operationRemove', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'toggleSpinner');
            sinon.stub(this.block, 'processError');
            sinon.stub(this.block, 'getControl').returns({
                isChecked: function() {
                    return true;
                }
            });

            sinon.stub(passport.api, 'request').returns(
                new $.Deferred().resolve({
                    status: 'error',
                    errors: error
                })
            );
        });

        afterEach(function() {
            this.block.toggleSpinner.restore();
            this.block.processError.restore();
            this.block.getControl.restore();
            passport.api.request.restore();
        });

        it('should set "remove" operation type', function() {
            this.block.operationRemove();
            expect(this.block.operation.type).to.eql('remove');
        });

        it('should call "toggleSpinner" method', function() {
            this.block.operationRemove();
            expect(this.block.toggleSpinner.called).to.be(true);
        });

        it('should call "error" method with errors array if API response with error', function() {
            this.block.operationRemove();
            expect(this.block.processError.calledWith(error)).to.be(true);
        });
    });
});

describe('YaSMS simple phones', function() {
    beforeEach(function() {
        this.block = passport.block('yasms-simple');
    });

    describe('init', function() {
        describe('should call', function() {
            ['setDefaultState', 'bindControls'].forEach(function(method) {
                it(method, function() {
                    sinon.stub(this.block, method);
                    this.block.init();

                    expect(this.block[method].called).to.be(true);
                    this.block[method].restore();
                });
            });
        });
    });

    describe('repaintBlock', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'switchState');
            sinon.stub(this.block, 'repaintPhonesList');
        });

        afterEach(function() {
            this.block.switchState.restore();
            this.block.repaintPhonesList.restore();
        });

        it('should call "switchState" method with arguments "null, true"', function() {
            this.block.repaintBlock();
            expect(this.block.switchState.calledWith(null, true)).to.be(true);
        });

        it('should call "repaintPhonesList" method', function() {
            this.block.repaintBlock();
            expect(this.block.repaintPhonesList.called).to.be(true);
        });
    });

    it('showBindState should call "switchState" method with argument "bind"', function() {
        sinon.stub(this.block, 'switchState');
        this.block.showBindState();

        expect(this.block.switchState.calledWith('bind')).to.be(true);
        this.block.switchState.restore();
    });

    describe('operationProceed', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'operationClone');
            sinon.stub(this.block, 'switchState');
        });

        afterEach(function() {
            this.block.operationClone.restore();
            this.block.switchState.restore();
        });

        it('should call "operationClone" method with event', function() {
            this.block.operationProceed();
            expect(this.block.operationClone.calledWith(event)).to.be(true);
        });

        it('should call "switchState" method with argument "confirm, null, true"', function() {
            this.block.operationProceed();
            expect(this.block.switchState.calledWith('confirm', null, true)).to.be(true);
        });
    });

    describe('operationCancelFromList', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'operationClone');
            sinon.stub(this.block, 'operationCancel');
            this.block.operationCancelFromList();
        });

        afterEach(function() {
            this.block.operationClone.restore();
            this.block.operationCancel.restore();
        });

        ['operationClone', 'operationCancel'].forEach(function(method) {
            it('should call "' + method + '" method with event', function() {
                expect(this.block[method].calledWith(event)).to.be(true);
            });
        });
    });

    describe('operationSecurify', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'toggleSpinner');
            sinon.stub(this.block, 'getParamFromEvent').returns(1);
        });

        afterEach(function() {
            this.block.toggleSpinner.restore();
            this.block.getParamFromEvent.restore();
        });

        describe('success API call', function() {
            beforeEach(function() {
                sinon.stub(passport.api, 'request').returns(
                    new $.Deferred().resolve({
                        status: 'ok',
                        operation: {}
                    })
                );
                sinon.stub(this.block, 'disableControls');
                sinon.stub(this.block, 'switchState');
            });

            afterEach(function() {
                passport.api.request.restore();
                this.block.disableControls.restore();
                this.block.switchState.restore();
            });

            it('shoud set "securify" operation type', function() {
                this.block.operationSecurify();
                expect(this.block.operation.type).to.eql('securify');
            });

            it('shoud call "toggleSpinner" method with argument "null"', function() {
                this.block.operationSecurify();
                expect(this.block.toggleSpinner.calledWith(null)).to.be(true);
            });

            it('shoud call "disableControls"', function() {
                this.block.operationSecurify();
                expect(this.block.disableControls.called).to.be(true);
            });

            it('shoud call "toggleSpinner" method with argument "true"', function() {
                this.block.operationSecurify();
                expect(this.block.toggleSpinner.calledWith(true)).to.be(true);
            });

            it('shoud call "switchState" method with argument "securify"', function() {
                this.block.operationSecurify();
                expect(this.block.switchState.calledWith('securify')).to.be(true);
            });
        });

        describe('failed API call', function() {
            var apiResponse = {
                status: 'error',
                errors: error
            };

            beforeEach(function() {
                sinon.stub(passport.api, 'request').returns(new $.Deferred().resolve(apiResponse));
                sinon.stub(this.block, 'processError');
                sinon.stub(this.block.parent, 'showReplaceState');
                sinon.stub(this.block.parent, 'setReplacedPhone');
            });

            afterEach(function() {
                this.block.processError.restore();
                this.block.parent.showReplaceState.restore();
                this.block.parent.setReplacedPhone.restore();
                passport.api.request.restore();
            });

            it('shoud set "securify" operation type', function() {
                this.block.operationSecurify();
                expect(this.block.operation.type).to.eql('securify');
            });

            it('shoud call "toggleSpinner" method with argument "null"', function() {
                this.block.operationSecurify();
                expect(this.block.toggleSpinner.calledWith(null)).to.be(true);
            });

            it('shoud call "error" with errors array', function() {
                this.block.operationSecurify();
                expect(this.block.processError.calledWith(apiResponse.errors)).to.be(true);
            });

            describe('if errors exists "phone_secure.already_exists" error', function() {
                beforeEach(function() {
                    passport.api.request.restore();
                    apiResponse.errors = ['phone_secure.already_exists'];
                    sinon.stub(passport.api, 'request').returns(new $.Deferred().resolve(apiResponse));
                    this.block.operationSecurify();
                });

                afterEach(function() {});

                it('shoud call "parent.showReplaceState"', function() {
                    expect(this.block.parent.showReplaceState.called).to.be(true);
                });

                it(
                    'shoud call "parent.setReplacedPhone" with id witch returns by ' + '"getParamFromEvent" method',
                    function() {
                        expect(this.block.parent.setReplacedPhone.calledWith(this.block.getParamFromEvent())).to.be(
                            true
                        );
                    }
                );
            });
        });
    });

    describe('operationRemove', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'toggleSpinner');
            sinon.stub(this.block, 'getParamFromEvent').returns(1);
        });

        afterEach(function() {
            this.block.toggleSpinner.restore();
            this.block.getParamFromEvent.restore();
        });

        describe('success API call', function() {
            beforeEach(function() {
                sinon.stub(passport.api, 'request').returns(
                    new $.Deferred().resolve({
                        status: 'ok',
                        phone: {}
                    })
                );
                sinon.stub(this.block, 'getState').returns(new $.Deferred().resolve());
                sinon.stub(this.block, 'successOperationNotify');
                sinon.stub(this.block, 'repaintBlocks');
            });

            afterEach(function() {
                passport.api.request.restore();
                this.block.getState.restore();
                this.block.successOperationNotify.restore();
                this.block.repaintBlocks.restore();
            });

            it('shoud set "remove" operation type', function() {
                this.block.operationRemove();
                expect(this.block.operation.type).to.eql('remove');
            });

            it('shoud call "toggleSpinner" method with argument "null"', function() {
                this.block.operationRemove();
                expect(this.block.toggleSpinner.calledWith(null)).to.be(true);
            });

            it('shoud call "getState"', function() {
                this.block.operationRemove();
                expect(this.block.getState.called).to.be(true);
            });
        });

        describe('failed API call', function() {
            var apiResponse = {
                status: 'error',
                errors: error
            };

            beforeEach(function() {
                sinon.stub(passport.api, 'request').returns(new $.Deferred().resolve(apiResponse));
                sinon.stub(this.block, 'processError');

                this.block.operationRemove();
            });

            afterEach(function() {
                passport.api.request.restore();
                this.block.processError.restore();
            });

            it('shoud set "remove" operation type', function() {
                this.block.operationRemove();
                expect(this.block.operation.type).to.eql('remove');
            });

            it('shoud call "toggleSpinner" method with argument "null"', function() {
                this.block.operationRemove();
                expect(this.block.toggleSpinner.calledWith(null)).to.be(true);
            });

            it('shoud call "error" with errors array', function() {
                this.block.operationRemove();
                expect(this.block.processError.calledWith(apiResponse.errors)).to.be(true);
            });

            it('shoud call "toggleSpinner" method with argument "true"', function() {
                this.block.operationRemove();
                expect(this.block.toggleSpinner.calledWith(true)).to.be(true);
            });
        });
    });

    generalTests.call(this);
});

function generalTests() {
    it('setDefaultState should call "clearOperationParams"', function() {
        sinon.stub(this.block, 'clearOperationParams');
        this.block.setDefaultState();
        expect(this.block.clearOperationParams.called).to.be(true);
        this.block.clearOperationParams.restore();
    });

    it('clearOperationParams should set default operation state', function() {
        var operationDefaultState = this.block.operation;

        this.block.operation = {
            blah: 'blah',
            id: 213123,
            type: 'sometype'
        };

        this.block.clearOperationParams();
        expect(this.block.operation).to.eql(operationDefaultState);
    });

    it('bindControls should call clearControls', function() {
        sinon.stub(this.block, 'clearControls');
        this.block.bindControls();

        expect(this.block.clearControls.called).to.be(true);
        this.block.clearControls.restore();
    });

    it('clearControls should clear block "fields" property', function() {
        this.block.fields = {
            someblock: 'block',
            someblock2: 'block2'
        };

        this.block.clearControls();
        expect(this.block.fields).to.eql({});
    });

    describe('error', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'goToAuth');
            sinon.stub(this.block, 'enableCaptcha');
        });

        afterEach(function() {
            this.block.goToAuth.restore();
            this.block.enableCaptcha.restore();
        });

        it('should send user to "/auth" if error consist in "authErrors"', function() {
            this.block.processError('sessionid.invalid');
            expect(this.block.goToAuth.called).to.be(true);
        });

        it('should not send user to "/auth" if error is not consist in "authErrors"', function() {
            this.block.processError('captcha.required');
            expect(this.block.goToAuth.called).to.be(false);
        });

        it('should call "enableCaptcha" method if error is "captcha.required"', function() {
            this.block.processError('captcha.required');
            expect(this.block.enableCaptcha.called).to.be(true);
        });

        it('should not call "enableCaptcha" method if error is not "captcha.required"', function() {
            this.block.processError('sessionid.invalid');
            expect(this.block.enableCaptcha.called).to.be(false);
        });
    });

    describe('switchState', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'bindControls');
            sinon.stub(this.block, 'disableControls');
            sinon.stub(this.block, 'startResendTimer');
        });

        afterEach(function() {
            this.block.bindControls.restore();
            this.block.disableControls.restore();
            this.block.startResendTimer.restore();
        });

        it('should not call "bindControls" if it called with argument "silent"', function() {
            this.block.switchState('confirm', true);
            expect(this.block.bindControls.called).to.be(false);
        });

        it('should call "bindControls" if it called without argument "silent"', function() {
            this.block.switchState('confirm');
            expect(this.block.bindControls.called).to.be(true);
        });

        it('should call "disableControls" if it called with argument "state"', function() {
            this.block.switchState('confirm');
            expect(this.block.disableControls.called).to.be(true);
        });

        it('should not call "disableControls" if it called without argument "state"', function() {
            this.block.switchState();
            expect(this.block.disableControls.called).to.be(false);
        });

        it(
            'should call "startResendTimer" if it called without argument "clearTimer" and ' +
                "state consist in ['confirm', 'confirm-simple', 'securify']",
            function() {
                this.block.switchState('confirm', false, false);
                expect(this.block.startResendTimer.called).to.be(true);
            }
        );

        it(
            'should not call "startResendTimer" if it called with argument "clearTimer" and ' +
                "state consist in ['confirm', 'confirm-simple', 'securify']",
            function() {
                this.block.switchState('confirm', false, true);
                expect(this.block.startResendTimer.called).to.be(false);
            }
        );

        it(
            'should call not "startResendTimer" if it called without argument "clearTimer" and ' +
                "state, witch is not consist in ['confirm', 'confirm-simple', 'securify']",
            function() {
                this.block.switchState('blah', false, false);
                expect(this.block.startResendTimer.called).to.be(false);
            }
        );
    });

    describe('repaintBlock', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'setDefaultState');
            sinon.stub(this.block, 'bindControls');
        });

        afterEach(function() {
            this.block.setDefaultState.restore();
            this.block.bindControls.restore();
        });

        it('should call "setDefaultState" method', function() {
            this.block.repaintBlock();
            expect(this.block.setDefaultState.called).to.be(true);
        });

        it('should call "bindControls" method', function() {
            this.block.repaintBlock();
            expect(this.block.bindControls.called).to.be(true);
        });
    });

    describe('repaintBlocks', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'toggleYasmsSimpleVisible');
            sinon.stub(this.block, 'repaintBlock');
        });

        afterEach(function() {
            this.block.toggleYasmsSimpleVisible.restore();
            this.block.repaintBlock.restore();
        });

        it('repaintBlocks should call "toggleYasmsSimpleVisible" method', function() {
            this.block.repaintBlocks();
            expect(this.block.toggleYasmsSimpleVisible.called).to.be(true);
        });

        it('repaintBlocks should call "repaintBlock" method', function() {
            this.block.repaintBlocks();
            expect(this.block.repaintBlock.called).to.be(true);
        });
    });

    describe('updateLocals', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'clearLocals');
        });

        afterEach(function() {
            this.block.clearLocals.restore();
        });

        it('should call "clearLocals" method', function() {
            this.block.updateLocals({phones: []});
            expect(this.block.clearLocals.called).to.be(true);
        });

        it('should not call "clearLocals" method calls without argument', function() {
            this.block.updateLocals();
            expect(this.block.clearLocals.called).to.be(false);
        });
    });

    it('enableCaptcha shoud call capthca block "enableCaptcha" method', function() {
        sinon.stub(this.block.captcha, 'enableCaptcha');
        this.block.enableCaptcha();

        expect(this.block.captcha.enableCaptcha.called).to.be(true);
        this.block.captcha.enableCaptcha.restore();
    });

    it('proceedCaptcha shoud call capthca block "closeCaptcha" method', function() {
        sinon.stub(this.block.captcha, 'closeCaptcha');
        sinon.stub(window.YsaLogger, 'submitEvent');
        this.block.proceedCaptcha();

        expect(this.block.captcha.closeCaptcha.called).to.be(true);
        this.block.captcha.closeCaptcha.restore();
        window.YsaLogger.submitEvent.restore();
    });

    describe('operationCancel', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'repaintBlocks');
            sinon.stub(this.block, 'preventSubmit');
            sinon.stub(this.block, 'toggleSpinner');
            this.block.operation = {
                type: 'bind',
                id: 1
            };
        });

        afterEach(function() {
            this.block.repaintBlocks.restore();
            this.block.preventSubmit.restore();
            this.block.toggleSpinner.restore();
            this.block.operation = {};
        });

        describe('success API call', function() {
            beforeEach(function() {
                sinon.stub(passport.api, 'request').returns(
                    new $.Deferred().resolve({
                        status: 'ok',
                        phone: {}
                    })
                );
                sinon.stub(this.block, 'getState').returns(new $.Deferred().resolve());
                sinon.stub(passport.api, 'log');

                this.block.operationCancel();
            });

            afterEach(function() {
                passport.api.request.restore();
                this.block.getState.restore();
                passport.api.log.restore();
            });

            it('if called with "event" shoul call "preventSubmit" method', function() {
                var event = document.createEvent('MouseEvents');

                this.block.operationCancel(event);
                expect(this.block.preventSubmit.calledWith(event)).to.be(true);
            });

            it('should call "repaintBlocks" method if there are no operation id', function() {
                this.block.operation.id = null;
                this.block.operationCancel();
                expect(this.block.repaintBlocks.called).to.be(true);
            });

            it('should call "toggleSpinner" method', function() {
                this.block.operationCancel();
                expect(this.block.toggleSpinner.called).to.be(true);
            });

            it('should call "passport.api.log"', function() {
                this.block.operationCancel();
                expect(passport.api.log.called).to.be(true);
            });

            it('should call "getState" method', function() {
                this.block.operationCancel();
                expect(this.block.getState.called).to.be(true);
            });

            it('should call "repaintBlocks" method', function() {
                this.block.operationCancel();
                expect(this.block.repaintBlocks.called).to.be(true);
            });
        });

        describe('failed API call', function() {
            beforeEach(function() {
                sinon.stub(passport.api, 'request').returns(
                    new $.Deferred().resolve({
                        status: 'error',
                        errors: error
                    })
                );
                sinon.stub(this.block, 'processError');
            });

            afterEach(function() {
                passport.api.request.restore();
                this.block.processError.restore();
            });

            it('if called with "event" shoul call "preventSubmit" method', function() {
                var event = document.createEvent('MouseEvents');

                this.block.operationCancel(event);
                expect(this.block.preventSubmit.calledWith(event)).to.be(true);
            });

            it('should call "repaintBlocks" method if there are no operation id', function() {
                this.block.operation.id = null;
                this.block.operationCancel();
                expect(this.block.repaintBlocks.called).to.be(true);
            });

            it('should call "toggleSpinner" method', function() {
                this.block.operationCancel();
                expect(this.block.toggleSpinner.called).to.be(true);
            });

            it('should call "error" method with errors array', function() {
                this.block.operationCancel();
                expect(this.block.processError.calledWith(error)).to.be(true);
            });

            it('should call "toggleSpinner" method with argument "true"', function() {
                this.block.operationCancel();
                expect(this.block.toggleSpinner.calledWith(true)).to.be(true);
            });
        });
    });

    describe('resendCode', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'toggleSpinner');
            sinon.stub(this.block, 'startResendTimer');
            sinon.stub(this.block, 'processError');
            sinon.stub(this.block, 'getControl').returns({
                reset: function() {}
            });
        });

        afterEach(function() {
            this.block.toggleSpinner.restore();
            this.block.startResendTimer.restore();
            this.block.processError.restore();
            this.block.getControl.restore();
        });

        it('should call "toggleSpinner" method', function() {
            sinon.stub(passport.api, 'request').returns(
                new $.Deferred().resolve({
                    status: 'ok',
                    phone: {}
                })
            );
            this.block.resendCode();
            expect(this.block.toggleSpinner.called).to.be(true);
            passport.api.request.restore();
        });

        it('should call "startResendTimer" method if API response without errors', function() {
            sinon.stub(passport.api, 'request').returns(
                new $.Deferred().resolve({
                    status: 'ok',
                    phone: {}
                })
            );
            this.block.resendCode();

            expect(this.block.startResendTimer.called).to.be(true);
            passport.api.request.restore();
        });

        it('should call "error" method with errors array', function() {
            sinon.stub(passport.api, 'request').returns(
                new $.Deferred().resolve({
                    status: 'error',
                    errors: error
                })
            );

            this.block.resendCode();
            expect(this.block.processError.calledWith(error)).to.be(true);
            passport.api.request.restore();
        });
    });

    describe('operationCommit', function() {
        describe('success API call', function() {
            beforeEach(function() {
                sinon.stub(this.block, 'updateState').returns(new $.Deferred());
                sinon.stub(passport.api, 'log');
                sinon.stub(passport.api, 'getTrackId');
                sinon.stub(passport.api, 'request').returns(
                    new $.Deferred().resolve({
                        status: 'ok',
                        phone: {}
                    })
                );
            });

            afterEach(function() {
                this.block.updateState.restore();
                passport.api.log.restore();
                passport.api.getTrackId.restore();
                passport.api.request.restore();
            });

            it('should call "passport.api.log"', function() {
                this.block.operationCommit();
                expect(passport.api.log.called).to.be(true);
            });

            it('should call "passport.api.getTrackId" with "trackType" property value', function() {
                this.block.operationCommit();
                expect(passport.api.getTrackId.firstCall.args[0] === this.block.trackType).to.be(true);
            });

            it('should call "updateState" method', function() {
                this.block.operationCommit();
                expect(this.block.updateState.called).to.be(true);
            });
        });
    });

    describe('updateState', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'successOperationNotify');
            sinon.stub(this.block, 'repaintBlocks');
            sinon.stub(this.block, 'processError');
        });

        afterEach(function() {
            this.block.successOperationNotify.restore();
            this.block.repaintBlocks.restore();
            this.block.processError.restore();
        });

        it(
            'should call "successOperationNotify" method if "getState" has successful response and operation ' +
                "type isn't undefined",
            function() {
                sinon.stub(this.block, 'getState').returns(new $.Deferred().resolve());
                this.block.operation.type = 'replace';

                this.block.updateState();
                expect(this.block.successOperationNotify.called).to.be(true);

                this.block.operation.type = undefined;
                this.block.getState.restore();
            }
        );

        it(
            'shouldn\'t call "successOperationNotify" method if "getState" has successful response and operation ' +
                'type is undefined',
            function() {
                sinon.stub(this.block, 'getState').returns(new $.Deferred().resolve());

                this.block.updateState();
                expect(this.block.successOperationNotify.called).to.be(false);

                this.block.getState.restore();
            }
        );

        it('should call "repaintBlocks" method if "getState" has successful response', function() {
            sinon.stub(this.block, 'getState').returns(new $.Deferred().resolve());

            this.block.updateState();
            expect(this.block.repaintBlocks.called).to.be(true);

            this.block.getState.restore();
        });

        it('should call "error" method with argument "internal" if "getState" has failed response', function() {
            sinon.stub(this.block, 'getState').returns(new $.Deferred().reject());

            this.block.updateState();
            expect(this.block.processError.calledWith('internal')).to.be(true);

            this.block.getState.restore();
        });
    });

    it('getState should call "updateLocals" method', function() {
        var account = {
            phones: [{id: 1, blah: 'blah'}]
        };

        sinon.stub(this.block, 'updateLocals');
        sinon.stub(passport.api, 'request').returns(
            new $.Deferred().resolve({
                status: 'ok',
                account: account
            })
        );

        this.block.getState();
        expect(this.block.updateLocals.calledWith(account)).to.be(true);

        this.block.updateLocals.restore();
        passport.api.request.restore();
    });

    it('operationBind should call "error" method with argument "number.empty" if there are no field value', function() {
        sinon.stub(this.block, 'processError');
        sinon.stub(this.block, 'getControl').returns({
            getValue: function() {
                return '';
            }
        });

        this.block.operationBind();
        expect(this.block.processError.calledWith('number.empty')).to.be(true);

        this.block.processError.restore();
        this.block.getControl.restore();
    });

    describe('operationBind', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'toggleSpinner');
            sinon.stub(this.block, 'switchState');
            sinon.stub(this.block, 'getControl').returns({
                getValue: function() {
                    return 'value';
                },
                isChecked: function() {
                    return true;
                },
                hideError: function() {}
            });
        });

        afterEach(function() {
            this.block.toggleSpinner.restore();
            this.block.switchState.restore();
            this.block.getControl.restore();
        });

        describe('success API call', function() {
            beforeEach(function() {
                sinon.stub(passport.api, 'request').returns(
                    new $.Deferred().resolve({
                        status: 'ok',
                        operation: {}
                    })
                );

                this.block.operationBind();
            });

            afterEach(function() {
                passport.api.request.restore();
            });

            it('should set "bind" operation type', function() {
                this.block.operationBind();
                expect(this.block.operation.type).to.eql('bind');
            });

            it('should call "toggleSpinner" method', function() {
                this.block.operationBind();
                expect(this.block.toggleSpinner.called).to.be(true);
            });

            it('should call "switchState" method with argument "confirm"', function() {
                this.block.operationBind();
                expect(this.block.switchState.calledWith('confirm')).to.be(true);
            });
        });

        describe('failed API call', function() {
            beforeEach(function() {
                sinon.stub(this.block, 'processError');
                sinon.stub(passport.api, 'request').returns(
                    new $.Deferred().resolve({
                        status: 'error',
                        errors: error
                    })
                );
            });

            afterEach(function() {
                this.block.processError.restore();
                passport.api.request.restore();
            });

            it('should set "bind" operation type', function() {
                this.block.operationBind();
                expect(this.block.operation.type).to.eql('bind');
            });

            it('should call "toggleSpinner" method', function() {
                this.block.operationBind();
                expect(this.block.toggleSpinner.called).to.be(true);
            });

            it('should call "error" method with errors array', function() {
                this.block.operationBind();
                expect(this.block.processError.calledWith(error)).to.be(true);
            });

            it('should call "toggleSpinner" method with argument "true"', function() {
                this.block.operationBind();
                expect(this.block.toggleSpinner.calledWith(true)).to.be(true);
            });
        });
    });
}
