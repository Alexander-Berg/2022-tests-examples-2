describe('Social-profiles', function() {
    beforeEach(function() {
        this.block = passport.block('social-profiles');
    });

    it("init should call 'setupBroker' method", function() {
        sinon.stub(this.block, 'setupBroker');
        this.block.init();
        expect(this.block.setupBroker.calledOnce).to.be(true);
        this.block.setupBroker.restore();
    });

    describe('socialAuthResponseHendle', function() {
        it("should call 'brokerOnSuccess' method if status 'ok'", function() {
            sinon.stub(this.block, 'brokerOnSuccess');

            this.block.socialAuthResponseHendle({
                data: {
                    status: 'ok',
                    socialAuth: true
                },
                // eslint-disable-next-line compat/compat
                origin: location.origin
            });

            expect(this.block.brokerOnSuccess.called).to.be(true);

            this.block.brokerOnSuccess.restore();
        });

        it("should call 'brokerOnFailure' method if status isn't 'ok'", function() {
            sinon.stub(this.block, 'brokerOnFailure');

            this.block.socialAuthResponseHendle({
                data: {
                    status: 'error',
                    socialAuth: true
                },
                // eslint-disable-next-line compat/compat
                origin: location.origin
            });

            expect(this.block.brokerOnFailure.called).to.be(true);

            this.block.brokerOnFailure.restore();
        });
    });

    it("brokerOnSuccess should call 'getDataByTask' method with arg task_id if it was", function() {
        sinon.stub(this.block, 'getDataByTask');

        var taskId = '2109384756';

        this.block.brokerOnSuccess({
            task_id: taskId
        });

        expect(this.block.getDataByTask.calledWith(taskId)).to.be(true);

        this.block.getDataByTask.restore();
    });
});
