describe('Control', function() {
    beforeEach(function() {
        this.control = passport.block('control');
        this.sinon = sinon.sandbox.create();

        this.$ = $('');
        this.sinon.stub(this.control, '$').returns(this.$);
    });

    afterEach(function() {
        this.sinon.restore();
    });

    describe('Error handling', function() {
        describe('hideErrors', function() {
            it('should set class .g-hidden on all the errors with class .p-control__error', function() {
                this.sinon.stub(this.$, 'addClass').returns(this.$);
                this.control.hideErrors();

                expect(this.control.$.calledWithExactly('.p-control__error')).to.be(true);
                expect(this.$.addClass.calledWithExactly('g-hidden')).to.be(true);
            });
        });

        describe('showError', function() {
            it('should throw if argument is not passed', function() {
                var control = this.control;

                expect(function() {
                    control.showError();
                }).to.throwError(function(err) {
                    expect(err.message).to.be('Error code should be a string');
                });
            });

            it('should throw if argument is not a string', function() {
                var control = this.control;

                expect(function() {
                    control.showError({});
                }).to.throwError(function(err) {
                    expect(err.message).to.be('Error code should be a string');
                });
            });

            it('should remove class .g-hidden from the error defined by control.id and error code', function() {
                this.sinon.stub(this.$, 'removeClass').returns(this.$);

                var errCode = 'cannotWorshipSatan';

                this.control.showError(errCode);

                expect(this.control.$.calledWithExactly('.p-control__error__' + this.control.id + '_' + errCode)).to.be(
                    true
                );
                expect(this.$.removeClass.calledWithExactly('g-hidden')).to.be(true);
            });
        });

        describe('error', function() {
            beforeEach(function() {
                this.sinon.stub(this.control, 'hideErrors');
                this.sinon.stub(this.control, 'showError');
            });

            it('should hide all errors and not call showError if no error code was passed', function() {
                this.control.error();
                expect(this.control.hideErrors.calledOnce).to.be(true);
                expect(this.control.showError.called).to.be(false);
            });

            it('should show a single error if a string is passed', function() {
                var errCode = 'cannot install democracy, conflicts with putin';

                this.control.error(errCode);

                expect(this.control.showError.calledOnce).to.be(true);
                expect(this.control.showError.calledWithExactly(errCode)).to.be(true);
            });

            it('should show all the errors from an array of error codes', function() {
                var codes = ['engine stopped', 'earth too close', 'kaboom'];

                this.control.error(codes);
                expect(this.control.showError.callCount).to.be(codes.length);

                var control = this.control;

                codes.forEach(function(code) {
                    expect(control.showError.calledWithExactly(code)).to.be(true);
                });
            });

            it('should call showError after calling hideErrors', function() {
                this.control.error('someError');
                expect(this.control.showError.calledAfter(this.control.hideErrors)).to.be(true);
            });
        });
    });
});
