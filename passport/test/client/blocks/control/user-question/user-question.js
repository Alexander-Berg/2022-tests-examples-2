describe('User-question', function() {
    beforeEach(function() {
        this.block = passport.block('user-question');
    });

    describe('init', function() {
        it('should set selected question for the control based on the question block value', function() {
            var val = '5';
            var questionBlock = passport.block('question');

            sinon.stub(questionBlock, 'val').returns(val);

            this.block.init();
            expect(questionBlock.val.calledOnce).to.be(true);
            expect(this.block.selectedQuestion).to.be(val);

            questionBlock.val.restore();
        });

        it('should call toggleState', function() {
            var val = 'asdfasdfsdf';

            sinon.stub(passport.block('question'), 'val').returns(val);

            sinon.stub(this.block, 'isUserQuestion').returns(true);
            sinon.stub(this.block, 'toggleState');

            this.block.init();
            expect(this.block.isUserQuestion.calledWithExactly(val)).to.be(true);
            expect(this.block.toggleState.calledWithExactly(true)).to.be(true);

            this.block.toggleState.restore();
            this.block.isUserQuestion.restore();
            passport.block('question').val.restore();
        });
    });

    describe('onquestion', function() {
        beforeEach(function() {
            sinon.stub(this.block, 'validate');
            sinon.stub(this.block, 'isEmpty');
            sinon.stub(this.block, 'error');

            this.block.init();
        });
        afterEach(function() {
            this.block.validate.restore();
            this.block.isEmpty.restore();
            this.block.error.restore();
        });

        describe('when changed to user question', function() {
            beforeEach(function() {
                this.change = ['99', '1']; //To 99 (aka user-question) from 1
            });

            it('should call validate with suppressError if the block is empty', function() {
                this.block.isEmpty.returns(true);
                this.block.onquestion(null, this.change);
                expect(this.block.validate.calledWithExactly(true)).to.be(true);
            });

            it('should call validate without suppressingError if the block is not empty', function() {
                this.block.isEmpty.returns(false);
                this.block.onquestion(null, this.change);
                expect(this.block.validate.calledWithExactly(false)).to.be(true);
            });

            it('should call error without arguments to clean up before validation', function() {
                this.block.onquestion(null, this.change);
                expect(this.block.error.calledWithExactly()).to.be(true);
                expect(this.block.error.calledBefore(this.block.validate)).to.be(true);
            });
        });

        describe('when changed from user question to anything else', function() {
            beforeEach(function() {
                this.block.onquestion(null, ['99', '1']); //Changing to user-question first
                this.change = ['1', '99']; //From 99 (aka user-question) to a predefined question 1
            });

            it('should call validate with suppressError if the block is empty', function() {
                this.block.isEmpty.returns(true);
                this.block.onquestion(null, this.change);
                expect(this.block.validate.calledWithExactly(true)).to.be(true);
            });

            it('should call validate with suppressError if the block is not empty', function() {
                this.block.isEmpty.returns(false);
                this.block.onquestion(null, this.change);
                expect(this.block.validate.calledWithExactly(true)).to.be(true);
            });

            it('should call error without arguments to clean up before validation', function() {
                this.block.onquestion(null, this.change);
                expect(this.block.error.calledWithExactly()).to.be(true);
                expect(this.block.error.calledBefore(this.block.validate)).to.be(true);
            });
        });

        describe('when changed to anything, that is not a user-question', function() {
            beforeEach(function() {
                this.change = ['1', '2'];
            });

            it('should not call validate', function() {
                this.block.onquestion(null, this.change);
                expect(this.block.validate.called).to.be(false);
            });
        });
    });
});
